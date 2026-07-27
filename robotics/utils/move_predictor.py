import sys, os, json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
from vision import BoardVision
from pathlib import Path
import time

GRAB_SPOT = [1080, 195, 30000]

def clamp(val, min, max):
    if val < min:
        val = min
    if val > max:
        val = max

    return val

def imagine_pos(current_pos, desired_pos, deltas):
    best_move = 0
    best_norm = 10000000

    desired_pos[0] = clamp(current_pos[0], 840, 1100)
    desired_pos[2] = clamp(current_pos[2], 20000, 30000)

    print("----------------")
    for move,effects in deltas.items():
        new_pos = np.array(current_pos)

        new_pos[0] += effects['dx']
        new_pos[1] += effects['dy']
        new_pos[2] += effects['da']

        norm = np.linalg.norm(new_pos - desired_pos)

        if norm < best_norm:
            best_norm = norm
            best_move = move

        print(f"Norm of {move} is:", norm)

    print()
    print(f"BEST MOVE: {best_move}")
    print("----------------")
    print()

    return best_move


file_path = Path(__file__).resolve()
utils = file_path.parent
robotics = file_path.parents[1]

with open(utils / "deltas.json") as f:
    board = BoardVision(main=False, cam=0, use_yolo=True,
        weights_path=str(robotics / "handle_model.pt"))

    print(board)

    deltas = json.load(f)

    while True:
        current_pos = list(board.get_handle_info())

        time.sleep(1.0)

        if all(x != -1 for x in current_pos):
            if len(current_pos) > 0:
                best_move = imagine_pos(current_pos, GRAB_SPOT.copy(), deltas)
