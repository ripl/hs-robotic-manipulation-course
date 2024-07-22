import pygame
from game import TicTacToe
from players import Player, Arm, SmartArm
import sys

class TicTacToeGUI:
    def __init__(self, game=None, size=800):
        # General setup
        pygame.init()
        self.clock = pygame.time.Clock()
        
        # Setting up the main window
        self.WIDTH, self.HEIGHT = size - 100, size
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
        self.border_width = 1
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
        Update the GUI and the game logic of the board.

        :param pos: The position where the player has clicked.
        """
        pass

    def run(self):
        # Game loop
        while True:
            # Handling input
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            # Fill the background with light grey color
            self.screen.fill(self.light_grey)
            
            # Draw all the boards
            self.draw_boards()
            
            # Update the screen
            pygame.display.flip()
            self.clock.tick(60)  # Frames per second

if __name__ == "__main__":
    game = TicTacToeGUI()
    game.run()
