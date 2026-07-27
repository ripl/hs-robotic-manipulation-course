import os, json, threading, argparse, time
from robotics.robot.robot import Robot
from vision import BoardVision

def parse_arguments():
    parser = argparse.ArgumentParser(description='Record positions for tic-tac-toe game.')
    parser.add_argument('-l', '--leader', action='store_true', default=False, 
                        help='Enable teleoperation using a leader arm.')
    return parser.parse_args()

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
def record_position(arm):
    arm._disable_torque()
    print(f'Move the arm to the calibration position. Press enter to begin.')
    user_input = input()
    if user_input == 's':
        return None
    arm._enable_torque()
    input()
    pos = arm.read_position()
    pos = [int(p) for p in pos]
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

def record_deltas(arm, vision, servo, delta):
    delta_x_avg = []
    delta_y_avg = []
    delta_a_avg = []

    for trial in range(3):
        # Record and move to initial position
        arm._disable_torque()
        input("Put the arm in the initial position. ")
        arm._enable_torque()
        root_pos = [int(p) for p in arm.read_position()]
        arm.set_and_wait_goal_pos(root_pos)

        # Capture initial piece info
        time.sleep(2.0)
        x1, y1, a1 = vision.get_handle_info()

        print(x1,y1,a1)
        time.sleep(2.0)

        # Move to new position
        new_pos = root_pos.copy()
        new_pos[servo] += delta
        arm.set_and_wait_goal_pos(new_pos)

        # Capture new piece info
        time.sleep(2.0)
        x2, y2, a2 = vision.get_handle_info()
        print(x2,y2,a2)
        time.sleep(2.0)

        if all(x != -1 for x in (x1, y1, a1, x2, y2, a2)):
            delta_x_avg.append(x2-x1)
            delta_y_avg.append(y2-y1)
            delta_a_avg.append(a2-a1)
    
    # Move to initial position
    arm.set_and_wait_goal_pos(root_pos)

    if len(delta_x_avg) > 0:
        delta_x_avg = sum(delta_x_avg) // len(delta_x_avg)
        delta_y_avg = sum(delta_y_avg) // len(delta_y_avg)
        delta_a_avg = sum(delta_a_avg) // len(delta_a_avg)

    arm._disable_torque()
    return (delta_x_avg, delta_y_avg, delta_a_avg)

def main():
    board = BoardVision(main=False, cam=0, use_yolo=True) #<- change the number around until you connect to the usb camera

    args = parse_arguments()
    arm_config, leader_config = load_robot_settings(args)
    arm, leader = initialize_robots(arm_config, leader_config)

    # Disable torque
    arm._disable_torque()

    if not os.path.exists('deltas.json'):
        with open('deltas.json', 'w') as f:
            json.dump({}, f)
    with open('deltas.json') as f:
        deltas = json.load(f)

    for servo in range(6):
        response = input(f"Press Enter to calibrate servo {servo+1}. Press s to skip a servo. Press q to quit. ")

        if response.lower() == "s":
            continue
        elif response.lower() != "q":
            if servo+1 not in deltas:
                deltas[servo+1] = {}

            dx_pos, dy_pos, da_pos = record_deltas(arm=arm, vision=board, servo=servo, delta=20)
            print(dx_pos, dy_pos, da_pos)

            ans = input("Are you okay with these values? Y/N ")
            if ans.lower() == "y":
                deltas[servo+1]['dx_pos'] = dx_pos
                deltas[servo+1]['dy_pos'] = dy_pos
                deltas[servo+1]['da_pos'] = da_pos
            else:
                pass

            dx_neg, dy_neg, da_neg = record_deltas(arm=arm, vision=board, servo=servo, delta=-20)
            print(dx_neg, dy_neg, da_neg)

            ans = input("Are you okay with these values? Y/N ")
            if ans.lower() == "y":
                deltas[servo+1]['dx_neg'] = dx_neg
                deltas[servo+1]['dy_neg'] = dy_neg
                deltas[servo+1]['da_neg'] = da_neg
            else:
                pass
        else:
            break

    # Dump calibration info
    with open('deltas.json', 'w') as f:
        json.dump(deltas, f, indent=4)

    arm.set_and_wait_goal_pos(arm_config['rest_pos'])
    arm._disable_torque()

if __name__ == "__main__":
    main()
