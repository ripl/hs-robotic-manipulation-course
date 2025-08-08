import cv2
import numpy as np
import threading
import time

class BoardVision:
    """
    Automatically detects the TicTacToe board state using a camera!
    """
    def __init__(self,main=False,cam=4):
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
        if main:
            self.cap_board_state()
        self.camera_thread = threading.Thread(target=self.cap_board_state)
        self.camera_thread.daemon = True
        self.camera_thread.start()



    def get_tile_from_piece(self, px, py, pw, ph):
        """
        TODO: Step 1
        Calculate the tile (0-8) given x, y, w, h of bounding rectangle around the piece.
        px, py: x, y coordinates of the upper-left point of the rectangle
        pw, ph: width and height of rectangle

        Useful to use: self.x, self.y (top left corner of TicTacToe board)
        """

        #TODO: Part 1: calculate the offset of the center of the piece from the bottom left corner of board
        #Replace with your code:

        center_piece_x = px + pw/2
        center_piece_y = py + ph/2

        offx = center_piece_x-self.x #replace
        offy = center_piece_y-self.y #replace
        
        #Makes sure the detected object is not outside of the board! No need to touch this.
        if offx > self.w or offx < 0 or offy > self.h or offy < 0:
            return None

        #TODO: Part 2: Calculate width and height of 1 tile!
        #Replace with your code:
        #Use self.w and self.h!
        tilew = self.w/3
        tileh = self.h/3

        #TODO: Part 3: Calculate the column and row of the piece, using tilew, tileh, offx, offy!
        #Replace with your code:
        col = int(offx // tilew)
        row = int(offy // tileh)

        #Returns tile index based on row and column
        tile_index = row * 3 + col
        return tile_index
    
    
    def update_board_state(self):
        """
        TODO: Step 2
        Updates the board state list according to camera measurements.

        self.board_state : List containing the state of each tile (0-8)
        self.board_window: List containing the measurements of each tile (0-8)

        Instructions:
        Loop through self.board_window, which includes the measurements for every tile.
        For each tile in self.board_window, if the value is less than -0.2, we detect a blue piece.
        For each tile in self.board_window, if the value is greater than 0.2, we detect a red piece.
        
        Each item self.board_state should contain either None to indicate empty, "x", or "o".

        Update each item in self.board_state based on self.board_window!
        """
        prev_board_state = self.board_state.copy()
        #YOUR CODE GOES HERE!
        for i in range(9):
            if self.board_window[i]>=0.2:
                self.board_state[i] = 'x'
            elif self.board_window[i]<-0.2:
                self.board_state[i] = 'o'
            else:
                self.board_state[i] = None
        #print(self.board_state)
        # for each item in self.board_window, update self.board_state accordingly.

        #Ignore code down here
        if self.board_state != prev_board_state:
            self.confidence = 0
            #print("Changed board:", self.board_state)
        self.confidence += 0.75
        if self.confidence > self.confidence_threshold:
            if self.true_board_state != self.board_state:
                self.true_board_state = self.board_state.copy()
                print("Board state:")
                for row in range(3):
                    print(" | ".join(" " if x is None else x for x in self.true_board_state[row*3:(row+1)*3]))

    def get_piece_change(self):
        """
        Compare old board and new board, and return the tile index
        and status of new piece.

        If more than one piece has changed, then the human probably messed  up.
        Keep track of count (the number of tiles changed), and if its >1 return None.

        new board: self.true_board_state
        """
        old_board = self.old_board_state
        count = 0 #should be == 1
        changed_tile = None #0-8
        new_piece = None #'x' or 'o'

        for i in range(9):
            if old_board[i] != self.true_board_state[i]:
                count+=1
                changed_tile = i
                new_piece = self.true_board_state[i] 
            
        if count!=1:
            changed_tile = None
            new_piece = None
        return changed_tile, new_piece
    

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
        return self.get_board()


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
        lower_red1 = np.array([0, 70, 50])
        upper_red1 = np.array([15, 255, 255])
        lower_red2 = np.array([160, 0, 0])
        upper_red2 = np.array([180, 255, 255])
        lower_blue = np.array([80, 100, 80])
        upper_blue = np.array([120, 255, 255])
        lower_green = np.array([40, 100, 90])
        upper_green = np.array([90, 255, 255])

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if ret:
                height, width = frame.shape[:2]

                # Calculate cropping coordinates for 50% zoom
                center_x, center_y = width // 2, height // 2
                new_width, new_height = int(width / 2), int(height / 2)

                x1 = center_x - new_width // 2
                y1 = center_y - new_height // 2
                x2 = center_x + new_width // 2
                y2 = center_y + new_height // 2

                # Crop and resize
                zoomed_frame = frame[y1:y2, x1:x2]
                frame = cv2.resize(zoomed_frame, (width, height))
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


if __name__ == "__main__":
    main=True
    board = BoardVision(True, 0) #<- change the number around until you connect to the usb camera

    if not main:
        while True:
            if board.latest_frame is not None:
                print("A")
                cv2.imshow("Camera View", board.latest_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            board.wait_for_move()
