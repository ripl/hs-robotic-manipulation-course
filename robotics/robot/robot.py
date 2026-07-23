import time
import numpy as np
from typing import Union
from enum import Enum, auto
from robot.dynamixel import Dynamixel, OperatingMode, ReadAttribute
from dynamixel_sdk import GroupSyncRead, GroupSyncWrite, DXL_LOBYTE, DXL_HIBYTE, DXL_LOWORD, DXL_HIWORD

class MotorControlType(Enum):
    PWM = auto()
    POSITION_CONTROL = auto()
    DISABLED = auto()
    UNKNOWN = auto()

class Robot:
    def __init__(self, 
                 device_name: str, 
                 baudrate: int=1_000_000, 
                 servo_ids: list=[1, 2, 3, 4, 5, 6],
                 velocity_limit: Union[int, list, np.ndarray]=0,
                 max_position_limit: Union[int, list, np.ndarray]=[3072, 2800, 3000, 3500, 4096, 2800],
                 min_position_limit: Union[int, list, np.ndarray]=[1024, 1650, 1100, 600, 0, 2020],
                 position_p_gain: Union[int, list, np.ndarray]=[640, 640, 640, 400, 400, 400],
                 position_i_gain: Union[int, list, np.ndarray]=[10, 10, 10, 10, 10, 10],
                ) -> None:
        self.servo_ids = servo_ids
        self.velocity_limit = self._int_to_list(velocity_limit, len(servo_ids))
        self.max_position_limit = self._int_to_list(max_position_limit, len(servo_ids))
        self.min_position_limit = self._int_to_list(min_position_limit, len(servo_ids))
        self.position_p_gain = self._int_to_list(position_p_gain, len(servo_ids))
        self.position_i_gain = self._int_to_list(position_i_gain, len(servo_ids))
        
        # Initialize motors
        self.dynamixel = Dynamixel.Config(baudrate=baudrate, device_name=device_name).instantiate()
        self._init_motors()

    def _int_to_list(self, val, length):
        if isinstance(val, int):
            return [val] * length
        return val
    
    def _init_motors(self):
        self.position_reader = GroupSyncRead(
            self.dynamixel.portHandler,
            self.dynamixel.packetHandler,
            ReadAttribute.POSITION.value,
            4)
        for id in self.servo_ids:
            self.position_reader.addParam(id)

        self.velocity_reader = GroupSyncRead(
            self.dynamixel.portHandler,
            self.dynamixel.packetHandler,
            ReadAttribute.VELOCITY.value,
            4)
        for id in self.servo_ids:
            self.velocity_reader.addParam(id)

        self.pos_writer = GroupSyncWrite(
            self.dynamixel.portHandler,
            self.dynamixel.packetHandler,
            self.dynamixel.ADDR_GOAL_POSITION,
            4)
        for id in self.servo_ids:
            self.pos_writer.addParam(id, [2048])

        self.pwm_writer = GroupSyncWrite(
            self.dynamixel.portHandler,
            self.dynamixel.packetHandler,
            self.dynamixel.ADDR_GOAL_PWM,
            2)
        for id in self.servo_ids:
            self.pwm_writer.addParam(id, [2048])
        self._disable_torque()

        self.motor_control_state = MotorControlType.DISABLED

    def read_position(self, tries=2):
        """
        Reads the joint positions of the robot. 2048 is the center position. 0 and 4096 are 180 degrees in each direction.
        :param tries: maximum number of tries to read the position
        :return: list of joint positions in range [0, 4096]
        """
        result = self.position_reader.txRxPacket()
        if result != 0:
            if tries > 0:
                return self.read_position(tries=tries - 1)
            else:
                print(f'failed to read position!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        positions = []
        for id in self.servo_ids:
            position = self.position_reader.getData(id, ReadAttribute.POSITION.value, 4)
            if position > 2 ** 31:
                position -= 2 ** 32
            positions.append(position)
        return np.array(positions)
    
    def read_velocity(self):
        """
        Reads the joint velocities of the robot.
        :return: list of joint velocities,
        """
        self.velocity_reader.txRxPacket()
        velocties = []
        for id in self.servo_ids:
            velocity = self.velocity_reader.getData(id, ReadAttribute.VELOCITY.value, 4)
            if velocity > 2 ** 31:
                velocity -= 2 ** 32
            velocties.append(velocity)
        return np.array(velocties)

    def set_goal_pos(self, action, servo_id=None):
        """
        :param action: list or numpy array of target joint positions in range [0, 4096]
        :param servo_id: servo id to set the goal position if controlling only one servo
        """
        # Clip the action to the limits
        action = np.clip(action, self.min_position_limit, self.max_position_limit)
        if not self.motor_control_state is MotorControlType.POSITION_CONTROL:
            self._set_position_control()
        for i, motor_id in enumerate(self.servo_ids):
            if servo_id is not None and servo_id != motor_id:
                continue
            data_write = [DXL_LOBYTE(DXL_LOWORD(action[i])),
                          DXL_HIBYTE(DXL_LOWORD(action[i])),
                          DXL_LOBYTE(DXL_HIWORD(action[i])),
                          DXL_HIBYTE(DXL_HIWORD(action[i]))]
            self.pos_writer.changeParam(motor_id, data_write)

        self.pos_writer.txPacket()
    
    def set_and_wait_goal_pos(self, action, threshold=1, servo_id=None):
        """
        Sets the goal position and waits until the robot reaches the goal position.
        :param action: list or numpy array of target joint positions in range [0, 4096]
        :param threshold: threshold for the velocity to consider the robot has reached the goal position
        :param servo_id: servo id to set the goal position if controlling only one servo
        """
        self.set_goal_pos(action, servo_id=servo_id)
        while True:
            time.sleep(0.1)
            vel = self.read_velocity()
            if np.all(np.abs(vel) <= threshold):
                break

    def set_pwm(self, action):
        """
        Sets the pwm values for the servos.
        :param action: list or numpy array of pwm values in range [0, 885]
        """
        if not self.motor_control_state is MotorControlType.PWM:
            self._set_pwm_control()
        for i, motor_id in enumerate(self.servo_ids):
            data_write = [DXL_LOBYTE(DXL_LOWORD(action[i])),
                          DXL_HIBYTE(DXL_LOWORD(action[i])),
                          ]
            self.pwm_writer.changeParam(motor_id, data_write)

        self.pwm_writer.txPacket()

    def set_trigger_torque(self):
        """
        Sets a constant torque torque for the last servo in the chain. This is useful for the trigger of the leader arm
        """
        self.dynamixel._enable_torque(self.servo_ids[-1])
        self.dynamixel.set_pwm_value(self.servo_ids[-1], 200)

    def limit_pwm(self, limit: Union[int, list, np.ndarray]):
        """
        Limits the pwm values for the servos in for position control
        @param limit: 0 ~ 885
        @return:
        """
        if isinstance(limit, int):
            limits = [limit, ] * len(self.servo_ids)
        else:
            limits = limit
        self._disable_torque()
        for motor_id, limit in zip(self.servo_ids, limits):
            self.dynamixel.set_pwm_limit(motor_id, limit)
        self._enable_torque()

    def limit_velocity(self, limit: Union[int, list, np.ndarray]):
        """
        Limits the velocity values for the servos in for velocity control
        @param limit: 0 ~ 2047
        @return:
        """
        if isinstance(limit, int):
            limits = [limit, ] * len(self.servo_ids)
        else:
            limits = limit
        self._disable_torque()
        for motor_id, limit in zip(self.servo_ids, limits):
            self.dynamixel.set_velocity_limit(motor_id, limit)
        self._enable_torque()

    def _disable_torque(self):
        print(f'disabling torque for servos {self.servo_ids}')
        for motor_id in self.servo_ids:
            self.dynamixel._disable_torque(motor_id)

    def _enable_torque(self):
        print(f'enabling torque for servos {self.servo_ids}')
        for motor_id in self.servo_ids:
            self.dynamixel._enable_torque(motor_id)

    def _set_pwm_control(self):
        self._disable_torque()
        for motor_id in self.servo_ids:
            self.dynamixel.set_operating_mode(motor_id, OperatingMode.PWM)
        self._enable_torque()
        self.motor_control_state = MotorControlType.PWM

    def _set_position_control(self):
        self._disable_torque()
        for motor_id in self.servo_ids:
            self.dynamixel.set_operating_mode(motor_id, OperatingMode.POSITION)
        # Set velocity limits
        for motor_id, limit in zip(self.servo_ids, self.velocity_limit):
            self.dynamixel.set_profile_velocity(motor_id, limit)
        # Set PID gains
        for motor_id, p_gain, i_gain in zip(self.servo_ids, self.position_p_gain, self.position_i_gain):
            self.dynamixel.set_P(motor_id, p_gain)
            self.dynamixel.set_I(motor_id, i_gain)
        self._enable_torque()
        self.motor_control_state = MotorControlType.POSITION_CONTROL
