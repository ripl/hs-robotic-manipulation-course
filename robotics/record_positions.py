import os, json, threading, argparse
from robotics.robot.robot import Robot

# Square and pose types
SQUARES = ['A', 'B', 'C', 'D', 'E', 'F', '0', '1', '2', '3', '4', '5', '6', '7', '8']
#For Recording TicTacToe Positions
#SQUARES = ['connect','1','2','3','4','5','6','7']
#For Recording Connect4 Positions
POSE_TYPES = ['hover', 'pre-grasp', 'grasp', 'post-grasp']

def parse_arguments():
    parser = argparse.ArgumentParser(description='Record positions for tic-tac-toe game.')
    parser.add_argument('-l', '--leader', action='store_true', default=True, 
                        help='Enable teleoperation using a leader arm.')
    return parser.parse_args()
    #variable default initially set to False and not changed elsewhere setting it to True lets the leader arm function properly


def load_robot_settings(args):
    with open('config.json') as f:
        config = json.load(f)
    arm_config = config['arm']
    leader_config = config['leader'] if args.leader else None
    return arm_config, leader_config

def initialize_robots(arm_config, leader_config):
    arm = Robot(device_name=arm_config['device_name'], 
                servo_ids=arm_config['servo_ids'],
                velocity_limit=arm_config['velocity_limit'],
                max_position_limit=arm_config['max_position_limit'],
                min_position_limit=arm_config['min_position_limit'],
                position_p_gain=arm_config['position_p_gain'],
                position_i_gain=arm_config['position_i_gain'])
    leader = None
    if leader_config:
        leader = Robot(device_name=leader_config['device_name'], 
                       servo_ids=leader_config['servo_ids'])
        leader.set_trigger_torque()
    return arm, leader

# TODO: Manual position recording is not that accurate
# Function to record positions manually
def record_position(arm, square, pose_type):
    arm._disable_torque()
    print(f'Move the arm to the {pose_type} position of square {square}. Press enter to record. Press s to skip.')
    user_input = input()
    if user_input == 's':
        return None
    arm._enable_torque()
    input()
    pos = arm.read_position()
    pos = [int(p) for p in pos]
    if pose_type in ['grasp', 'post-grasp']:
        pos[-1] -= 50
    return pos

# Function to record positions with leader arm
def record_position_with_leader(arm, leader, square, pose_type):
    print(f'Move the arm to the {pose_type} position of square {square}.')
    # Wait for user input to stop teleoperation
    stop = threading.Event()
    def wait_for_input(stop):
        input('Press enter to record.')
        stop.set()
    thread = threading.Thread(target=wait_for_input, args=(stop,))
    thread.start()
    # Teleoperation
    while not stop.is_set():
        pos = leader.read_position()
        arm.set_goal_pos(pos)
    thread.join()
    # Record position
    pos = [int(p) for p in pos]
    return pos

def main():
    args = parse_arguments()
    arm_config, leader_config = load_robot_settings(args)
    arm, leader = initialize_robots(arm_config, leader_config)
    
    # Go to game home position
    arm.set_and_wait_goal_pos(arm_config['home_pos'])

    # Create actions.json if it does not exist
    if not os.path.exists('actions_c4.json'):
        with open('actions_c4.json', 'w') as f:
            json.dump({}, f)
    with open('actions_c4.json') as f:
        positions = json.load(f)

    # Record positions for each square and pose type
    for square in SQUARES:
        print(f'Record positions for square {square}. Press enter to record. Press s to skip.')
        user_input = input()
        if user_input == 's':
            continue
        if square not in positions:
            positions[square] = {}
        for pose_type in POSE_TYPES:
            if not args.leader:
                pos = record_position(arm, square, pose_type)
            else:
                pos = record_position_with_leader(arm, leader, square, pose_type)
            if pos is not None:
                positions[square][pose_type] = pos
    with open('actions_c4.json', 'w') as f:
        json.dump(positions, f, indent=4)

    # Go to rest position and disable torque
    arm.set_and_wait_goal_pos(arm_config['rest_pos'])
    arm._disable_torque()

if __name__ == "__main__":
    main()
