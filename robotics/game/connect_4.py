import random, os, sys
import numpy as np
import time
from robotics.robot.robot import Robot
from c4_players import Player, Arm, SmartArm

class Connect_Four:

    
    def __init__(self, player1, player2, board=None):
        '''
        Create an instance of Connect_Four.
        
        :param player1: The first player.
        :param player2: The second player.
        :param board: Optional initial board state.
        '''
        self.p1 = player1
        self.p2 = player2
        
        if board is None:
            self.board = [[None for _ in range(7)] for _ in range(6)]
            print(board)

            
            # Player 1 is always first
            self.curr_turn = player1.piece
        else:
            self.board = board
            # Determine which Player's turn it is
            p1_count = board.count(self.p1.piece)
            p2_count = board.count(self.p2.piece)

            if p1_count > p2_count:
                self.curr_turn = self.p2.piece
            else:
                self.curr_turn = self.p1.piece

        # Record the current state of the board.
        self.history = [self.board.copy()]
                
        # Display board and current player's turn.
        print(self)

        # If the current player is a SmartArm, play a piece.
        self.smart_place_piece()

    def current_player(self):
        '''
        Return the current player's piece.
        
        :returns: The piece of the current player.
        '''
        return self.curr_turn
        
    def __repr__(self):
        '''
        Draw the current state of the Connect_Four board.
        
        :returns: The string representation of the board.
        '''
        board_str = ''

        def piece(space):
            return ' ' if space is None else space
        
        if self.current_player() == self.p1.piece:
            player = self.p1.count
        else:
            player = self.p2.count

        if self.current_player_wins():
            board_str += f'Player {player} Wins!'
        elif self.determine_draw():
            board_str += 'Draw!'
        else:
            board_str += f'Your move, Player {player}.'

        board_str += '\n'
        for row in self.board:
            board_str += f'{(row)}'
            board_str += '---------\n'
        return board_str

    def is_valid_move(self, pos):
        '''
        Determine if the given coordinates are a valid move.
        
        :param pos: The position on the board.
        :returns: True if the move is valid, False otherwise.
        '''
        if not 0 <= pos < 7:
            print('Invalid space!')
            return False
        elif self.board[pos] is not None:
            print('Space is occupied!')
            return False
        else:
            return True 
    
    
    def place_piece(self, pos):
        '''
        Handle updates to the state of the Connect_Four board.
        
        :param pos: The position on the board.
        
        '''
        row_number = None
        for row in reversed(range(len(self.board))):  # Start from the bottom row
            if self.board[row][pos] == None:
                self.board[row][pos] = self.current_player()
                self.history.append(self.board.copy())
                row_number = row
                break

        current_player = self.current_player_obj()
        if isinstance(current_player, Arm):
            self.arm_move(pos, current_player)        
                                                                                                                                                                                                                        
        if not self.current_player_wins():
            self.update()

        print(self)
        return row_number
    
    def smart_place_piece(self):                                                                                                                                                                                                                                                                                                                                                                                                                                     
        next_player = self.current_player_obj()
        if isinstance(next_player, SmartArm):   
            next_player.play(self)
    



    def update(self):
        '''
        Update the current turn of the player in the game ('red' or 'yel').
        '''
        if self.curr_turn == self.p1.piece:
            self.curr_turn = self.p2.piece
        else:
            self.curr_turn = self.p1.piece
 
    def current_player_wins(self):
        '''String representation of the winner,
        Checks to see if the current player has a winning triple.
        
        :returns: True if the current player has won, False otherwise.
        '''

        if self.check_horizontal():
            return True
        elif self.check_vertical():
            return True
        elif self.check_diagonal():
            return True
        else:
            return False
        
    def check_horizontal(self):
        for row in range(6):
            for col in range(3):  # 6 - 4 + 1 = 3
                if (
                    self.board[row][col] is not None and
                    self.board[row][col] == self.board[row][col+1] == self.board[row][col+2] == self.board[row][col+3]
                ):
                    return True
        
    
    def check_vertical(self):
        for col in range(4):
            for row in range(3):  
                if (
                    self.board[row][col] is not None and
                    self.board[row][col] == self.board[row+1][col] == self.board[row+2][col] == self.board[row+3][col]
                ):
                    return True
        return False
    
    def check_diagonal(self):
    # Positive slope (\)
        for row in range(6):
            for col in range(4):
                if (
                    self.board[row][col] is not None and
                    self.board[row][col] == self.board[row-1][col+1] == self.board[row-2][col+2] == self.board[row-3][col+3]
                ):
                    return True
        # Negative slope (/)
        for row in range(3):
            for col in range(4):
                if (
                    self.board[row][col] is not None and
                    self.board[row][col] == self.board[row+1][col-1] == self.board[row+2][col-2] == self.board[row+3][col-3]
                ):
                    return True
        return False
                
    
    

    def get_winner(self):
        '''
        Return the winner if there is one.
        
        :returns: 'Player 1', 'Player 2' or 'Undecided'
        '''
        if self.current_player_wins():
            return self.current_player()
        return None

    def determine_draw(self):
        '''
        Determine if there are no moves left on the board, resulting in a draw.
        
        :returns: True if the game is a draw, False otherwise.
        '''
        for space in self.board[0]:
            if space is None:
                return False
        return True


    def current_player_obj(self):
        '''
        Return the current Player object.

        This method determines the current player based on the game state 
        and returns the corresponding Player or Arm object.

        :returns: The current Player object (self.p1 or self.p2).
        '''
        return self.p1 if self.curr_turn == self.p1.piece else self.p2

    def arm_move(self, pos, current_player):
        '''
        Execute a move using the robotic arm if the current player is an Arm.

        This method checks if the current player is an Arm and, if so, 
        commands the robotic arm to move a piece to the specified position 
        on the physical board.

        :param pos: The position on the physical board where the piece should be moved.
        '''
        #indx = random.randint(0, len(current_player.pieces) - 1)
        piece = 'connect'
        #current_player.used_pieces.append(piece)
        current_player.move_piece(piece, str(pos))

if __name__ == '__main__':

    print("Welcome to Connect_Four. \nYou are Player 1. \nPlayer 2 is the Smart Arm.\n")
    print("AI difficulty: ")
    print("   Novice  (0)")
    print("   Pro     (1)")
    print("   Expert  (2)")
    lvl = int(input("\nChoose Wisely: ").strip())

    p1 = Player('rd')
    p2 = SmartArm('yw', lvl)
    game = Connect_Four(p1, p2)

    os.system('clear')

    print(p1)
    print(p2)
    print("Enter a position (0-6) to place your piece. \nThe SmartArm will play automatically.")
    print("Enter 'q' at any time to quit. Press Enter to start the game.")
    print()
    
    while True:
        try:
            user_input = input("Enter the position: ")
            if user_input.lower() == 'q':
                print("Quitting the game.")
                break
            pos = int(user_input)
            game.place_piece(pos)
            time.sleep(0.25)  # add suspense
            game.smart_place_piece()
           
        except Exception as e:
            print(f"An error occurred: {e}")
            
    # game.reset()
    p2.arm.set_and_wait_goal_pos([2048, 1600, 1070, 2200, 2048, 2048])
    p2.arm._disable_torque()
