import json
from robotics.robot.robot import Robot

class Player:
    """
    Represents a player in a TicTacToe instance.

    Examples:
    -----------

    >>> p1 = Player('x')
    >>> p2 = Player('o') 
    >>> p1
    Player 1 is "x"
    >>> p2
    Player 2 is "o"
    >>> p3 = Player('x')
    Warning: Cannot create more than two players.
    >>> p3 is None
    True
    """
    # cls variable
    player_count = 0

    def __new__(cls, piece):
        if cls.player_count >= 2:
            print('Warning: Cannot create more than two players.')
            return None
        return super(Player, cls).__new__(cls)

    def __init__(self, piece):
        self.piece = piece
        Player.player_count += 1
        self.count = Player.player_count

    def __repr__(self):
        return f'Player {self.count} is "{self.piece}"'


class Arm(Player):
    """
    Represents a Robotic arm in a TicTacToe instance.

    Examples:
    -----------

    >>> p1 = Player('x')
    >>> p2 = Arm('o') 
    >>> p1
    Player 1 is "x"
    >>> p2
    ArmPlayer 2 is "o"
    >>> p2.move_piece("A", 0)
    Moved piece from A to 0.
    """
    def __init__(self, piece, config_path='../config.json', positions_path='../actions.json'):
        """
        Create an Arm instance, inherit from the Player class.

        :param piece: The piece assigned to the Arm player (e.g., 'x' or 'o').
        :param config_path: Path to the configuration file for the robotic arm.
        :param positions_path: Path to the file containing actions or positions.
        """
        super().__init__(piece)

        # Load robot settings
        with open(config_path, 'r') as f:
            config = json.load(f)
            self.arm_config = config['arm']

        # Load game positions
        with open(positions_path, 'r') as f:
            self.positions = json.load(f)

        # Initialize the robotic arm with the loaded configuration
        self.arm = Robot(device_name=self.arm_config['device_name'], 
                         servo_ids=self.arm_config['servo_ids'],
                         velocity_limit=self.arm_config['velocity_limit'],
                         max_position_limit=self.arm_config['max_position_limit'],
                         min_position_limit=self.arm_config['min_position_limit'])

        # Move the arm to the home start position
        self.arm.set_and_wait_goal_pos(self.arm_config['home_pos'])

        # NOTE: This list will represnt the available "start" pieces.
        self.pieces = ["A", "B", "C", "D", "E", "F"]

    def __repr__(self):
        return f'ArmPlayer {self.count} is "{self.piece}"'
    
    def move_piece(self, start, end):
        """
        Move a piece from start to end position on the physical board.

        This method will use the robotic arm to pick up a piece from the 
        specified start position and place it at the specified end position.

        :param start: The start position on the physical board.
        :param end: The end position on the physical board.
        """
        pass

    def clean_board(self, curr_board):
        """
        Reset the board by moving pieces back to their start positions.

        This method finds the pieces that belong to the robotic arm on the 
        board and moves them back to their designated start positions.

        :param curr_board: The current state of the board to be reset.
        """
        start_positions = ["A", "B", "C", "D", "E", "F"]
        pass

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
    >>> game.curr_player_wins()
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
    o | o |  
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
    Cat Game!
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
            # Determine which Players turn it is
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

        if self.curr_player_wins():
            board_str += f'Player {player} Wins!'
        elif self.determine_draw():
            board_str += 'Cat Game!'
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

            # If the Player is the Arm, play on the board
            self.arm_move(pos)

        if not self.curr_player_wins():
            self.update()
        
        print(self)

    def update(self):
        """
        Update the current turn of the player in the game ('x' or 'o').
        """
        if self.curr_turn == self.p1.piece:
            self.curr_turn = self.p2.piece
        else:
            self.curr_turn = self.p1.piece

    def curr_player_wins(self):
        """
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
        
        :returns: The piece of the winner, or None if there is no winner.
        """
        if self.curr_player_wins():
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
        # the robotic arm should clean up it's own pieces.
        curr_board = self.history[-1].copy()
        if isinstance(self.p1, Arm):
            self.p1.clean_board(curr_board)
        elif isinstance(self.p2, Arm):
            self.p1.clean_board(curr_board)

        self.board = [None] * 9
        self.history = [self.board.copy()]
        self.curr_turn = self.p1.piece
        print("The game has been reset to an empty board.")
        print(self)

    def initial(self):
        """
        Reset the game to its initial state.
        """
        self.board = self.history[0].copy()
        self.history = [self.board.copy()]
        self.curr_turn = self.p2.piece if self.board.count(self.p1.piece) > self.board.count(self.p2.piece) else self.p1.piece
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

    def curr_player_obj(self):
        """
        Return the current Player object.

        This method determines the current player based on the game state 
        and returns the corresponding Player or Arm object.

        :returns: The current Player object (self.p1 or self.p2).
        """
        pass

    def arm_move(self, pos):
        """
        Execute a move using the robotic arm if the current player is an Arm.

        This method checks if the current player is an Arm and, if so, 
        commands the robotic arm to move a piece to the specified position 
        on the physical board.

        :param pos: The position on the physical board where the piece should be moved.
        """
        obj = self.curr_player_obj()
        if isinstance(obj, Arm):
            pass