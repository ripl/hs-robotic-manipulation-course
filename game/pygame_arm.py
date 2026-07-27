import json
from pathlib import Path
from robotics.robot.robot import Robot

class PygameArm():
    def __init__(self, config_path='../robotics/config.json', leader=True, claw=12):
        # Load robot settings
        with open(config_path, 'r') as f:
            config = json.load(f)
            if leader:
                self.arm_config = config['leader']
            else:
                self.arm_config = config['arm']

        # Create robot
        if leader:
            self.robot = Robot(device_name=self.arm_config['device_name'], 
                            servo_ids=self.arm_config['servo_ids'])
        else:
            self.robot = Robot(device_name=self.arm_config['device_name'], 
                            servo_ids=self.arm_config['servo_ids'],
                            velocity_limit=self.arm_config['velocity_limit'],
                            max_position_limit=self.arm_config['max_position_limit'],
                            min_position_limit=self.arm_config['min_position_limit'],
                            position_p_gain=self.arm_config['position_p_gain'],
                            position_i_gain=self.arm_config['position_i_gain'])
            
        
        self.claw = claw

    def get_positions(self):
        return self.robot.read_position_dict()

    def get_position(self, servo_id, min=None, max=None) -> float:
        result = self.robot.read_position_dict()[servo_id]

        if min and max:
            middle = (min + max) / 2
            result += middle

            # TODO: Add some scaling

        return result

    def is_claw_closed(self, threshold=2250):
        return self.get_position(self.claw) <= threshold
