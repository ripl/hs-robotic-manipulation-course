import cv2
import numpy as np

# Start webcam
class Board:
    def __init__(self):
        self.x = None
        self.y = None
        self.w = None
        self.h = None
        self.board_window = [0]*9
        self.board_state = [" "]*9
    
    def update_board_cam(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
    
    def process_detected_piece(self, px, py, pw, ph, is_red):
        t = self.get_tile_from_piece(px, py,pw, ph)
        if t is not None:
            if t>=9:
                return
            if is_red:
                self.board_window[t] = self.board_window[t] * 0.9 + 0.1
            else:
                self.board_window[t] = self.board_window[t] * 0.9 -0.1

            self.update_board_state()
    
    def update_board_state(self):
        prev_board_state = self.board_state.copy()
        for z, b in enumerate(self.board_window):
            if abs(b) > 0.2:
                self.board_state[z] = "X" if b > 0 else "O"
            else:
                self.board_state[z] = " "
        if self.board_state != prev_board_state:
            print("Board state:")
            for row in range(3):
                print(" | ".join(self.board_state[row*3:(row+1)*3]))

    
    def get_tile_from_piece(self, px, py, pw, ph):
        cx = px + pw / 2
        cy = py + ph / 2
        offx = cx - self.x
        offy = cy - self.y
        #print("wh",self.w, self.h)
        
        if offx > self.w or offx < 0 or offy > self.h or offy < 0:
            return None
        #print(offx, offy)
        tilew = self.w / 3
        tileh = self.h / 3
        col = int(offx // tilew)
        row = int(offy // tileh)
        tile_index = row * 3 + col
        return tile_index
    



def cap_board_state(board):
    cap = cv2.VideoCapture(4)
    lower_red1 = np.array([0, 100, 100])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([160, 100, 100])
    upper_red2 = np.array([180, 255, 255])

    lower_blue = np.array([100, 150, 50])
    upper_blue = np.array([140, 255, 255])
    lower_green = np.array([65, 100, 90])
    upper_green = np.array([85, 255, 255])
    i = 0
    board_state = [" "]*9
    while True:
        i+=1
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
                board.update_board_cam(x,y,w,h)
                #print(x, y, w, h)
                board_seen = True
        if board_seen:
            contours_red, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours_red:
                area = cv2.contourArea(cnt)
                if area > 500:
                    x, y, w, h = cv2.boundingRect(cnt)
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                    t = board.process_detected_piece(x,y,w,h,True)


            contours_blue, _ = cv2.findContours(blue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours_blue:
                area = cv2.contourArea(cnt)
                if area > 500:
                    x, y, w, h = cv2.boundingRect(cnt)
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                    t = board.process_detected_piece(x,y,w,h,False)
            for n in range(len(board.board_window)):
                board.board_window[n] = board.board_window[n]*0.9
                    #if t: print(t)
                    #else: print("out of bounds")
            if i % 50 == 0:
                prev_board_state = board_state.copy()
                for z, b in enumerate(board_window):
                    if abs(b) > 0.2:
                        board_state[z] = "X" if b > 0 else "O"
                    else:
                        board_state[z] = " "
                if board_state != prev_board_state:
                    print("Board state:")
                    for row in range(3):
                        print(" | ".join(board_state[row*3:(row+1)*3]))

        # Show result
        cv2.imshow("TicTacToe Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    board_window = [0]*9
    board = Board()
    cap_board_state(board)