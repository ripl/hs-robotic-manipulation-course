# Import Pygame Library calling it pygame
import pygame
import sys

# General setup
pygame.init()
clock = pygame.time.Clock()

# Setting up the main window
WIDTH, HEIGHT = 500, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TTIC Interface")

# Colors
blk = (0, 0, 0)
white = (255, 255, 255)
light_grey = (211, 211, 211)
dark_blue = (0, 0, 209)
dark_grey = (169, 169, 169)

# Font setup
pygame.font.init()
font_large = pygame.font.SysFont(None, 30)
font_small = pygame.font.SysFont(None, 24)

# Define the Tic Tac Toe board cells
board_size = 300
cell_size = board_size // 3
border_width = 1
adjusted_cell_size = cell_size - border_width

# Position the board in the bottom left corner
board_origin_x = border_width  # Slightly offset to account for border width
board_origin_y = HEIGHT - board_size - border_width  # Offset from bottom

# Create the board of rectangles
board = []
for row in range(3):
    for col in range(3):
        rect = pygame.Rect(
            board_origin_x + col * (adjusted_cell_size + border_width), 
            board_origin_y + row * (adjusted_cell_size + border_width), 
            adjusted_cell_size, 
            adjusted_cell_size
        )
        board.append(rect)

# Define the TTIC board cells
ttic_board_size = cell_size
ttic_cell_size = ttic_board_size // 2
ttic_adjusted_cell_size = ttic_cell_size - border_width

# Position the TTIC board to the right of the main board, centered on the board center block, and moved down by 100 pixels
ttic_board_origin_x = board_origin_x + board_size + cell_size // 2 + border_width
ttic_board_origin_y = board_origin_y + cell_size // 2 + 52

# Create the TTIC board of rectangles
ttic_board = []
for row in range(2):
    for col in range(2):
        rect = pygame.Rect(
            ttic_board_origin_x + col * (ttic_adjusted_cell_size + border_width), 
            ttic_board_origin_y + row * (ttic_adjusted_cell_size + border_width), 
            ttic_adjusted_cell_size, 
            ttic_adjusted_cell_size
        )
        ttic_board.append(rect)

# Define the letters for TTIC
letters = {
    0: "T", 1: "T", 2: "I", 3: "C"
}

# Define the new board in the top right corner
pieces_board_width = 200
pieces_board_height = 300
top_right_cell_width = pieces_board_width // 2
top_right_cell_height = pieces_board_height // 3
top_right_adjusted_cell_width = top_right_cell_width - border_width
top_right_adjusted_cell_height = top_right_cell_height - border_width

# Position the top right board in the top right corner
pieces_board_origin_x = WIDTH - pieces_board_width - border_width
pieces_board_origin_y = border_width

# Create the top right board of rectangles
pieces_board = []
for row in range(3):
    for col in range(2):
        rect = pygame.Rect(
            pieces_board_origin_x + col * (top_right_adjusted_cell_width + border_width), 
            pieces_board_origin_y + row * (top_right_adjusted_cell_height + border_width), 
            top_right_adjusted_cell_width, 
            top_right_adjusted_cell_height
        )
        pieces_board.append(rect)

# Define the letters for the top right board
top_right_letters = {
    0: "A", 1: "B", 2: "C", 3: "D", 4: "E", 5: "F"
}

# Game loop
while True:
    # Handling input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    # Fill the background with light grey color
    screen.fill(light_grey)
    
    # Draw the board of rectangles and labels
    for index, rect in enumerate(board):
        pygame.draw.rect(screen, blk, rect, border_width)
        
        # Create the text surface
        label = font_small.render(str(index), True, blk)
        # Draw the text surface on the screen
        screen.blit(label, (rect.x + 5, rect.y + 5))  # Slightly offset from top left corner
    
    # Draw the TTIC board of rectangles and labels
    for index, rect in enumerate(ttic_board):
        if letters[index] == "T" or letters[index] == "I":
            pygame.draw.rect(screen, dark_blue, rect)
        elif letters[index] == "C":
            pygame.draw.rect(screen, dark_grey, rect)
        pygame.draw.rect(screen, blk, rect, border_width)  # Border
        
        # Create the text surface for TTIC
        label = font_large.render(letters[index], True, white)
        label_rect = label.get_rect(center=(rect.x + rect.width // 2, rect.y + rect.height // 2))
        # Draw the text surface on the screen
        screen.blit(label, label_rect)
    
    # Draw the top right board of rectangles and labels
    for index, rect in enumerate(pieces_board):
        pygame.draw.rect(screen, blk, rect, border_width)
        
        # Create the text surface for the top right board
        label = font_small.render(top_right_letters[index], True, blk)
        # Draw the text surface on the screen
        screen.blit(label, (rect.x + 5, rect.y + 5))  # Slightly offset from top left corner

    # Update the screen
    pygame.display.flip()
    clock.tick(60) # Frames per second
