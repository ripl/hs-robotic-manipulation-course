# Robotic Manipulation

- [Robotic Manipulation](#robotic-manipulation)
  - [Setup](#setup)
  - [Controlling the robot](#controlling-the-robot)

## Setup

Clone the repo and create a virtual environment. We use Python 3.10.12.

```bash
# Create a virtual environment in the project root
python3 -m venv env

# Add the project to the PYTHONPATH in the virtual environment
echo 'export PYTHONPATH="$PYTHONPATH:/home/school/Desktop/hs-robotic-manipulation-course"' >> env/bin/activate


# Activate the virtual environment
source env/bin/activate

# Install the dependencies
pip install -r requirements.txt

# To deactivate the virtual environment
deactivate
```

## Controlling the robot

First, in `config.json`, modify `device_name` to the USB port name on your PC. For example, mine is `"device_name": "/dev/ttyACM2"`.

Then, `cd` into the `robotics/` directory and run the script: `python position_control.py`.

The script will prompt you to enter a servo ID (which we set 1-6 from base to gripper) and a delta position, which is the amount (in degrees) to move the servo by. Positive and negative values move the servo in opposite directions. **PLEASE USE SMALL VALUES FOR DELTA POSITION WHEN STARTING OUT!** Otherwise, the arm may run into the table and damage itself.

**Note**: in case of emergency, unplug the power source!!!

**Note**: motor 3 is the 5V motor supporting the most weight. Thus, when rotating that joint up, you need a positive delta of at least 15.
