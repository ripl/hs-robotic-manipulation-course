import json, time, os, threading, argparse
import numpy as np
import pandas as pd
from robot.robot import Robot

CONVERSION_FACTOR = 4096 / 360
VALID_POSE_TYPES = ['hover', 'pre-grasp', 'grasp', 'post-grasp']


def parse_arguments():
    parser = argparse.ArgumentParser(description='Record positions for tic-tac-toe game.')
    parser.add_argument('-l', '--leader', action='store_true', default=False, 
                        help='Enable teleoperation using a leader arm.')
    return parser.parse_args()

def calculate_action_margin_of_error(arm, action):
    """
    Calculate and display the margin of error of what is saved in actions.json 
    and the actual readings during execution of a specific action.
    
    Inputs:
        arm (object): The robotic arm instance.
        action (str): The name of the action to be tested.
    """
    if not os.path.exists('actions.json'):
        print("Error: actions.json file not found.")
        return
    
    with open('actions.json') as f:
        actions = json.load(f)
    
    if action not in actions:
        print(f"Error: {action} is not a valid action.")
        return
    
    print(f"Testing Action: {action}")
    poses = actions[action]
    for pose_type, recorded_positions in poses.items():
        print(f"  Pose: {pose_type}")
        
        # Move to the recorded pose
        arm.set_and_wait_goal_pos(recorded_positions)
        time.sleep(0.25)  # Ensure the arm has enough time to reach the position
        
        # Read the actual positions
        actual_positions = arm.read_position()
        actual_positions = [int(p) for p in actual_positions]
        
        # Calculate the margin of error
        errors = [np.abs(rp - ap) for rp, ap in zip(recorded_positions, actual_positions)]
        errors_in_degrees = np.round(np.array(errors) / CONVERSION_FACTOR, 2)
        
        # Display the errors
        for servo_id, error in zip(arm.servo_ids, errors_in_degrees):
            print(f"    Servo ID: {servo_id}, Error: {error} degrees")
        
    print()

def load_robot_settings(args):
    """
    Load the config file for the Robot arm instances.

    Inputs:
        None

    Returns:
        arm_config (dict): A dictionary continaing the arm configuration parameters.
    """
    with open('config.json') as f:
        config = json.load(f)

    arm_config = config['arm']
    lead_config = config['leader'] if args.leader else None
    
    return arm_config, lead_config

