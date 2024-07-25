import json, time
from robotics.robot.robot import Robot

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
            min_position_limit=arm_config['min_position_limit'],
            position_p_gain=arm_config['position_p_gain'],
            position_i_gain=arm_config['position_i_gain'])

# Go to home start position
arm.set_and_wait_goal_pos(arm_config['home_pos'])

def move_piece(start, end):
    arm.set_and_wait_goal_pos(positions[start]['hover'])
    arm.set_and_wait_goal_pos(positions[start]['pre-grasp'])
    arm.set_and_wait_goal_pos(positions[start]['grasp'])
    arm.set_and_wait_goal_pos(positions[start]['post-grasp'])
    arm.set_and_wait_goal_pos(positions[end]['hover'])
    arm.set_and_wait_goal_pos(positions[end]['pre-grasp'])
    arm.set_and_wait_goal_pos(positions[end]['grasp'])
    arm.set_and_wait_goal_pos(positions[end]['post-grasp'])
    arm.set_and_wait_goal_pos(arm_config['home_pos'])


# Sample game
move_piece('A', '4')
time.sleep(3) # 0
move_piece('B', '1')

time.sleep(3) #3
move_piece('C', '6')
time.sleep(3) # 2
move_piece('D', '2')
time.sleep(3) # 7
move_piece('E', '8')

# Go to home position and disable torque
arm.set_and_wait_goal_pos(arm_config['rest_pos'])
arm._disable_torque()
