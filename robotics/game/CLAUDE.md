# robotics/game — Vision-driven TicTacToe (gamevision.py)

`gamevision.py` runs a pygame UI for physical TicTacToe: a human plays real pieces on a board, a camera (`BoardVision`) detects each move, and a robotic arm (`SmartArm`) answers by moving its own pieces.

## Running

```bash
python robotics/game/gamevision.py [--size 750] [--cam 4]
```

- `--size`: window height in px. The window width is `size - size//6`.
- `--cam`: OpenCV camera index passed to `BoardVision(False, cam, use_yolo=False)`.
- The arm must be connected. `SmartArm` → `Arm.__init__` opens the serial device in `robotics/config.json` (`arm.device_name`) and moves to `home_pos` as soon as the player is created, which happens in the setup menu.
- `players.py` imports `robotics.robot.robot` and `robotics.utils.track_piece`, so the repo root has to be importable (run from the repo root with `PYTHONPATH=.`). The script itself only adds `robotics/` to `sys.path`.

## Dependencies (local modules)

| Import | From | Used for |
|---|---|---|
| `TicTacToe` | `game.py` | Board state, turns, win/draw, `reset()`, `place_piece()`, `smart_place_piece()` |
| `Player`, `Arm`, `SmartArm` | `players.py` | Human and robot players. `SmartArm(piece, lvl)` picks `novice`/`pro`/`expert` |
| `BoardVision` | `../vision.py` | `wait_for_move()`, `get_piece_change() -> (tile, piece)`, `reset_vision()` |
| piece images | `images/` | `x_piece.png`/`o_piece.png`, falling back to `x.png`/`o.png` |

Config files: `robotics/config.json` (the `arm` section: servo ids, gains, limits, `home_pos`, `rest_pos`) and `robotics/actions.json` (stored arm positions). `Arm` resolves both relative to `players.py`.

## Program flow

1. `__main__` creates a **module-global** `vision` and then `TicTacToeUI(size)`, and calls `ui.run()`.
2. `run()` → `show_setup_menu()`:
   - Difficulty: 0 Novice, 1 Pro, 2 Expert (the default; Enter picks it).
   - Who starts: Human or Smart Arm. Whoever starts is always `'x'`.
   - Resets `Player.player_count = 0` and builds `TicTacToe(p1, p2, auto_start=False)`.
3. If the arm starts on an empty board, it moves once right after the window opens.
4. Main loop, one turn at a time:
   - Redraw, then check win/draw → `handle_game_over()`.
   - Block on `vision.wait_for_move()` / `get_piece_change()` until a tile 0–8 shows the **human's** piece.
   - `game.place_piece(tile)`, redraw, then `smart_update()` (the arm plays) unless the game ended.
5. `handle_game_over()`: Restart (R/Enter) calls `game.reset()` (the arm clears its pieces), re-runs the setup menu and `vision.reset_vision()`. Quit (Q/Esc) calls `quit_game()`.
6. `quit_game()` closes pygame, sends the arm to `arm_config['rest_pos']`, disables torque and calls `sys.exit(0)`. Window close, Q or Esc trigger it from any screen.

## UI layout (`TicTacToeUI`)

- **Main 3×3 board** (bottom-left, `self.board`): cells indexed 0–8 row-major, matching `TicTacToe.board` and vision tile ids.
- **TTIC logo** (2×2, `self.ttic_board`): decoration only.
- **Arm piece supply** (top-right 3×2, `self.pieces_board`, labels A–F): shows the arm's remaining pieces from `arm.pieces` (starts as `A`–`E`).
- **Status card** (top-left): current turn, victory or tie. Red = `'x'`, blue = `'o'`.
- `draw_button()` handles hover styling and drops to the small font when the text is too wide.
- `arm_player` / `human_player` properties pick out the `Arm` vs non-`Arm` player from `p1`/`p2`.

## Gotchas

- **`vision` is a global, not an attribute.** `run()` uses the module-level `vision` that `__main__` defines, and `handle_game_over()` looks it up through `globals()`. Importing `TicTacToeUI` from another module will fail with a `NameError` unless you set `gamevision.vision` first. Prefer passing it in (e.g. `self.vision`) if you refactor.
- **`update(pos)` is dead code here**: its mouse hit-testing assumes a hard-coded 750×1500 layout and nothing in this file calls it. Moves only come from vision.
- **Piece images are reloaded from disk on every frame** in `draw_current_board()`. Cache them in `__init__` if performance matters.
- `Player.__new__` refuses to create more than 2 players. `show_setup_menu()` resets `Player.player_count` before creating new ones, so keep that reset if you touch the restart logic.
- The status card always calls the arm "Smart Arm" (`isinstance(..., Arm)`). The game-over screen says "Player 1/2" instead.
- The restart path is duplicated for mouse and keyboard in `handle_game_over()`. Change both, or factor it out.
- A tile index > 8 from `get_piece_change()` (the off-board supply area) is ignored, and so is a detected change with the arm's piece.

## Related files in this directory

- `game.py`: `TicTacToe` logic. `game_ui.py`: mouse-driven UI without vision.
- `players.py`: player classes and AI levels (`minimax.py` for search).
- `smart_game.py` / `smart_player.py` / `robot_player.py`: other game modes.
