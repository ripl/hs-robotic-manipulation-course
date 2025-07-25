import cv2
import numpy as np
import threading
import time

class BoardVision:
    """
    Automatically detects the TicTacToe board state using a camera!
    """
    def __init__(self):
        """
        No need to change anything!
        """
        self.x = None
        self.y = None
        self.w = None
        self.h = None
        self.board_window = [0]*9
        self.board_state = [" "]*9

        self.cap = cv2.VideoCapture(1) #Tune this number until you get the USB camera!

        self.camera_thread = threading.Thread(target=self.cap_board_state)
        self.camera_thread.daemon = True
        self.camera_thread.start()


    def get_tile_from_piece(self, px, py, pw, ph):
        """
        TODO: Step 1
        Calculate the tile (0-9) given x, y, w, h of bounding rectangle around the piece.
        px, py: x, y coordinates of the lower-left point of the rectangle
        pw, ph: width and height of rectangle

        Useful to use: self.x, self.y (bottom left corner of TicTacToe board)
        """

        #TODO: Part 1: calculate the offset of the center of the piece from the bottom left corner of board
        #Replace with your code:
        offx = None
        offy = None
        
        #Makes sure the detected object is not outside of the board!
        if offx > self.w or offx < 0 or offy > self.h or offy < 0:
            return None

        #TODO: Part 2: Calculate width and height of 1 tile!
        #Replace with your code:
        tilew = None
        tileh = None

        #TODO: Part 3: Calculate the column and row of the piece, using tilew, tileh, offx, offy!
        #Replace with your code:
        col = None
        row = None

        #Returns tile index based on row and column
        tile_index = row * 3 + col
        return tile_index
    
    
    def update_board_state(self):
        """
        TODO: Step 2
        Updates the board state list according to camera measurements.

        self.board_state : List containing the state of each tile (0-9)
        self.board_window: List containing the measurements of each tile (0-9)

        Instructions:
        Loop through self.board_window, which includes the measurements for every tile.
        For each tile in self.board_window, if the value is less than -0.2, we detect a blue piece.
        For each tile in self.board_window, if the value is greater than 0.2, we detect a red piece.
        
        Each item self.board_state should contain either " " to indicate empty, "X", or "O".

        Update each item in self.board_state based on self.board_window!
        """
        prev_board_state = self.board_state.copy()
        #TODO: Part 1: Update self.board_state based on self.board_window. (Use instructions above)

        #Your code goes here!

        #TODO: Part 2: Print out board state
        if self.board_state != prev_board_state:
            print("Board state:")
            #Your code goes here!

    def get_board(self):
        """
        No changes needed!
        """
        return self.board_state


    def process_detected_piece(self, px, py, pw, ph, is_red):
        """
        No changes needed!
        """
        t = self.get_tile_from_piece(px, py,pw, ph)
        if t is not None:
            if t>=9:
                return
            if is_red:
                self.board_window[t] = self.board_window[t] * 0.9 + 0.1
            else:
                self.board_window[t] = self.board_window[t] * 0.9 -0.1

            self.update_board_state()


    def update_board_cam(self, x, y, w, h):
        """
        No changes needed!
        """
        self.x = x
        self.y = y
        self.w = w
        self.h = h
    
    
    def cap_board_state(self):
        """
        Don't need to change anything here!
        """
        cap = self.cap
        lower_red1 = np.array([0, 100, 100])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([160, 100, 100])
        upper_red2 = np.array([180, 255, 255])

        lower_blue = np.array([100, 150, 50])
        upper_blue = np.array([140, 255, 255])
        lower_green = np.array([65, 100, 90])
        upper_green = np.array([85, 255, 255])
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            board_seen = False
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            red_mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
            red_mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
            red_mask = cv2.bitwise_or(red_mask1, red_mask2)

            blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)        
            green_mask = cv2.inRange(hsv, lower_green, upper_green)

            contours_green, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours_green:
                area = cv2.contourArea(cnt)
                if area > 500:
                    x, y, w, h = cv2.boundingRect(cnt)
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    self.update_board_cam(x,y,w,h)
                    board_seen = True
            if board_seen:
                contours_red, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                for cnt in contours_red:
                    area = cv2.contourArea(cnt)
                    if area > 500:
                        x, y, w, h = cv2.boundingRect(cnt)
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                        self.process_detected_piece(x,y,w,h,True)

                contours_blue, _ = cv2.findContours(blue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                for cnt in contours_blue:
                    area = cv2.contourArea(cnt)
                    if area > 500:
                        x, y, w, h = cv2.boundingRect(cnt)
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                        self.process_detected_piece(x,y,w,h,False)
                for n in range(len(self.board_window)):
                    self.board_window[n] = self.board_window[n]*0.9
        cap.release()
        cv2.destroyAllWindows()

board = BoardVision()
while True:
    time.sleep(1)

