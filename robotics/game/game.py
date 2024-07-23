import random, os, sys
from robotics.robot.robot import Robot
from players import Player, Arm, SmartArm

class TicTacToe:
    """
    Represents a TicTacToe game instance.

    Example 1:
    -----------

    >>> p1 = Player('x')
    >>> p2 = Player('o')
    >>> board = ['x', 'o', None, 'x', None, None, None, None, None ]
    >>> game = TicTacToe(p1, p2, board)
    Your move, Player 2.
    x | o |  
    ---------
    x |   |  
    ---------
      |   |  
    >>> game.place_piece(6)
    Your move, Player 1.
    x | o |  
    ---------
    x |   |  
    ---------
    o |   |  
    >>> game.current_player_wins()
    False
    >>> game.place_piece(1)
    Space is occupied!
    Your move, Player 1.
    x | o |  
    ---------
    x |   |  
    ---------
    o |   |  
    >>> game.place_piece(9)
    Invalid space!
    Your move, Player 1.
    x | o |  
    ---------
    x |   |  
    ---------
    o |   |  
    >>> game.place_piece(4)
    Your move, Player 2.
    x | o |  
    ---------
    x | x |  
    ---------
    o |   |  
    >>> game.current_player()
    'o'
    >>> game.place_piece(7)
    Your move, Player 1.
    x | o |  
    ---------
    x | x |  
    ---------
    o | o |  
    >>> game.place_piece(8)
    Player 1 Wins!
    x | o |  
    ---------
    x | x |  
    ---------
    o | o | x 
    >>> game.get_winner()
    'x'
    >>> game.undo()
    Your move, Player 1.
    x | o |  
    ---------
    x | x |  
    ---------
    o |   |  
    >>> game.place_piece(2)
    Your move, Player 2.
    x | o | x 
    ---------
    x | x |  
    ---------
    o | o | 
    >>> game.determine_draw()
    False
    >>> game.place_piece(5)
    Your move, Player 1.
    x | o | x 
    ---------
    x | x | o 
    ---------
    o | o | 
    >>> game.place_piece(8)
    Draw!
    x | o | x 
    ---------
    x | x | o 
    ---------
    o | o | x
    >>> game.determine_draw()
    True
    >>> game.reset()
    Your move, Player 1.
      |   |   
    ---------
      |   |   
    ---------
      |   |  
    >>> game.undo()
    This is the initial state of the board.
    """
    def __init__(self, player1, player2, board=None):
        """
        Create an instance of TicTacToe.
        
        :param player1: The first player.
        :param player2: The second player.
        :param board: Optional initial board state.
        """
        self.p1 = player1
        self.p2 = player2
        
        if board is None:
            self.board = [None] * 9
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

    def current_player(self):
        """
        Return the current player's piece.
        
        :returns: The piece of the current player.
        """
        return self.curr_turn
        
    def __repr__(self):
        """
        Draw the current state of the TicTacToe board.
        
        :returns: The string representation of the board.
        """
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
        board_str += f'{piece(self.board[0])} | {piece(self.board[1])} | {piece(self.board[2])}\n'
        board_str += '---------\n'
        board_str += f'{piece(self.board[3])} | {piece(self.board[4])} | {piece(self.board[5])}\n'
        board_str += '---------\n'
        board_str += f'{piece(self.board[6])} | {piece(self.board[7])} | {piece(self.board[8])}'

        return board_str

    def is_valid_move(self, pos):
        """
        Determine if the given coordinates are a valid move.
        
        :param pos: The position on the board.
        :returns: True if the move is valid, False otherwise.
        """
        if not 0 <= pos < 9:
            print('Invalid space!')
            return False
        elif self.board[pos] is not None:
            print('Space is occupied!')
            return False
        else:
            return True 
    
    def place_piece(self, pos):
        """
        Handle updates to the state of the TicTacToe board.
        
        :param pos: The position on the board.
        """
        if self.is_valid_move(pos):
            self.board[pos] = self.current_player()
            self.history.append(self.board.copy())

            current_player = self.current_player_obj()
            if isinstance(current_player, Arm):
                self.arm_move(pos, current_player)            

            if not self.current_player_wins():
                self.update()

        print(self)

    def smart_place_piece(self):
        next_player = self.current_player_obj()
        if isinstance(next_player, SmartArm):   
            next_player.play(self)

    def update(self):
        """
        Update the current turn of the player in the game ('x' or 'o').
        """
        if self.curr_turn == self.p1.piece:
            self.curr_turn = self.p2.piece
        else:
            self.curr_turn = self.p1.piece

    def current_player_wins(self):
        """String representation of the winner,
        Checks to see if the current player has a winning triple.
        
        :returns: True if the current player has won, False otherwise.
        """
        winning_triples = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8),  # horizontal
            (0, 3, 6), (1, 4, 7), (2, 5, 8),  # vertical
            (0, 4, 8), (2, 4, 6)              # diagonal
        ]
        for x, y, z in winning_triples:
            if self.board[x] is not None and self.board[x] == self.board[y] == self.board[z]:

                return True
        return False

    def get_winner(self):
        """
        Return the winner if there is one.
        
        :returns: 'Player 1', 'Player 2' or 'Undecided'
        """
        if self.current_player_wins():
            return self.current_player()
        return None

    def determine_draw(self):
        """
        Determine if there are no moves left on the board, resulting in a draw.
        
        :returns: True if the game is a draw, False otherwise.
        """
        for space in self.board:
            if space is None:
                return False
        return True

    def reset(self):
        """
        Reset the game to an empty board. This will create a new initial state.
        """
        # If the board is reset and an Arm is one of the players,
        # the robotic arm should clean up its own pieces.
        curr_board = self.history[-1].copy()
        if isinstance(self.p1, Arm):
            self.p1.clean_board(curr_board)
        elif isinstance(self.p2, Arm):
            self.p2.clean_board(curr_board)

        self.board = [None] * 9
        self.history = [self.board.copy()]
        self.curr_turn = self.p1.piece

        print("The game has been reset to an empty board.")

    def initial(self):
        """
        Reset the game to its initial state.
        """
        self.board = self.history[0].copy()
        self.history = [self.board.copy()]
        self.curr_turn = self.p1.piece if self.board.count(self.p1.piece) <= self.board.count(self.p2.piece) else self.p2.piece
        print("The game has been reset to its initial state.")
        print(self)

    def undo(self):
        """
        Revert to the previous state of the game.
        """
        if len(self.history) > 1:
            self.history.pop()
            self.board = self.history[-1].copy()
            self.update()
        else:
            print('This is the initial state of the board.')
        
        print(self)

    def current_player_obj(self):
        """
        Return the current Player object.

        This method determines the current player based on the game state 
        and returns the corresponding Player or Arm object.

        :returns: The current Player object (self.p1 or self.p2).
        """
        return self.p1 if self.curr_turn == self.p1.piece else self.p2

    def arm_move(self, pos, current_player):
        """
        Execute a move using the robotic arm if the current player is an Arm.

        This method checks if the current player is an Arm and, if so, 
        commands the robotic arm to move a piece to the specified position 
        on the physical board.

        :param pos: The position on the physical board where the piece should be moved.
        """
        indx = random.randint(0, len(current_player.pieces) - 1)
        piece = current_player.pieces.pop(indx)
        current_player.used_pieces.append(piece)
        current_player.move_piece(piece, str(pos))

if __name__ == '__main__':

    print("Welcome to TicTacToe. \nYou are Player 1. \nPlayer 2 is the Smart Arm.\n")
    print("AI difficulty: ")
    print("   Novice  (1)")
    print("   Pro     (2)")
    print("   Expert  (3)")
    lvl = int(input("\nChoose Wisely: ").strip())

    p1 = Player('x')
    p2 = SmartArm('o', lvl)
    game = TicTacToe(p1, p2)

    os.system('clear')

    print(p1)
    print(p2)
    print("Enter a position (0-8) to place your piece. \nThe SmartArm will play automatically.")
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
            game.smart_place_piece()
        except ValueError:
            print("Invalid input. Please enter a number between 0 and 8 or 'q' to quit.")
        except Exception as e:
            print(f"An error occurred: {e}")
            
    # game.reset()
    p2.arm.set_and_wait_goal_pos([2048, 1600, 1070, 2200, 2048, 2048])
    p2.arm._disable_torque()
