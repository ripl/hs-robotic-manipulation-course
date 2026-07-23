import sys, os, time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pygame
from game import TicTacToe
from players import Player, Arm, SmartArm
from vision import BoardVision

def load_piece_image(primary_name, fallback_name, scale_size):
    img_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
    primary_path = os.path.join(img_dir, primary_name)
    fallback_path = os.path.join(img_dir, fallback_name)
    path = primary_path if os.path.exists(primary_path) else fallback_path
    return pygame.transform.scale(pygame.image.load(path), scale_size)

class TicTacToeUI:
    def __init__(self, game=None, size=1500):
        # General setup
        pygame.init()
        self.clock = pygame.time.Clock()
        
        # Setting up the main window
        self.WIDTH, self.HEIGHT = size - 250, size
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("TTIC Interface")
        
        # Colors
        self.blk = (0, 0, 0)
        self.white = (255, 255, 255)
        self.light_grey = (211, 211, 211)
        self.dark_blue = (0, 0, 209)
        self.dark_grey = (169, 169, 169)
        
        # Font setup
        pygame.font.init()
        self.font_pieces = pygame.font.SysFont(None, int(60 * self.HEIGHT / 600))
        self.font_large = pygame.font.SysFont(None, int(30 * self.HEIGHT / 600))
        self.font_small = pygame.font.SysFont(None, int(24 * self.HEIGHT / 600))
        
        # Initialize boards
        self.init_boards()

        # Connect the TicTacToe instance to the GUI
        self.game = game
        
    def init_boards(self):
        # Define the Tic Tac Toe board cells
        self.board_size = int(self.HEIGHT * 0.5)
        self.cell_size = self.board_size // 3
        self.border_width = 3
        self.adjusted_cell_size = self.cell_size - self.border_width
        
        # Position the board in the bottom left corner
        self.board_origin_x = self.border_width
        self.board_origin_y = self.HEIGHT - self.board_size - self.border_width
        
        # Create the board of rectangles
        self.board = []
        for row in range(3):
            for col in range(3):
                rect = pygame.Rect(
                    self.board_origin_x + col * (self.adjusted_cell_size + self.border_width),
                    self.board_origin_y + row * (self.adjusted_cell_size + self.border_width),
                    self.adjusted_cell_size,
                    self.adjusted_cell_size
                )
                self.board.append(rect)
        
        # Define the TTIC board cells
        self.ttic_board_size = self.cell_size
        self.ttic_cell_size = self.ttic_board_size // 2
        self.ttic_adjusted_cell_size = self.ttic_cell_size - self.border_width
        
        # Position the TTIC board
        self.ttic_board_origin_x = self.board_origin_x + self.board_size + self.cell_size // 2 + self.border_width
        self.ttic_board_origin_y = self.board_origin_y + self.cell_size // 2 + int(self.HEIGHT * 0.086)
        
        # Create the TTIC board of rectangles
        self.ttic_board = []
        for row in range(2):
            for col in range(2):
                rect = pygame.Rect(
                    self.ttic_board_origin_x + col * (self.ttic_adjusted_cell_size + self.border_width),
                    self.ttic_board_origin_y + row * (self.ttic_adjusted_cell_size + self.border_width),
                    self.ttic_adjusted_cell_size,
                    self.ttic_adjusted_cell_size
                )
                self.ttic_board.append(rect)
        
        # Define the letters for TTIC
        self.letters = {0: "T", 1: "T", 2: "I", 3: "C"}
        
        # Define the new board in the top right corner
        self.pieces_board_width = int(self.WIDTH * 0.4)
        self.pieces_board_height = int(self.HEIGHT * 0.5)
        self.top_right_cell_width = self.pieces_board_width // 2
        self.top_right_cell_height = self.pieces_board_height // 3
        self.top_right_adjusted_cell_width = self.top_right_cell_width - self.border_width
        self.top_right_adjusted_cell_height = self.top_right_cell_height - self.border_width
        
        # Position the top right board
        self.pieces_board_origin_x = self.WIDTH - self.pieces_board_width - self.border_width
        self.pieces_board_origin_y = self.border_width
        
        # Create the top right board of rectangles
        self.pieces_board = []
        for row in range(3):
            for col in range(2):
                rect = pygame.Rect(
                    self.pieces_board_origin_x + col * (self.top_right_adjusted_cell_width + self.border_width),
                    self.pieces_board_origin_y + row * (self.top_right_adjusted_cell_height + self.border_width),
                    self.top_right_adjusted_cell_width,
                    self.top_right_adjusted_cell_height
                ) 
                self.pieces_board.append(rect)
        
        # Define the letters for the top right board
        self.top_right_letters = {0: "A", 1: "B", 2: "C", 3: "D", 4: "E", 5: "F"}
    
    def draw_boards(self):
        # Draw the board of rectangles and labels
        for index, rect in enumerate(self.board):
            pygame.draw.rect(self.screen, self.blk, rect, self.border_width)
            label = self.font_small.render(str(index), True, self.blk)
            self.screen.blit(label, (rect.x + 5, rect.y + 5))  # Slightly offset from top left corner
        
        # Draw the TTIC board of rectangles and labels
        for index, rect in enumerate(self.ttic_board):
            if self.letters[index] == "T" or self.letters[index] == "I":
                pygame.draw.rect(self.screen, self.dark_blue, rect)
            elif self.letters[index] == "C":
                pygame.draw.rect(self.screen, self.dark_grey, rect)
            pygame.draw.rect(self.screen, self.blk, rect, self.border_width)  # Border
            label = self.font_large.render(self.letters[index], True, self.white)
            label_rect = label.get_rect(center=(rect.x + rect.width // 2, rect.y + rect.height // 2))
            self.screen.blit(label, label_rect)
        
        # Draw the top right board of rectangles and labels
        for index, rect in enumerate(self.pieces_board):
            pygame.draw.rect(self.screen, self.blk, rect, self.border_width)
            label = self.font_small.render(self.top_right_letters[index], True, self.blk)
            self.screen.blit(label, (rect.x + 5, rect.y + 5))  # Slightly offset from top left corner

    def update(self, pos):
        """
        Update the game logic of the board.

        :param pos: The position where the player has clicked.
        """
        x, y = pos[0], pos[1]
        if 0 <= x <= 750 and 750 <= y <= 1500:
            for i in range(3):
                for j in range(3):
                    if 250 * i  <= x <= 250 * (i + 1):
                        if 750 + (250 * j) <= y <= 750 + (250 * (j + 1)):
                            move = i + j * 3
                            self.game.place_piece(move)

    def smart_update(self):
        self.game.smart_place_piece()
        self.draw_current_board()
        pygame.display.flip()

    def draw_current_board(self):
        """
        Update the board of the GUI.
        """
        X_IMAGE = load_piece_image("x_piece.png", "x.png", (120, 120))
        O_IMAGE = load_piece_image("o_piece.png", "o.png", (120, 120))

        # Draw main 3x3 board pieces centered in each cell
        for index in range(9):
            space = self.game.board[index]
            if space is not None:
                rect = self.board[index]
                img = X_IMAGE if space == 'x' else O_IMAGE
                img_rect = img.get_rect(center=rect.center)
                self.screen.blit(img, img_rect)
        
        # Status Card (top-left quadrant)
        card_rect = pygame.Rect(0, 0, 660, 270)
        card_rect.center = (375, 375)

        winner = self.game.get_winner()
        is_draw = self.game.determine_draw()

        if winner is not None:
            player_obj = self.game.p1 if winner == self.game.p1.piece else self.game.p2
            role = "Smart Arm" if isinstance(player_obj, Arm) else "Human"
            piece_str = "Red 'X'" if winner == 'x' else "Blue 'O'"
            status_title = "VICTORY!"
            status_desc = f"{role} ({piece_str}) Wins!"
            border_color = (34, 139, 34)
            text_color = (34, 139, 34)
            badge_img = X_IMAGE if winner == 'x' else O_IMAGE
        elif is_draw:
            status_title = "GAME OVER"
            status_desc = "Tie Game!"
            border_color = (100, 100, 100)
            text_color = self.blk
            badge_img = None
        else:
            curr_turn_piece = self.game.current_player()
            curr_player_obj = self.game.current_player_obj()
            role = "Smart Arm" if isinstance(curr_player_obj, Arm) else "Human"
            piece_str = "Red 'X'" if curr_turn_piece == 'x' else "Blue 'O'"
            status_title = "CURRENT TURN"
            status_desc = f"{role} ({piece_str})"
            border_color = (200, 30, 30) if curr_turn_piece == 'x' else (30, 80, 200)
            text_color = border_color
            badge_img = X_IMAGE if curr_turn_piece == 'x' else O_IMAGE

        # Draw card background & border
        pygame.draw.rect(self.screen, self.white, card_rect, border_radius=20)
        pygame.draw.rect(self.screen, border_color, card_rect, 4, border_radius=20)

        # Draw Title
        lbl_title = self.font_small.render(status_title, True, (120, 120, 120))
        self.screen.blit(lbl_title, lbl_title.get_rect(center=(card_rect.centerx, card_rect.top + 45)))

        # Draw Status Description & Badge Icon
        lbl_desc = self.font_large.render(status_desc, True, text_color)
        if badge_img:
            icon_scaled = pygame.transform.scale(badge_img, (55, 55))
            total_w = lbl_desc.get_width() + 65
            start_x = card_rect.centerx - (total_w // 2)
            self.screen.blit(icon_scaled, (start_x, card_rect.top + 135))
            self.screen.blit(lbl_desc, (start_x + 65, card_rect.top + 145))
        else:
            self.screen.blit(lbl_desc, lbl_desc.get_rect(center=(card_rect.centerx, card_rect.top + 160)))
            
        # Available pieces centered in cells A-F
        arm = self.arm_player
        pieces = arm.pieces

        for indx in range(6):
            letter = self.top_right_letters[indx]
            if letter in pieces:
                rect = self.pieces_board[indx]
                img = X_IMAGE if arm.piece == 'x' else O_IMAGE
                img_rect = img.get_rect(center=rect.center)
                self.screen.blit(img, img_rect)

    @property
    def arm_player(self):
        return self.game.p1 if isinstance(self.game.p1, Arm) else self.game.p2

    @property
    def human_player(self):
        return self.game.p1 if not isinstance(self.game.p1, Arm) else self.game.p2

    def draw_button(self, rect, text, is_hovered, font=None):
        font = font or self.font_large
        lbl_test = font.render(text, True, self.blk)
        if lbl_test.get_width() > rect.width - 30:
            font = self.font_small

        if is_hovered:
            bg_color = (220, 235, 252)
            border_color = (0, 102, 204)
            border_width = 4
            text_color = (0, 102, 204)
        else:
            bg_color = self.white
            border_color = self.blk
            border_width = 3
            text_color = self.blk

        pygame.draw.rect(self.screen, bg_color, rect, border_radius=12)
        pygame.draw.rect(self.screen, border_color, rect, border_width, border_radius=12)
        lbl = font.render(text, True, text_color)
        self.screen.blit(lbl, lbl.get_rect(center=rect.center))

    def show_setup_menu(self):
        # Step 1: Choose AI Difficulty
        lvl = 2
        btn_width, btn_height = int(self.WIDTH * 0.80), int(self.HEIGHT * 0.08)
        cx = (self.WIDTH - btn_width) // 2

        btn_novice = pygame.Rect(cx, int(self.HEIGHT * 0.35), btn_width, btn_height)
        btn_pro    = pygame.Rect(cx, int(self.HEIGHT * 0.46), btn_width, btn_height)
        btn_expert = pygame.Rect(cx, int(self.HEIGHT * 0.57), btn_width, btn_height)

        selecting_diff = True
        while selecting_diff:
            self.screen.fill(self.light_grey)
            
            title = self.font_pieces.render("TicTacToe (Vision)", True, self.blk)
            self.screen.blit(title, title.get_rect(center=(self.WIDTH // 2, int(self.HEIGHT * 0.15))))
            
            sub = self.font_large.render("Select AI Difficulty:", True, self.blk)
            self.screen.blit(sub, sub.get_rect(center=(self.WIDTH // 2, int(self.HEIGHT * 0.26))))

            mouse_pos = pygame.mouse.get_pos()
            any_hovered = False
            for rect, text, level in [(btn_novice, "0: Novice", 0), (btn_pro, "1: Pro", 1), (btn_expert, "2: Expert (Default)", 2)]:
                is_h = rect.collidepoint(mouse_pos)
                if is_h:
                    any_hovered = True
                self.draw_button(rect, text, is_h)

            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND if any_hovered else pygame.SYSTEM_CURSOR_ARROW)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_game()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if btn_novice.collidepoint(event.pos):
                        lvl = 0; selecting_diff = False
                    elif btn_pro.collidepoint(event.pos):
                        lvl = 1; selecting_diff = False
                    elif btn_expert.collidepoint(event.pos):
                        lvl = 2; selecting_diff = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_0, pygame.K_KP0):
                        lvl = 0; selecting_diff = False
                    elif event.key in (pygame.K_1, pygame.K_KP1):
                        lvl = 1; selecting_diff = False
                    elif event.key in (pygame.K_2, pygame.K_KP2, pygame.K_RETURN, pygame.K_KP_ENTER):
                        lvl = 2; selecting_diff = False
                    elif event.key == pygame.K_ESCAPE:
                        self.quit_game()

        # Step 2: Choose Who Starts First
        btn_human = pygame.Rect(cx, int(self.HEIGHT * 0.40), btn_width, btn_height)
        btn_arm   = pygame.Rect(cx, int(self.HEIGHT * 0.54), btn_width, btn_height)

        arm_starts = False
        selecting_start = True
        while selecting_start:
            self.screen.fill(self.light_grey)

            title = self.font_pieces.render("Who Starts First?", True, self.blk)
            self.screen.blit(title, title.get_rect(center=(self.WIDTH // 2, int(self.HEIGHT * 0.20))))

            mouse_pos = pygame.mouse.get_pos()
            any_hovered = False
            for rect, text in [(btn_human, "1: Human (Red 'x')"), (btn_arm, "2: Smart Arm (Red 'x')")]:
                is_h = rect.collidepoint(mouse_pos)
                if is_h:
                    any_hovered = True
                self.draw_button(rect, text, is_h)

            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND if any_hovered else pygame.SYSTEM_CURSOR_ARROW)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_game()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if btn_human.collidepoint(event.pos):
                        arm_starts = False; selecting_start = False
                    elif btn_arm.collidepoint(event.pos):
                        arm_starts = True; selecting_start = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_1, pygame.K_KP1, pygame.K_RETURN, pygame.K_KP_ENTER):
                        arm_starts = False; selecting_start = False
                    elif event.key in (pygame.K_2, pygame.K_KP2):
                        arm_starts = True; selecting_start = False
                    elif event.key == pygame.K_ESCAPE:
                        self.quit_game()

        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        if arm_starts:
            p1 = SmartArm('x', lvl=lvl)
            p2 = Player('o')
        else:
            p1 = Player('x')
            p2 = SmartArm('o', lvl=lvl)

        self.game = TicTacToe(p1, p2, auto_start=False)

    def quit_game(self):
        print("Closing game gracefully...")
        try:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        except Exception:
            pass

        try:
            pygame.display.quit()
            pygame.quit()
        except Exception:
            pass

        if hasattr(self, 'game') and self.game is not None:
            arm_obj = getattr(self, 'arm_player', None)
            if arm_obj and hasattr(arm_obj, 'arm'):
                try:
                    print("Disabling arm torque...")
                    arm_obj.arm._disable_torque()
                except Exception as e:
                    print(f"Arm shutdown notice: {e}")
        sys.exit(0)

    def handle_game_over(self):
        btn_width, btn_height = int(self.WIDTH * 0.80), int(self.HEIGHT * 0.08)
        cx = (self.WIDTH - btn_width) // 2

        btn_restart = pygame.Rect(cx, int(self.HEIGHT * 0.46), btn_width, btn_height)
        btn_quit    = pygame.Rect(cx, int(self.HEIGHT * 0.60), btn_width, btn_height)

        winner = self.game.get_winner()
        if winner is not None:
            player_num = 1 if winner == self.game.p1.piece else 2
            result_text = f"Player {player_num} Wins!"
            color = (34, 139, 34)
        else:
            result_text = "Tie Game!"
            color = (0, 0, 0)

        while True:
            self.screen.fill(self.light_grey)

            title = self.font_pieces.render(result_text, True, color)
            self.screen.blit(title, title.get_rect(center=(self.WIDTH // 2, int(self.HEIGHT * 0.25))))

            sub = self.font_large.render("Game Over", True, self.blk)
            self.screen.blit(sub, sub.get_rect(center=(self.WIDTH // 2, int(self.HEIGHT * 0.35))))

            mouse_pos = pygame.mouse.get_pos()
            is_h_r = btn_restart.collidepoint(mouse_pos)
            is_h_q = btn_quit.collidepoint(mouse_pos)

            self.draw_button(btn_restart, "Restart (Arm Cleans Board)", is_h_r)
            self.draw_button(btn_quit, "Quit Game", is_h_q)

            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND if (is_h_r or is_h_q) else pygame.SYSTEM_CURSOR_ARROW)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_game()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if btn_restart.collidepoint(event.pos):
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                        print("Resetting board and cleaning pieces...")
                        self.game.reset()
                        if isinstance(self.game.current_player_obj(), SmartArm):
                            self.smart_update()
                            time.sleep(0.3)
                        return
                    elif btn_quit.collidepoint(event.pos):
                        self.quit_game()
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_r, pygame.K_RETURN, pygame.K_KP_ENTER):
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                        print("Resetting board and cleaning pieces...")
                        self.game.reset()
                        if isinstance(self.game.current_player_obj(), SmartArm):
                            self.smart_update()
                            time.sleep(0.3)
                        return
                    elif event.key in (pygame.K_q, pygame.K_ESCAPE):
                        self.quit_game()
            time.sleep(0.05)

    def run(self):
        if self.game is None:
            self.show_setup_menu()

        # Initial render of board window so UI is visible
        self.screen.fill(self.light_grey)
        self.draw_boards()
        self.draw_current_board()
        # Update the screen
        pygame.display.flip()

        # If Arm starts, make its first move AFTER UI window is open
        if isinstance(self.game.current_player_obj(), SmartArm) and self.game.board.count(None) == 9:
            self.smart_update()
            time.sleep(0.3)

        while True:
            # Re-draw current board state every frame so post-restart window is clean
            self.screen.fill(self.light_grey)
            self.draw_boards()
            self.draw_current_board()
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_game()
                elif event.type == pygame.KEYDOWN and event.key in (pygame.K_q, pygame.K_ESCAPE):
                    self.quit_game()

            if self.game.current_player_wins() or self.game.determine_draw():
                self.handle_game_over()
                continue

            play_detected = False
            while not play_detected:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.quit_game()
                    elif event.type == pygame.KEYDOWN and event.key in (pygame.K_q, pygame.K_ESCAPE):
                        self.quit_game()

                vision.wait_for_move()
                time.sleep(0.1)
                tile, new_piece = vision.get_piece_change()
                if tile is None or tile > 8:
                    continue
                if new_piece == self.human_player.piece:
                    play_detected = True

            self.game.place_piece(tile)

            # Fill the background with light grey color
            self.screen.fill(self.light_grey)
            # Draw all the boards
            self.draw_boards()
            # Draw moves
            self.draw_current_board()
    
            # Update the screen
            pygame.display.flip()

            if not self.game.current_player_wins() and not self.game.determine_draw():
                self.smart_update()
                time.sleep(0.3)
                self.screen.fill(self.light_grey)
                # Draw all the boards
                self.draw_boards()
                # Draw moves
                self.draw_current_board()
                # Update the screen
                pygame.display.flip()

            self.clock.tick(60) # Frames per second

if __name__ == "__main__":
    vision = BoardVision(False, 4)
    ui = TicTacToeUI()
    ui.run()
    if hasattr(ui.arm_player, 'arm'):
        ui.arm_player.arm._disable_torque()
