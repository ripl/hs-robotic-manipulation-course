import json
from robot.robot import Robot

# Load robot settings
with open('../config.json') as f:
    config = json.load(f)
    arm_config = config['arm']

# Load game positions
with open('../actions.json') as f:
    positions = json.load(f)

# Dynamixel configuration
arm = Robot(device_name=arm_config['device_name'], 
            servo_ids=arm_config['servo_ids'],
            velocity_limit=arm_config['velocity_limit'],
            max_position_limit=arm_config['max_position_limit'],
            min_position_limit=arm_config['min_position_limit'],)

# Go to home start position
arm.set_and_wait_goal_pos(arm_config['home_pos'])

# Write this function!
def move_piece(start, end):
    ''' Move a piece from start to end position. 
    '''
    pass

# Hard code a sample move to see if your code works!

# Go to home position and disable torque
arm.set_and_wait_goal_pos(arm_config['rest_pos'])
arm._disable_torque()
