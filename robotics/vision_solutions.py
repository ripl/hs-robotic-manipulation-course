import cv2
import numpy as np
import threading
import time

class BoardVision:
    """
    Automatically detects the TicTacToe board state using a camera!
    """
    def __init__(self,main=False,cam=0):
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
        self.latest_frame = None
        self.main = main
        self.cap = cv2.VideoCapture(cam) #Tune this number until you get the USB camera!
        if main:
            self.cap_board_state()
        self.camera_thread = threading.Thread(target=self.cap_board_state)
        self.camera_thread.daemon = True
        self.camera_thread.start()


    def get_tile_from_piece(self, px, py, pw, ph):
        """
        TODO: Step 1
        Calculate the tile (0-9) given x, y, w, h of bounding rectangle around the piece.
        px, py: x, y coordinates of the lower-left point of the rectangle
        pw, ph: width and height of rectangle

        Useful to use: self.x, self.y
        """

        #TODO: Part 1: calculate the offset of the center of the piece
        cx = px + pw / 2
        cy = py + ph / 2
        offx = cx - self.x
        offy = cy - self.y
        
        #TODO: Part 2: make sure the detected object is not outside of the board!
        if offx > self.w or offx < 0 or offy > self.h or offy < 0:
            return None
        #print(offx, offy)

        #TODO: Part 3: Calculate the tile based on the board position!
        tilew = self.w / 3
        tileh = self.h / 3
        col = int(offx // tilew)
        row = int(offy // tileh)
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
        
        Each item self.board_state should contain either None to indicate empty, "x", or "o".

        Update each item in self.board_state based on self.board_window!
        """
        prev_board_state = self.board_state.copy()
        for z, b in enumerate(self.board_window):
            if abs(b) > 0.2: #Checks if threshold is met to detect piece, you can play with this value if you want! (This value works well, though.)
                self.board_state[z] = "x" if b > 0 else "o"
            else:
                self.board_state[z] =  None
        if self.board_state != prev_board_state:
            self.confidence = 0
            print("Changed board:", self.board_state)
        self.confidence += 1
        if self.confidence > self.confidence_threshold:
            if self.true_board_state != self.board_state:
                self.true_board_state = self.board_state.copy()
                print("Board state:")
                for row in range(3):
                    print(" | ".join(self.true_board_state[row*3:(row+1)*3]))

    def get_board(self):
        """
        No changes needed!
        """
        while self.confidence < self.confidence_threshold:
            time.sleep(0.05)
        return self.true_board_state
    
    def wait_for_move(self):
        """
        No changes needed!
        """
        prev_truth = self.true_board_state.copy()
        self.old_board_state = prev_truth
        while self.get_board() == prev_truth:
            time.sleep(0.1)
        print("new board status detected!")
        # ret, frame = self.cap.read()
        # if ret:
        #     cv2.imshow("Frame", frame)
        return self.get_board()

    def get_piece_change(self):
        count = 0
        changed = None
        new_piece = None

        for i, piece in enumerate(self.old_board_state):
            if self.true_board_state[i] != piece:
                count += 1
                if count > 1:
                    return None, None
                new_piece = self.true_board_state[i]
                changed = i
        return changed, new_piece
                
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

        lower_blue = np.array([90, 100, 40])
        upper_blue = np.array([150, 255, 255])
        lower_green = np.array([65, 100, 90])
        upper_green = np.array([85, 255, 255])
        while True:
            ret, frame = cap.read()
            #self.latest_frame = frame.copy()
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
            if self.main:
                cv2.imshow("Camera View", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        cap.release()
        cv2.destroyAllWindows()
main=True
board = BoardVision(True)

if not main:
    while True:
        if board.latest_frame is not None:
            print("A")
            cv2.imshow("Camera View", board.latest_frame)

            # Press 'q' to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        board.wait_for_move()

