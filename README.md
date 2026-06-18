# Robotic Manipulation
- [Robotic Manipulation](#robotic-manipulation)
	- [Setup](#setup)
	- [Controlling the robot](#controlling-the-robot)
	- [Recording positions](#recording-positions)
	- [Camera and vision](#camera-and-vision)

## Setup

Clone the repo and create a virtual environment. We use Python 3.14.

```bash
# Create a virtual environment in the project root
python3 -m venv env

# Add the project to the PYTHONPATH in the virtual environment
echo 'export PYTHONPATH="$PYTHONPATH:/absolute/path/to/hs-robotic-manipulation-course"' >> env/bin/activate
# Change this to be your directory path to hs-robotic-manipulation-course
# cd into hs-robotic-manipulation-course, then run pwd to find your path
# Ex: echo 'export PYTHONPATH="$PYTHONPATH:/home/ttic/Desktop/hs-robotic-manipulation-course"' >> env/bin/activate

# To activate the virtual environment, run
source env/bin/activate

# Install the dependencies
# The first time you activate the environment, run
pip install -r requirements.txt

# To deactivate the virtual environment, run
deactivate
```

Alternatively, you can use the `virtual.sh` file to automate many of the above steps:

```
# NEW WAY TO RUN VIRTUAL ENVIRONMENT USING 'virtual.sh'
# virtual.sh is a shell file that will do most of the work for you
# Running './virtual.sh' runs the file, then will prompt you to complete setting up the environment by activating it

# ---Steps---
# On first activation, make the file executable
# In the hs-robotic-manipulation-course path, run:
chmod +x ./virtual.sh

# Run the shell file
./virtual.sh

# Activate the environment
source env/bin/activate

# If it is the first time activating the environment on the device, run:
pip install -r requirements.txt

#Deactivate the virtual environment 
deactivate
```

### Motor setup in Dynamixel Wizard
Install the [Dynamixel 2.0 Wizard](https://docs.robotis.com/docs/software/dynamixel_wizard_2_0/introduction/).

If you are on a new install of Ubuntu, run:

```sudo apt install libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-render-util0```

to install the packages necessary to view the Dynamixel Wizard. Then, run `./DynamixelWizard2Setup-linux-x64.run` in the Downloads folder.

Then, navigate to the directory where Dynamixel Wizard V2 is installed (for Ubuntu, defaults to Home/ROBOTIS). Then, run `./DynamixelWizard2` to open it.

Change the options to scan only IDs 0 to 15 with Protocol 2.0, the USB port where your robot arm is plugged in, and baudrates 57,600 and 1,000,000.

Scan with only one arm at a time.

For the follower arm: Set the IDs from 1 to 6, with 1 being the motor closest to the base and 6 being the final motor for the claw.

For the leader arm: Set the IDs from 7 to 12, with 7 being the motor closest to the base and 12 being the final motor for the claw.

Once you have set up the motor IDs, be sure to close the Dynamixel Wizard, as none of the following Python programs will work while it is open.

## Controlling the robot

First, in `config.json`, modify `device_name` to the USB port name on your PC. This will correspond to one of the same ports that you scanned in the Dynamixel Wizard. For example, mine is `"device_name": "/dev/ttyACM2"`.

Then, `cd` into the `robotics/` directory and run the script: `python position_control.py`.

The script will prompt you to enter a servo ID (which we set 1-6 from base to gripper) and a delta position, which is the amount (in degrees) to move the servo by. Positive and negative values move the servo in opposite directions. **PLEASE USE SMALL VALUES FOR DELTA POSITION WHEN STARTING OUT!** Otherwise, the arm may run into the table and damage itself.

**Note**: In case of emergency (such as smoke or fire), unplug the power source!!!

**Note**: Motor 3 is the 5V motor supporting the most weight. Thus, when rotating that joint up, you need a positive delta of at least 15.

### How values affect the servo positions
|                 | Direction + | Direction - |
|-----------------|-------------|-------------|
| Motor 1 (Base)  | Left +      | Right -     |
| Motor 2 (Base)  | Forward +   | Back -      |
| Motor 3 (Elbow) | Up +        | Down -      |
| Motor 4 (Wrist) | Up +        | Down -      |
| Motor 5 (Wrist) | Right +     | Left -      |
| Motor 6 (Claw)  | Open +      | Cloe -      |

The home position for the follower arm is (2048, 1800, 1850, 1100, 2048, 2048).

The values of each motor are found in the `actions.json` file. Note that the values in `actions.json` are not measured in degrees.

## Recording positions

To prepare the arm for tic-tac-toe gameplay, you will need to record 4 positions per square on the board, which has 15 squares total.

### With `record_positions.py`
In the `robotics/` directory, there is a file named `record_positions.py`. This program is used to record positions for every action.

If you are using the leader arm, you can open this program with `python robotics/record_positions.py -l`. Otherwise, you can run `python robotics/record_positions.py`.

The program will prompt you to record four poses for each square, and existing positions can be skipped by typing “s”.

### With `position_control.py`
In the `robotics/` directory, there is a file named `position_control.py`. This program lets you record and overwrite positions for a specific action.

If you are using the leader arm, you can open this program with `python robotics/position_control.py -l`. Otherwise, you can run `python robotics/position_control.py`.

To record poses for a specific square, type “a” followed by the name of the action you wish to record (A to 8). The program will then prompt you to record all four poses for the chosen square.

You can also modify the values in `actions.json` while this program is open, but be sure to make only small changes to prevent damaging the arm or overloading motors. Note that these values are not measured in degrees.

### Troubleshooting a stuck motor
If a motor stops working, check if it has overloaded. In this case, you will see a red light on the motor and an “OL” error in the Dynamixel app. You can reboot it by opening the Dynamixel Wizard. After it overloads, ensure that none of your poses put too much stress on that motor (for example, make sure the claw is not trying to close all the way when gripping a piece).

Another possibility is that the overloaded motor is tangled in wires. If it is, try unplugging it and rotating it in the other direction to help return it to a more neutral position.

## Camera and Vision

### Using `vision.py`
Use this file to determine which camera ID corresponds to the USB camera. On line 265 of `vision.py`, you can change the integer value of the BoardVision call until the program shows the USB cam output. Then, change the `cam` value on line 10 to match the correct value.

### Using `gamevision.py`
This program lets you play tic-tac-toe against the robotic arm using the poses you defined in the previous steps.

If the `gamevision.py` program stays frozen, it may be using the wrong camera. In this case, redo the setup steps in `vision.py`.
