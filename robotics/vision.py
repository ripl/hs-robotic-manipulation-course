import cv2
import numpy as np
import threading
import time
from ultralytics import YOLO

class BoardVision:
    """
    Automatically detects the TicTacToe board state using a camera!
    """
    def __init__(self,main=False,cam=4,use_yolo=False, weights_path="handle_model.pt"):
        """
        No need to change anything!
        """
        self.x = None
        self.y = None
        self.w = None
        self.h = None
        self.board_window = [0]*9
        self.board_state = [None]*9
        self.old_board_state = [None]*9
        self.true_board_state = self.board_state.copy()
        self.confidence = 0
        self.confidence_threshold = 100
        self.main = main
        self.cap = cv2.VideoCapture(cam) #Tune this number until you get the USB camera!

        # Load YOLO model
        self.use_yolo = use_yolo

        if use_yolo:
            self.frame_count = 0
            self.last_predictions = []
            self.model = YOLO(weights_path)
            self.infer_every_n = 3
            self.last_predictions_clean = []

        if main:
            self.cap_board_state()
        self.camera_thread = threading.Thread(target=self.cap_board_state)
        self.camera_thread.daemon = True
        self.camera_thread.start()

    def apply_nms(self, predictions, iou_threshold=0.5):
        """
        Applies Non-Maximum Suppression (NMS) to a list of bounding box predictions.
        
        Tuple format per item: (x1, y1, x2, y2, label, conf)
        """
        if not predictions:
            return []

        # 1. Sort predictions by confidence score in descending order
        # Highest confidence boxes come first
        sorted_preds = sorted(predictions, key=lambda item: item[5], reverse=True)
        
        keep_boxes = []

        while sorted_preds:
            # Pick the box with the highest confidence
            current = sorted_preds.pop(0)
            keep_boxes.append(current)
            
            c_x1, c_y1, c_x2, c_y2, c_label, c_conf = current
            c_area = (c_x2 - c_x1) * (c_y2 - c_y1)
            
            filtered_preds = []
            for next_box in sorted_preds:
                n_x1, n_y1, n_x2, n_y2, n_label, n_conf = next_box

                # Calculate coordinates of the intersection rectangle
                inter_x1 = max(c_x1, n_x1)
                inter_y1 = max(c_y1, n_y1)
                inter_x2 = min(c_x2, n_x2)
                inter_y2 = min(c_y2, n_y2)

                # Compute width and height of intersection box
                inter_w = max(0, inter_x2 - inter_x1)
                inter_h = max(0, inter_y2 - inter_y1)
                inter_area = inter_w * inter_h

                # If there is no overlap, keep the box
                if inter_area == 0:
                    filtered_preds.append(next_box)
                    continue

                # Compute IoU (Intersection over Union)
                n_area = (n_x2 - n_x1) * (n_y2 - n_y1)
                union_area = c_area + n_area - inter_area
                iou = inter_area / union_area if union_area > 0 else 0

                # If IoU is below the threshold, keep the lower-confidence box.
                # If IoU >= threshold, it gets dropped (suppression).
                if iou < iou_threshold:
                    filtered_preds.append(next_box)

            # Update remaining list with non-suppressed boxes
            sorted_preds = filtered_preds

        return keep_boxes

    def get_handle_info(self):
        x = -1
        y = -1
        area = -1

        max_conf = 0

        for x1, y1, x2, y2, label, conf in self.last_predictions_clean:
            box_area = (x2 - x1) * (y2 - y1)

            if conf > max_conf and box_area > 13000:
                max_conf = conf

                x = (x1 + x2) // 2
                y = (y1 + y2) // 2
                area = box_area
        
        return (x, y, area)

    def reset_vision(self):
        """
        Resets the internal vision board state baseline to empty.
        """
        self.board_window = [0]*9
        self.board_state = [None]*9
        self.old_board_state = [None]*9
        self.true_board_state = [None]*9
        self.confidence = self.confidence_threshold


        max_conf = 0

        for x1, y1, x2, y2, label, conf in self.last_predictions_clean:
            box_area = (x2 - x1) * (y2 - y1)

            if conf > max_conf and box_area > 13000:
                max_conf = conf

                x = (x1 + x2) // 2
                y = (y1 + y2) // 2
                area = box_area
        
        return (x, y, area)

    def draw_model_predictions(self, frame):
        """
        Draw the cached predictions on every frame; only run YOLO
        (and refresh the cache) every self.infer_every_n frames.
        """

        if self.frame_count % self.infer_every_n == 0:
            results = self.model.predict(frame, conf=0.25, verbose=False)[0]
            self.last_predictions = [
                (*map(int, box.tolist()), self.model.names[int(cls)], float(conf))
                for box, cls, conf in zip(results.boxes.xyxy, results.boxes.cls, results.boxes.conf)
            ]
            self.last_predictions_clean = self.apply_nms(self.last_predictions)

        cv2.circle(img=frame, center=(1080, 195), radius=15, color=(255,255,255))

        for x1, y1, x2, y2, label, conf in self.last_predictions_clean:
            pos_x = (x1 + x2) // 2
            pos_y = (y1 + y2) // 2
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)

            area = (x2-x1) * (y2-y1)

            cv2.putText(frame, f"{label} {conf:.2f}, Pos: ({pos_x}, {pos_y}), Area: {area}", (x1, max(y1 - 8, 0)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
            
        return frame

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
                    if row < 2:
                        print("-" * 9)

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
    
    def get_cap(self):
        return self.cap

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
        Smooths board position across frames using exponential moving average (low-pass filter).
        """
        if self.x is None:
            self.x, self.y, self.w, self.h = x, y, w, h
        else:
            alpha = 0.25  # Smooth out frame-to-frame jitter
            self.x = self.x * (1 - alpha) + x * alpha
            self.y = self.y * (1 - alpha) + y * alpha
            self.w = self.w * (1 - alpha) + w * alpha
            self.h = self.h * (1 - alpha) + h * alpha
    
    
    def cap_board_state(self):
        """
        Don't need to change anything here!
        """
        cap = self.cap
        lower_red1 = np.array([0, 70, 50])
        upper_red1 = np.array([15, 255, 255])
        lower_red2 = np.array([160, 0, 0])
        upper_red2 = np.array([180, 255, 255])
        lower_blue = np.array([100, 170, 80])
        upper_blue = np.array([120, 255, 255])

        lower_blue_close = np.array([111, 197, 70])
        upper_blue_close = np.array([120, 215, 90])

        lower_green = np.array([40, 100, 90])
        upper_green = np.array([90, 255, 255])

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if self.use_yolo:
                self.frame_count += 1
                annotated_frame = self.draw_model_predictions(frame)   # always called; internally decides whether to re-infer

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
                #frame = cv2.resize(zoomed_frame, (width, height))
            board_seen = False
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            red_mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
            red_mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
            red_mask = cv2.bitwise_or(red_mask1, red_mask2)

            blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)   
            blue_mask_close = cv2.inRange(hsv, lower_blue_close, upper_blue_close)     
            green_mask = cv2.inRange(hsv, lower_green, upper_green)

            contours_green, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            valid_green = [cnt for cnt in contours_green if cv2.contourArea(cnt) > 100]
            if valid_green:
                all_pts = np.vstack(valid_green)
                x_min = float(np.min(all_pts[:, 0, 0]))
                x_max = float(np.max(all_pts[:, 0, 0]))
                y_min = float(np.min(all_pts[:, 0, 1]))
                y_max = float(np.max(all_pts[:, 0, 1]))

                w = x_max - x_min
                # Ensure y_max is at least y_min + w so pieces on bottom row don't block green and pull y_max upward
                y_max = max(y_max, y_min + w)
                h = max(y_max - y_min, w)
                w = h  # Force square geometry

                x = x_min
                y = y_min

                if w > 50 and h > 50:
                    cv2.rectangle(frame, (int(x), int(y)), (int(x + w), int(y + h)), (0, 255, 0), 2)
                    self.update_board_cam(x, y, w, h)
                    board_seen = True

            if board_seen and self.x is not None and self.w is not None and self.h is not None:
                def is_inside_board(px, py, pw, ph):
                    cx = px + pw / 2.0
                    cy = py + ph / 2.0
                    return (self.x <= cx <= self.x + self.w) and (self.y <= cy <= self.y + self.h)

                contours_red, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                for cnt in contours_red:
                    area = cv2.contourArea(cnt)
                    if area > 800:
                        x, y, w, h = cv2.boundingRect(cnt)
                        if is_inside_board(x, y, w, h):
                            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                            self.process_detected_piece(x, y, w, h, True)

                contours_blue, _ = cv2.findContours(blue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                for cnt in contours_blue:
                    area = cv2.contourArea(cnt)
                    if area > 800:
                        x, y, w, h = cv2.boundingRect(cnt)
                        if is_inside_board(x, y, w, h):
                            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                            self.process_detected_piece(x, y, w, h, False)
                for n in range(len(self.board_window)):
                    self.board_window[n] = self.board_window[n]*0.9
                self.update_board_state()
            if self.main:
                cv2.imshow("Camera View", annotated_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                if cv2.waitKey(1) & 0xFF == ord('c'):
                    self.print_handle_info()
                if cv2.waitKey(1) & 0xFF == ord('b'):
                    print()
                    
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main=True
    board = BoardVision(main=True, cam=4, use_yolo=False) #<- change the number around until you connect to the usb camera

    if not main:
        while True:
            if board.latest_frame is not None:
                print("A")
                cv2.imshow("Camera View", board.latest_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            board.wait_for_move()
