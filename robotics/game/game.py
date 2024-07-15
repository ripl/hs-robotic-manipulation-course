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
