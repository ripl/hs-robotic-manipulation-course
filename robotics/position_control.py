import json, time
import numpy as np
import pandas as pd
from robot.robot import Robot

CONVERSION_FACTOR = 4096 / 360

def load_robot_settings():
    with open('config.json') as f:
        config = json.load(f)
    arm_config = config['arm']
    return arm_config

def initialize_robot(arm_config):
    arm = Robot(device_name=arm_config['device_name'], 
                servo_ids=arm_config['servo_ids'],
                velocity_limit=arm_config['velocity_limit'],
                max_position_limit=arm_config['max_position_limit'],
                min_position_limit=arm_config['min_position_limit'])
    return arm

def change_servo_angle(arm, servo_id, delta):
    pos = arm.read_position()
    pos = [int(p) for p in pos]
    servo_id_index = arm.servo_ids.index(servo_id)
    pos[servo_id_index] += delta
    arm.set_and_wait_goal_pos(pos, servo_id=servo_id)
    # Print the current position of the servo after the move
    time.sleep(0.25)
    cur_pos = arm.read_position()
    positions_in_degrees = np.round(np.array(cur_pos) / CONVERSION_FACTOR, 2)
    df = pd.DataFrame({
        'ID': arm.servo_ids,
        'Degrees': positions_in_degrees
    })
    print('\n', df.to_string(index=False), '\n')

def main():
    arm_config = load_robot_settings()
    arm = initialize_robot(arm_config)
    
    # Go to home position
    arm.set_and_wait_goal_pos(arm_config['home_pos'])

    # Position control loop
    print('\n\nWelcome to position control mode!')
    print('Enter servo ID and delta angle (in degrees) to move the servo.')
    print('Delta angle can be positive or negative, and the servo angle will change by that amount.')
    print('The current position of the servo will be printed after each move.')
    print('Enter "q" at any time to quit.\n\n')
    while True:
        try:
            user_input = input('Enter servo ID: ')
            if user_input.lower() == 'q':
                break
            servo_id = int(user_input)
            if servo_id not in arm_config['servo_ids']:
                print(f'Invalid servo ID. Please enter one of {arm_config["servo_ids"]}\n')
                continue
            delta_input = input('Enter delta angle: ')
            if delta_input.lower() == 'q':
                break
            delta = float(delta_input)
            delta = int(delta * CONVERSION_FACTOR)
            change_servo_angle(arm, servo_id, delta)
        except KeyboardInterrupt:
            break

    # Go to rest position and disable torque
    arm.set_and_wait_goal_pos(arm_config['rest_pos'])
    arm._disable_torque()

if __name__ == '__main__':
    main()