def initialize_robot(arm_config, lead_config):
    """
    Creates and initializes a robot instance using the provided arm configuration.

    Arm configuration should include:
        - 'device_name': Name of the port connected to the robot arm.
        - 'baudrate': Bits per second.
        - 'servo_ids': List of servo IDs for the arm.
        - 'velocity_limit': Maximum velocity limit of each servo of the arm.
        - 'max_position_limit': Maximum position limit of each servo of the arm.
        - 'min_position_limit': Minimum position limit of each servo of the arm.

    Inputs:
        arm_config (dict): A dictionary containing the arm configuration parameters.

    Returns:
        arm (object): A conigured (arm) Robot instance.
    """
    arm = Robot(
                arm_config['device_name'],
                arm_config['baudrate'], 
                arm_config['servo_ids'],
                arm_config['velocity_limit'],
                arm_config['max_position_limit'],
                arm_config['min_position_limit']
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
    print(f'Move the arm to the {pose_type} position of the action called "{action}"')
    stop = threading.Event()
    def wait_for_input(stop):
        input('Press enter to record. ')
        stop.set()
    thread = threading.Thread(target=wait_for_input, args=(stop,))
    thread.start()
     # Teleoperation
    while not stop.is_set():
        pos = lead.read_position()
        arm.set_goal_pos(pos)
    thread.join()
    # Record position
    positions = [int(p) for p in positions]

    print('Leader Arm Recording Successfull')

    return positions

def print_joint_angles(arm):
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
    Adjusts the angle of a specified servo motor by a given delta and prints 
    the updated angles of all servos in the robotic arm instance.

    Inputs:
        arm (object): The robotic arm instance
        servo_id (int): The id of the servo whose angle is to be changed.
        delta (float): The +/- rotation to be applied to the servo motor.

    Returns:
        None
    """
    pos = arm.read_position()
    pos = [int(p) for p in pos]
    servo_id_index = arm.servo_ids.index(servo_id)
    pos[servo_id_index] += delta
    arm.set_and_wait_goal_pos(pos, servo_id=servo_id)

def record_action(arm, action, pose_type):
    """
    Updates an existing action or creates a new one if it doesn't exist, 
    and records one of the four pose types for that action.

    An action consists of four pose types:
        - 'hover': Arm placement before attempting to grasp an object.
        - 'pre-grasp': Arm moves into a grasping position.
        - 'grasp': Arm grasps the object.
        - 'post-grasp': Arm lifts the object.
    
    Inputs:
        arm (object): The robotic arm instance.
        action (str): The name of the action to be updated or created.
        pose_type (str): The type of pose to be recorded (one of 'hover', 'pre-grasp', 'grasp', 'post_grasp').

    Returns:
        bool: True for a successful action record, otherwise False
    """
    if pose_type not in VALID_POSE_TYPES:
        print(f"pose_type must be one of {VALID_POSE_TYPES}")
        return False

    # Load existing actions from the file
    with open('actions.json') as f:
        actions = json.load(f)

    # Read the current position of the arm
    positions = arm.read_position()
    positions = [int(p) for p in positions]

    # Update the action with the specified pose type
    if action not in actions:
        actions[action] = {}

    actions[action][pose_type] = positions

    # Write the updated actions back to the file
    with open('actions.json', 'w') as f:
        json.dump(actions, f, indent=4)

    return True

def go_to_pose(arm, action, pose_type):
    if pose_type not in VALID_POSE_TYPES:
        print(f"pose_type must be one of {VALID_POSE_TYPES}")
        return False

    # Load existing actions from the file
    with open('actions.json') as f:
        actions = json.load(f)

    # Update the action with the specified pose type
    if action not in actions:
        print("Error: {action} is not valid. Please enter a valid action.")
        return
    
    arm.set_and_wait_goal_pos(actions[action][pose_type])
    print("Requested pose in place. You may proceed.")

def manual_record(arm, action, pose_type):
    if pose_type not in VALID_POSE_TYPES:
        print(f"pose_type must be one of {VALID_POSE_TYPES}")
        return False

    # Load existing actions from the file
    with open('actions.json') as f:
        actions = json.load(f)

    # Update the action with the specified pose type
    if action not in actions:
        print("Error: {action} is not valid. Please enter a valid action.")
        return
    
    arm._disable_torque()
    print("You have entered manual record. BE GENTLE!!")
    print(f'Move the arm to the {pose_type} of the {action}.')
    user_input= input('Press "r" to record and "s" to skip.')
    if user_input == 's':
        arm.enable_torque()
        arm.set_and_wait_goal_pos([2048, 1800, 1850, 1100, 2048, 2048])
        return None
    else:
        arm._enable_torque()
        positions = arm.read_position()
        positions = [int(p) for p in positions]
        if pose_type in ['grasp', 'post_grasp']:
            positions[-1] -= 50

        actions[action][pose_type] = positions

        # Write the updated actions back to the file
        with open('actions.json', 'w') as f:
            json.dump(actions, f, indent=4) 
    
    print("Manual record successful.")


def initiate_action(arm, action):
    """
    Initiate an action (if present) within the action.json file.

    Inputs:
        arm (object): The robotic arm instance.
        action (str): The name of the action to be executed.
    
    Returns:
        None
    """
    # Load existing actions from the file
    with open('actions.json') as f:
        actions = json.load(f)

    if action not in actions:
        print(f"Error: {action} is not a valid action.")
        return

    # Initiate each pose within the provided action
    # Sleep for 0.25 seconds after each pose.
    for pose in VALID_POSE_TYPES:

        if pose in actions[action]:
            arm.set_and_wait_goal_pos(actions[action][pose])
            time.sleep(0.25)
        else:
            print(f"Error: {pose} is not found, {action} is incomplete.")
            return
    
    print(f"{action} completed successfully.")

def main():
    args = parse_arguments()
    arm_config, lead_config = load_robot_settings(args)
    arm , lead = initialize_robot(arm_config, lead_config)
    
    # Go to either home or lead position
    if not args.leader:
        arm.set_and_wait_goal_pos(arm_config['home_pos'])
    else:
        lead_positions = lead.read_position()
        lead_positions = [int(p) for p in lead_positions]
        arm.set_and_wait_goal_pos(lead_positions)


    # Create an actions.json file if it does not already exist
    if not os.path.exists('actions.json'):
        with open('actions.json', 'w') as f:
            json.dump({}, f)

    # Position control loop
    print('\nWelcome to position control mode!\n')
    print("This mode provides several methods for positioning your robotic arm.")
    print("Although these methods are useful, be warned. Accurary in movements is spotty.\n")

    proceed = input("Would you like to proceed? [y/n] ").lower()
    print()

    if proceed == 'y':
        proceed = True
    else:
        proceed = False

    while proceed:
        try:
            os.system('clear')
            print("Joint Angle Readings:")
            print_joint_angles(arm)
            if args.leader:
                print("You have entered Teleoperation mode. You can use the leader arm to position your Robotic Arm.")
                print()
                print("First enter the action name, followed by the pose type you want to record.")
                print()
                action = input("Enter an action name: ")
                pose_type = input("Enter a pose_type: ")
                print()
                positions = record_position_with_leader(arm, lead, action, pose_type)
                 # Load existing actions from the file
                with open('actions.json') as f:
                    actions = json.load(f)
                
                # Update the action with the specified pose type
                if action not in actions:
                    actions[action] = {}

                actions[action][pose_type] = positions

                # Write the updated actions back to the file
                with open('actions.json', 'w') as f:
                    json.dump(actions, f, indent=4)
            else:
                print('1) Enter "p" to position a specific motor.')
                print('2) Enter "a" to use a saved action')
                print('3) Enter "g" to go to a specific pose within an action.')
                print('4) Enter "m" to manually position the robot. Be warned, the reading is not accurate.')
                print('5) Enter "r" at any time to record new action.')
                print('6) Enter "t" to test the margin of error of an action.')
                print('7) Enter "q" at any time to quit.\n')
                user_input = input('Enter task: ').lower()
                

                if user_input in ['p', 'r', 'm', 'g', 'q', 'a', 't']:
                    if user_input == 'q':
                        print("Exiting Position Control...")
                        print("Goodbye!")
                        break
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
                        print()
                    elif user_input == 'p':
                        servo_id = int(input("Enter Servo id to be positioned: "))
                        if servo_id not in arm_config['servo_ids']:
                            print(f'Invalid servo ID. Please enter one of {arm_config["servo_ids"]}\n')
                            continue
                        delta = float(input('Enter delta angle: '))
                        delta = int(delta * CONVERSION_FACTOR)
                        change_servo_angle(arm, servo_id, delta)
                    elif user_input.lower() == 'r':
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
                    print()
                else:
                    continue
        except KeyboardInterrupt:
            break

    # Go to rest position and disable torque
    print()
    arm.set_and_wait_goal_pos(arm_config['rest_pos'])
    arm._disable_torque()
    if args.leader:
        lead._disable_torque()

if __name__ == '__main__':
    main()
