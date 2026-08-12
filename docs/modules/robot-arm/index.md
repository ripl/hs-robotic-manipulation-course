# Robot Arm Sequence

The robot arm sequence connects Python code to physical hardware. The full course uses the arm to play Tic-Tac-Toe, but teachers can also use these modules as a standalone robotics lab.

## Modules

| Module | Student task | Main concept |
| --- | --- | --- |
| 3D printing and building | Assemble the arm from printed and mechanical parts | Mechanical structure |
| Wiring | Connect motors and controller safely | Power and communication |
| Dynamixel setup | Assign motor IDs and confirm communication | Actuator configuration |
| Position control | Move individual joints and record poses | Calibration |
| Vision | Identify the camera and read board state | Sensing |
| Machine learning object sorting | Train an image classifier and map predictions to actions | Perception and safety-gated action |
| Game integration | Connect game logic, camera state, and robot motion | Closed-loop robotics |

## Hardware Files

The repository includes printable and design files:

- Arm parts: <https://github.com/ripl/hs-robotic-manipulation-course/tree/main/robotics/hardware/arm>
- Leader arm parts: <https://github.com/ripl/hs-robotic-manipulation-course/tree/main/robotics/hardware/leader_arm>
- Camera mount: <https://github.com/ripl/hs-robotic-manipulation-course/tree/main/robotics/hardware/camera>
- Game board and pieces: <https://github.com/ripl/hs-robotic-manipulation-course/tree/main/robotics/hardware/game>

## Safety

Students should begin with small motions and keep clear of the arm while it is powered. If the arm moves unexpectedly, disconnect power before debugging code.

## Source Code

- Robot interface: <https://github.com/ripl/hs-robotic-manipulation-course/tree/main/robotics/robot>
- Position control: <https://github.com/ripl/hs-robotic-manipulation-course/blob/main/robotics/position_control.py>
- Position recording: <https://github.com/ripl/hs-robotic-manipulation-course/blob/main/robotics/record_positions.py>
- Game integration: <https://github.com/ripl/hs-robotic-manipulation-course/tree/main/robotics/game>
