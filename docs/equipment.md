# Equipment

These parts build one follower arm and one leader arm. The arm designs are adapted from [Alexander Koch's low-cost robot arm designs](https://github.com/AlexanderKoch-Koch/low_cost_robot).

The course code and hardware source files live in the course repository at <https://github.com/ripl/hs-robotic-manipulation-course>.

## Follower Arm

### Electronics

| Part | Quantity | Link |
| --- | --- | --- |
| Dynamixel XL430-W250-T Servo | 2 | [Robotis](https://www.robotis.us/dynamixel-xl430-w250-t/) |
| Dynamixel XL330-M288 Servo | 4 | [Robotis](https://www.robotis.us/dynamixel-xl330-m288-t/) |
| XL430 Idler Wheel | 1 | [Robotis](https://www.robotis.us/hn11-i101-set/) |
| XL330 Idler Wheel | 3 | [Robotis](https://www.robotis.us/fpx330-h101-4pcs-set/) (sold in 4-packs) |
| Waveshare Serial Bus Servo Driver Board | 1 | [Waveshare](https://www.waveshare.com/bus-servo-adapter-a.htm) |
| Waveshare 5MP USB Camera | 1 | [Waveshare](https://www.waveshare.com/IMX335-5MP-USB-Camera-B.htm) |
| Voltage Reducer | 1 | [Amazon](https://a.co/d/1TjkOB6) (sold in 4-packs) |
| 12V Power Supply | 1 | [Amazon](https://a.co/d/40o8uMN) |
| USB-C Cable | 1 | [Amazon](https://a.co/d/gMLkyVl) (sold in 2-packs) |

### Hardware and Miscellaneous

| Part | Quantity | Link |
| --- | --- | --- |
| Table Clamp | 1 | [Amazon](https://a.co/d/4KEiYdV) |
| Nylon Screws and Nuts | a few | [Amazon](https://a.co/d/f66xfhL) (100-pack) |
| M2 x 8 mm Phillips Machine Screws | a few | [Amazon](https://a.co/d/4WAUIEz) (100-pack) |
| Dupont Wires, female to male | a few | [Amazon](https://a.co/d/68xGPk6) |
| Rubber Sheet for gripper | 1 | [Amazon](https://a.co/d/0gCGdtl) |
| Velcro Cable Ties | a few | [Amazon](https://a.co/d/jikpAGs) (150-pack) |

### 3D Printed Parts

STL files are in [`robotics/hardware/arm`](https://github.com/ripl/hs-robotic-manipulation-course/tree/main/robotics/hardware/arm).

| Part | Quantity |
| --- | --- |
| [base.stl](https://github.com/ripl/hs-robotic-manipulation-course/blob/main/robotics/hardware/arm/base.stl) | 1 |
| [shoulder_rotation.stl](https://github.com/ripl/hs-robotic-manipulation-course/blob/main/robotics/hardware/arm/shoulder_rotation.stl) | 1 |
| [shoulder_to_elbow.stl](https://github.com/ripl/hs-robotic-manipulation-course/blob/main/robotics/hardware/arm/shoulder_to_elbow.stl) | 1 |
| [elbow_to_wrist.stl](https://github.com/ripl/hs-robotic-manipulation-course/blob/main/robotics/hardware/arm/elbow_to_wrist.stl) | 1 |
| [elbow_to_wrist_extension.stl](https://github.com/ripl/hs-robotic-manipulation-course/blob/main/robotics/hardware/arm/elbow_to_wrist_extension.stl) | 1 |
| [gripper_static_part.stl](https://github.com/ripl/hs-robotic-manipulation-course/blob/main/robotics/hardware/arm/gripper_static_part.stl) | 1 |
| [gripper_moving_part.stl](https://github.com/ripl/hs-robotic-manipulation-course/blob/main/robotics/hardware/arm/gripper_moving_part.stl) | 1 |

## Leader Arm

### Electronics

| Part | Quantity | Link |
| --- | --- | --- |
| Dynamixel XL330-M077 Servo | 6 | [Robotis](https://www.robotis.us/dynamixel-xl330-m077-t/) |
| XL330 Frame | 1 | [Robotis](https://www.robotis.us/fpx330-s101-4pcs-set/) (sold in 4-packs) |
| XL330 Idler Wheel | 3 | [Robotis](https://www.robotis.us/fpx330-h101-4pcs-set/) (sold in 4-packs) |
| Waveshare Serial Bus Servo Driver Board | 1 | [Waveshare](https://www.waveshare.com/bus-servo-adapter-a.htm) |
| 5V Power Supply | 1 | [Amazon](https://a.co/d/5u90NVp) |
| Dupont Wires, female to male | a few | [Amazon](https://a.co/d/68xGPk6) |

### Hardware

| Part | Quantity | Link |
| --- | --- | --- |
| Table Clamp | 1 | [Amazon](https://a.co/d/0dzNNFsq) (sold in 8-packs) |

### 3D Printed Parts

STL files are in [`robotics/hardware/leader_arm`](https://github.com/ripl/hs-robotic-manipulation-course/tree/main/robotics/hardware/leader_arm).

| Part | Quantity |
| --- | --- |
| [base.stl](https://github.com/ripl/hs-robotic-manipulation-course/blob/main/robotics/hardware/leader_arm/base.stl) | 1 |
| [shoulder_to_elbow.stl](https://github.com/ripl/hs-robotic-manipulation-course/blob/main/robotics/hardware/leader_arm/shoulder_to_elbow.stl) | 1 |
| [elbow_to_wrist.stl](https://github.com/ripl/hs-robotic-manipulation-course/blob/main/robotics/hardware/leader_arm/elbow_to_wrist.stl) | 1 |
| [elbow_to_wrist_extension.stl](https://github.com/ripl/hs-robotic-manipulation-course/blob/main/robotics/hardware/leader_arm/elbow_to_wrist_extension.stl) | 1 |
| [gripper_handle.stl](https://github.com/ripl/hs-robotic-manipulation-course/blob/main/robotics/hardware/leader_arm/gripper_handle.stl) | 1 |
| [gripper_trigger.stl](https://github.com/ripl/hs-robotic-manipulation-course/blob/main/robotics/hardware/leader_arm/gripper_trigger.stl) | 1 |
| [leader_arm.stl](https://github.com/ripl/hs-robotic-manipulation-course/blob/main/robotics/hardware/leader_arm/leader_arm.stl) | 1 |
| [leader_base_electronics_holder.stl](https://github.com/ripl/hs-robotic-manipulation-course/blob/main/robotics/hardware/leader_arm/leader_base_electronics_holder.stl) | 1 |
