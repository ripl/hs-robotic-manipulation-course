# Vision and Game Integration

This module connects camera input, board-state recognition, game strategy, and robot actions.

## Camera Setup

Use `robotics/vision.py` to identify which camera ID corresponds to the USB camera.

The course notes currently suggest changing the integer used to create `BoardVision` until the USB camera output appears. After identifying the correct camera, use that value consistently in the vision and game-vision scripts.

## Game Vision

If `gamevision.py` freezes or uses the wrong camera, repeat the camera setup process with `vision.py`.

If Pygame font errors appear, reinstall Pygame inside the active environment:

```bash
pip uninstall pygame
pip install pygame --no-cache-dir
```

## Board Calibration

The repository includes board calibration and mapping files:

- <https://github.com/ripl/hs-robotic-manipulation-course/blob/main/robotics/game/calibrate_board_map.py>
- <https://github.com/ripl/hs-robotic-manipulation-course/blob/main/robotics/game/board_position_map.json>

Students should understand that the robot does not know the board automatically. The board map connects camera observations and robot positions to named Tic-Tac-Toe squares.

## Integration Loop

The full robot game follows the same pattern students saw in Python games:

1. Read the current board.
2. Decide whether the game is over.
3. Choose a legal move.
4. Move the robot arm to place a piece.
5. Observe the board again.

## Repository Code

- `smart_game.py`: integrated game flow.
- `smart_player.py`: decision-making player.
- `robot_player.py`: robot-controlled player.
- `gamevision.py`: board vision.
- `game_ui.py`: user interface.

Source folder:

<https://github.com/ripl/hs-robotic-manipulation-course/tree/main/robotics/game>
