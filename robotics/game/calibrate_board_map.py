import argparse
import json
import os

from robotics.robot.robot import Robot


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, 'config.json')
ACTIONS_PATH = os.path.join(BASE_DIR, 'actions.json')
OUTPUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'board_position_map.json')
BOARD_KEYS = [str(i) for i in range(9)]


def parse_args():
    parser = argparse.ArgumentParser(description='Calibrate tic-tac-toe board position mapping.')
    parser.add_argument(
        '--pose',
        choices=['hover', 'pre-grasp'],
        default='hover',
        help='Pose to move to for each numbered square. Default: hover.',
    )
    parser.add_argument(
        '--output',
        default=OUTPUT_PATH,
        help='Where to save the observed mapping.',
    )
    return parser.parse_args()


def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)


def initialize_arm(config):
    arm_config = config['arm']
    arm = Robot(
        device_name=arm_config['device_name'],
        baudrate=arm_config['baudrate'],
        servo_ids=arm_config['servo_ids'],
        velocity_limit=arm_config['velocity_limit'],
        max_position_limit=arm_config['max_position_limit'],
        min_position_limit=arm_config['min_position_limit'],
        position_p_gain=arm_config['position_p_gain'],
        position_i_gain=arm_config['position_i_gain'],
    )
    return arm, arm_config


def prompt_observed_square(action_key):
    while True:
        observed = input(f'Position {action_key} went to physical square [0-8], s=skip, q=quit: ').strip()
        if observed in BOARD_KEYS or observed in {'s', 'q'}:
            return observed
        print('Please enter 0-8, s, or q.')


def main():
    args = parse_args()
    config = load_json(CONFIG_PATH)
    actions = load_json(ACTIONS_PATH)

    missing = [key for key in BOARD_KEYS if key not in actions or args.pose not in actions[key]]
    if missing:
        raise KeyError(f'Missing {args.pose} pose for board positions: {missing}')

    arm, arm_config = initialize_arm(config)
    mapping = {}

    try:
        print(f'Using {args.pose} pose only. This should hover over each recorded board square.')
        input('Clear the robot workspace, then press Enter to start.')
        arm.set_and_wait_goal_pos(arm_config['home_pos'])

        for action_key in BOARD_KEYS:
            print(f'\nMoving to recorded position {action_key}...')
            arm.set_and_wait_goal_pos(actions[action_key][args.pose])
            observed = prompt_observed_square(action_key)

            if observed == 'q':
                break
            if observed != 's':
                mapping[action_key] = observed

            arm.set_and_wait_goal_pos(arm_config['home_pos'])

    finally:
        print('\nReturning to rest and disabling torque.')
        arm.set_and_wait_goal_pos(arm_config['rest_pos'])
        arm._disable_torque()

    with open(args.output, 'w') as f:
        json.dump(mapping, f, indent=4)

    print(f'\nSaved observed mapping to {args.output}')
    print('Recorded action key -> observed physical square:')
    print(json.dumps(mapping, indent=4))

    inverse = {observed: action_key for action_key, observed in mapping.items()}
    if len(inverse) == len(mapping):
        print('\nUse this as BOARD_POSITION_MAP in players.py:')
        print(json.dumps({key: inverse[key] for key in sorted(inverse)}, indent=4))
    else:
        print('\nSome physical squares were observed more than once; retest those before updating players.py.')


if __name__ == '__main__':
    main()
