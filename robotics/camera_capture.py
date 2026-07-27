import sys, os, time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import cv2
import numpy as np
import threading
import time
import argparse
import sys

"""
camera_capture is used to take photos from the USB camera, which can be used as data
for machine learning models.
When running with no flags, press the 'c' key to manually take a screenshot.
Press 'q' with the window in focus to close the program.
You may need to adjust the camera value on line 108.
If you do not want this program to overwrite existing files, make sure to change
the screenshot count on line 44.

Flags:
    -t: If this flag is included, the program will take a screenshot every 0.5 seconds.
        This flag will also disable the ability to manually take photos.
"""

class BoardVision:
    """
    Automatically detects the TicTacToe board state using a camera!
    """
    def __init__(self, main=False, cam=4, use_timer=False):
        """
        No need to change anything!
        """
        self.x = None
        self.y = None
        self.w = None
        self.h = None
        self.board_window = [0]*9
        self.board_state = [None]*9
        self.old_board_state = None
        self.true_board_state = self.board_state.copy()
        self.confidence = 0
        self.confidence_threshold = 100
        self.main = main
        self.cap = cv2.VideoCapture(cam) #Tune this number until you get the USB camera!

        # Screenshot settings
        self.use_timer = use_timer
        self.screenshot_interval = 0.5  # seconds, only used if use_timer is True
        self.screenshot_count = 0
        self.last_screenshot_time = 0

        self.camera_thread = None
        if self.main:
            # GUI calls (imshow/waitKey) must happen on the main thread on macOS,
            # so run the loop directly here instead of in a background thread.
            self.cap_board_state()
        else:
            # No GUI involved, so it's safe to run this in a background thread.
            self.camera_thread = threading.Thread(target=self.cap_board_state)
            self.camera_thread.daemon = True
            self.camera_thread.start()

    def get_cap(self):
        return self.cap

    def update_board_cam(self, x, y, w, h):
        """
        No changes needed!
        """
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def take_screenshot(self, frame):
        filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"captures/data-{self.screenshot_count}.jpg")
        cv2.imwrite(filename, frame)
        print(f"Saved {filename}")
        self.screenshot_count += 1

    def cap_board_state(self):
        """
        Don't need to change anything here!
        """
        cap = self.cap

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if self.use_timer:
                # Take a screenshot every self.screenshot_interval seconds
                current_time = time.time()
                if current_time - self.last_screenshot_time >= self.screenshot_interval:
                    self.take_screenshot(frame)
                    self.last_screenshot_time = current_time

            if self.main:
                cv2.imshow("Camera View", frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                if not self.use_timer and key == ord('c'):
                    self.take_screenshot(frame)

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TicTacToe BoardVision camera capture")
    parser.add_argument("-t", action="store_true", help="Automatically take a screenshot every 0.5 seconds instead of capturing on keypress")
    args = parser.parse_args()

    board = BoardVision(True, 4, use_timer=args.t) #<- change the number around until you connect to the usb camera
