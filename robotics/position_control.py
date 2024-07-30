import json
import time
import os
import threading
import argparse
import numpy as np
import pandas as pd
from robot.robot import Robot

CONVERSION_FACTOR = 4096 / 360
VALID_POSE_TYPES = ['hover', 'pre-grasp', 'grasp', 'post-grasp']
CONFIG_FILE = 'config.json'
ACTIONS_FILE = 'actions.json'


def parse_arguments():
    """
    Parse command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(description='Record positions for tic-tac-toe game.')
    parser.add_argument('-l', '--leader', action='store_true', default=False, 
                        help='Enable teleoperation using a leader arm.')
    return parser.parse_args()


def load_json_file(file_path):
    """
    Load a JSON file from the specified path.

    Args:
        file_path (str): Path to the JSON file.

    Returns:
        dict: Parsed JSON data, or None if file is not found.
    """
    if not os.path.exists(file_path):
        print(f"Error: {file_path} file not found.")
        return None
    with open(file_path) as f:
        return json.load(f)


def save_json_file(data, file_path):
    """
    Save data to a JSON file.

    Args:
        data (dict): Data to be saved.
        file_path (str): Path to the JSON file.
    """
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)


def calculate_action_margin_of_error(arm, action):
    """
    Calculate and display the margin of error for a specified action.

    Args:
        arm (Robot): The robotic arm instance.
        action (str): The name of the action to be tested.
    """
    actions = load_json_file(ACTIONS_FILE)
    if not actions or action not in actions:
        print(f"Error: {action} is not a valid action.")
        return

    print(f"Testing Action: {action}")
    poses = actions[action]
    for pose_type, recorded_positions in poses.items():
        print(f"  Pose: {pose_type}")
        arm.set_and_wait_goal_pos(recorded_positions)
        time.sleep(0.25)

        actual_positions = [int(p) for p in arm.read_position()]
        errors = [abs(recorded_positions[i] - actual_positions[i]) for i in range(len(recorded_positions))]
        errors_in_degrees = np.round(np.array(errors) / CONVERSION_FACTOR, 2)

        for i in range(len(errors_in_degrees)):
            print(f"    Servo ID: {arm.servo_ids[i]}, Error: {errors_in_degrees[i]} degrees")
    print()


def load_robot_settings(args):
    """
    Load robot settings from the configuration file.

    Args:
        args (argparse.Namespace): Parsed command-line arguments.

    Returns:
        tuple: Arm configuration and leader configuration (if any).
    """
    config = load_json_file(CONFIG_FILE)
    if not config:
        return None, None

    arm_config = config['arm1']
    lead_config = config['leader'] if args.leader else None
    return arm_config, lead_config


def initialize_robot(arm_config, lead_config):
    """
    Initialize the robotic arm and leader (if any).

    Args:
        arm_config (dict): Configuration for the robotic arm.
        lead_config (dict): Configuration for the leader arm (if any).

    Returns:
        tuple: Initialized robotic arm and leader arm (if any).
    """
    arm = Robot(
        arm_config['device_name'],
        arm_config['baudrate'], 
        arm_config['servo_ids'],
        arm_config['velocity_limit'],
        arm_config['max_position_limit'],
        arm_config['min_position_limit'],
        arm_config['position_p_gain'],
        arm_config['position_i_gain']
    )

    lead = None
    if lead_config:
        lead = Robot(
            lead_config['device_name'], 
            lead_config['baudrate'], 
            lead_config['servo_ids']
        )
        lead.set_trigger_torque()
    return arm, lead


def record_position_with_leader(arm, lead, action, pose_type):
    """
    Record the position of the arm using a leader arm.

    Args:
        arm (Robot): The robotic arm instance.
        lead (Robot): The leader arm instance.
        action (str): The name of the action being recorded.
        pose_type (str): The type of pose being recorded.

    Returns:
        list: Recorded positions.
    """
    print(f'Move the arm to the {pose_type} position of the action called "{action}"')
    stop = threading.Event()

    def wait_for_input(stop_event):
        input('Press enter to record. ')
        stop_event.set()

    thread = threading.Thread(target=wait_for_input, args=(stop,))
    thread.start()

    while not stop.is_set():
        positions = lead.read_position()
        arm.set_goal_pos(positions)
    thread.join()

    positions = [int(p) for p in positions]
    print(f'{action}: {pose_type} recorded successfully')

    return positions


def print_joint_angles(arm):
    """
    Print the current joint angles of the robotic arm.

    Args:
        arm (Robot): The robotic arm instance.
    """
    time.sleep(0.25)
    cur_pos = arm.read_position()
    positions_in_degrees = np.round(np.array(cur_pos) / CONVERSION_FACTOR, 2)
    df = pd.DataFrame({
        'ID': arm.servo_ids,
        'Degrees': positions_in_degrees
    })
    print('\n', df.to_string(index=False), '\n')


def change_servo_angle(arm, servo_id, delta):
    """
    Change the angle of a specific servo motor.

    Args:
        arm (Robot): The robotic arm instance.
        servo_id (int): The ID of the servo motor.
        delta (float): The change in angle.
    """
    positions = [int(p) for p in arm.read_position()]
    servo_id_index = arm.servo_ids.index(servo_id)
    positions[servo_id_index] += delta
    arm.set_and_wait_goal_pos(positions, servo_id=servo_id)


def update_action(actions, action, pose_type, positions):
    """
    Update an action with new positions.

    Args:
        actions (dict): Existing actions.
        action (str): The name of the action.
        pose_type (str): The type of pose being updated.
        positions (list): The new positions.
    """
    if action not in actions:
        actions[action] = {}
    actions[action][pose_type] = positions
    save_json_file(actions, ACTIONS_FILE)


def record_action(arm, action, pose_type):
    """
    Record a new action or update an existing one.

    Args:
        arm (Robot): The robotic arm instance.
        action (str): The name of the action.
        pose_type (str): The type of pose being recorded.

    Returns:
        bool: True if successful, False otherwise.
    """
    if pose_type not in VALID_POSE_TYPES:
        print(f"pose_type must be one of {VALID_POSE_TYPES}")
        return False

    actions = load_json_file(ACTIONS_FILE) or {}

    positions = [int(p) for p in arm.read_position()]
    update_action(actions, action, pose_type, positions)
    return True


def go_to_pose(arm, action, pose_type):
    """
    Move the robotic arm to a specified pose within an action.

    Args:
        arm (Robot): The robotic arm instance.
        action (str): The name of the action.
        pose_type (str): The type of pose to go to.

    Returns:
        bool: True if successful, False otherwise.
    """
    if pose_type not in VALID_POSE_TYPES:
        print(f"pose_type must be one of {VALID_POSE_TYPES}")
        return False

    actions = load_json_file(ACTIONS_FILE)
    if not actions or action not in actions:
        print(f"Error: {action} is not valid. Please enter a valid action.")
        return

    arm.set_and_wait_goal_pos(actions[action][pose_type])
    print("Requested pose in place. You may proceed.")


def manual_record(arm, action, pose_type):
    """
    Manually record a new pose for an action.

    Args:
        arm (Robot): The robotic arm instance.
        action (str): The name of the action.
        pose_type (str): The type of pose being recorded.

    Returns:
        bool: True if successful, False otherwise.
    """
    if pose_type not in VALID_POSE_TYPES:
        print(f"pose_type must be one of {VALID_POSE_TYPES}")
        return False

    actions = load_json_file(ACTIONS_FILE) or {}
    if action not in actions:
        print(f"Error: {action} is not valid. Please enter a valid action.")
        return

    arm._disable_torque()
    print("You have entered manual record. BE GENTLE!!")
    print(f'Move the arm to the {pose_type} of the {action}.')
    user_input = input('Press "r" to record and "s" to skip.')
    if user_input == 's':
        arm.enable_torque()
        arm.set_and_wait_goal_pos([2048, 1800, 1850, 1100, 2048, 2048])
        return None

    arm._enable_torque()
    positions = [int(p) for p in arm.read_position()]
    if pose_type in ['grasp', 'post-grasp']:
        positions[-1] -= 50

    update_action(actions, action, pose_type, positions)
    print("Manual record successful.")


def initiate_action(arm, action):
    """
    Initiate a sequence of poses for a specified action.

    Args:
        arm (Robot): The robotic arm instance.
        action (str): The name of the action.
    """
    actions = load_json_file(ACTIONS_FILE)
    if not actions or action not in actions:
        print(f"Error: {action} is not a valid action.")
        return

    for pose in VALID_POSE_TYPES:
        if pose in actions[action]:
            arm.set_and_wait_goal_pos(actions[action][pose])
            time.sleep(0.25)
        else:
            print(f"Error: {pose} is not found, {action} is incomplete.")
            return
    print(f"{action} completed successfully.")


def handle_user_input(user_input, arm, lead, arm_config):
    """
    Handle user input to control the robotic arm.

    Args:
        user_input (str): The user input command.
        arm (Robot): The robotic arm instance.
        lead (Robot): The leader arm instance (if any).
        arm_config (dict): Configuration for the robotic arm.

    Returns:
        bool: True to continue, False to exit.
    """
    if user_input == 'q':
        print("Exiting Position Control...")
        print("Goodbye!")
        return False
    elif user_input == 'm':
        action = input("Enter action you want to modify: ")
        pose_type = input("Enter pose you'd like to manually set: ")
        manual_record(arm, action, pose_type)
    elif user_input == 'g':
        action = input("Enter action name: ")
        pose_type = input("Enter pose you'd like to go to: ")
        go_to_pose(arm, action, pose_type)
    elif user_input == 'a':
        action = input('Enter the action you want to initiate: ')
        initiate_action(arm, action)
    elif user_input == 'p':
        servo_id = int(input("Enter Servo id to be positioned: "))
        if servo_id not in arm_config['servo_ids']:
            print(f'Invalid servo ID. Please enter one of {arm_config["servo_ids"]}\n')
            return True
        delta = float(input('Enter delta angle: '))
        delta = int(delta * CONVERSION_FACTOR)
        change_servo_angle(arm, servo_id, delta)
    elif user_input == 'r':
        action_name = input('Enter action name: ')
        pose_type = input('Enter pose type (hover, pre-grasp, grasp, post-grasp): ')
        success = record_action(arm, action_name, pose_type)
        if success:
            print('Action recording successful')
        else:
            print('Action recording failed')
    elif user_input == 't':
        action = input('Enter action to be tested: ')
        calculate_action_margin_of_error(arm, action)
    return True


def main():
    """
    Main function to execute the robotic arm control program.
    """
    args = parse_arguments()
    arm_config, lead_config = load_robot_settings(args)
    if not arm_config:
        return

    arm, lead = initialize_robot(arm_config, lead_config)

    if not args.leader:
        arm.set_and_wait_goal_pos(arm_config['home_pos'])
    else:
        lead_positions = [int(p) for p in lead.read_position()]
        arm.set_and_wait_goal_pos(lead_positions)

    if not os.path.exists(ACTIONS_FILE):
        save_json_file({}, ACTIONS_FILE)

    print('\nWelcome to position control mode!\n')
    print("This mode provides several methods for positioning your robotic arm.")
    print("Although these methods are useful, be warned. Accuracy in movements is spotty.\n")

    proceed = input("Would you like to proceed? [y/n] ").lower() == 'y'

    while proceed:
        try:
            os.system('clear')
            print("Joint Angle Readings:")
            print_joint_angles(arm)
            if args.leader:
                print("You have entered Teleoperation mode. You can use the leader arm to position your Robotic Arm.")
                action = input("Enter an action name to record: ")
                for pose_type in VALID_POSE_TYPES:
                    positions = record_position_with_leader(arm, lead, action, pose_type)
                    actions = load_json_file(ACTIONS_FILE) or {}
                    update_action(actions, action, pose_type, positions)
                    
                user_input = input("Would you like to exit Teleoperation mode? [Y/n]").lower()
                if user_input == 'y':
                    print("Exiting Teleoperation Position Control...")
                    print("Goodbye!")
                    proceed = False
            else:
                print('1) Enter "p" to position a specific motor.')
                print('2) Enter "a" to use a saved action.')
                print('3) Enter "g" to go to a specific pose within an action.')
                print('4) Enter "m" to manually position the robot. Be warned, the reading is not accurate.')
                print('5) Enter "r" to record a new action.')
                print('6) Enter "t" to test the margin of error of an action.')
                print('7) Enter "q" to quit.\n')
                user_input = input('Enter task: ').lower()
                proceed = handle_user_input(user_input, arm, lead, arm_config)
        except KeyboardInterrupt:
            break

    print()
    arm.set_and_wait_goal_pos(arm_config['rest_pos'])
    arm._disable_torque()
    if args.leader:
        lead._disable_torque()


if __name__ == '__main__':
    main()
