# Course Guide

The curriculum is designed to be modular with continuity. Each module has a concrete student artifact, but the artifacts also build toward the final robotic Tic-Tac-Toe system.

## Continuity Thread

The course works best when students repeatedly see the same pattern:

1. Play or inspect a small system.
2. Identify the state, actions, and rules.
3. Write a Python version.
4. Improve the algorithm.
5. Connect the algorithm to graphics, vision, or robot motion.

That thread starts with number guessing and ends with a camera-informed robot action.

## Six-Week Arc

| Phase | Focus | Representative activities |
| --- | --- | --- |
| Week 1 | Lab orientation, setup, Python basics | Introduction to Python, Guess My Number, Pig |
| Week 2 | Game logic and algorithmic thinking | Rock Paper Scissors, Tic-Tac-Toe, Hangman |
| Week 3 | Graphics and interaction | Pygame drawing, Pop the Balloon, Race for the Treasure, Tic-Tac-Toe GUI |
| Week 4 | Hardware build and calibration | 3D-printed arm parts, wiring, Dynamixel Wizard, position recording |
| Week 5 | Vision and decision making | Camera setup, board detection, Teachable Machine object sorting, minimax, robot game player |
| Week 6 | Integration and presentations | Robotic Tic-Tac-Toe, student extensions, final demos |

## Modular Use

Teachers can shorten the course by choosing one coherent path:

| Path | Modules to use | Good for |
| --- | --- | --- |
| Intro Python | Guess My Number, Pig, Rock Paper Scissors | A few class periods of beginner programming. |
| Algorithms through games | Tic-Tac-Toe, Hangman, extensions | Students who know loops and conditionals. |
| Graphics | Pygame basics, Pop the Balloon, Race for the Treasure, Tic-Tac-Toe GUI, Connect Four | Moving from text programs to visual programs and visual strategy games. |
| Robotics lab | Setup, motor control, vision, robot game integration | Students with prior Python experience. |
| Full course | All modules in order | A multi-week internship or summer program. |

## Student Outputs

By the end of the full course, students should have:

- Several playable Python games.
- A graphics-based program using Pygame.
- A working local Python environment and GitHub repository.
- A calibrated robotic arm with recorded board positions.
- A robot-controlled Tic-Tac-Toe demonstration.
- A short explanation of how their system senses, decides, and acts.

## Instructor Notes

The programming modules intentionally begin with unplugged versions of the games. This gives students a shared mental model before they write code.

The robotics modules should be run with explicit hardware safety norms. Students should use small motion increments at first, keep hands clear of the arm during powered motion, and know how to disconnect power quickly.
