import pygame
import sys
import random
players=["R","Y"]
random.shuffle(players)
names=["Player", "Computer"]

width = 784
height = 700
size = 108
offset = 120
game_height = height + offset
the_ys = [0,0,0,0,0,0]
the_xs = [0,0,0,0,0,0,0]
locations = []
h = 8 + offset
for i in range(6):
    row=[]
    w = 2
    for j in range(7):
        row.append((w,h))
        w += 112
    locations.extend(row)
    h += 117
for i in range(6):
    the_ys[5-i]=(590 + offset) - 117*i
for j in range(7):
    the_xs[j]=2+112*j

board = []
k=0
for i in range(6):
    row = []
    for j in range(7):
        row.append(" ")
        k+=1
    board.append(row)

def print_board():
    for i in range(6):
        print(board[i])

def find_sequence_old(nums,token,seq_length):
    """
    Given a list nums with length larger than seq_length,
    return True if there is a sequence of tokens of 
    length seq_length, and return False otherwise
    Note: token is either "R" or "Y", not " ".
    Note: seq_length will be either 2 or 3
    """
    if len(nums)<seq_length:
        return False
    if seq_length==3:
        for i in range(len(nums)-2):
            if nums[i]==nums[i+1]==nums[i+2]==token:
                return True
    elif seq_length==2:
        for i in range(len(nums)-1):
            if nums[i]==nums[i+1]==token:
                return True           
    return False

def find_sequence(nums,token,seq_length):
    """
    Given a list nums with length larger than seq_length,
    return True if there is a sequence of tokens of 
    length seq_length, and return False otherwise
    Note: token is either "R" or "Y", not " ".
    Note: seq_length will be either 2 or 3
    """
    if len(nums)<seq_length:
        return False
    count = 0
    for i in range(len(nums)-1):
        if nums[i]==nums[i+1]==token:
            count+=1
            if seq_length==2:
                return True
            if count==2 and seq_length==3:
                return True
        else:
            count=0
    return False        

def get_diagonals():
    diags=[ [board[3][0],board[2][1],board[1][2],board[0][3]],
            [board[4][0],board[3][1],board[2][2],board[1][3],board[0][4]],
            [board[5][0],board[4][1],board[3][2],board[2][3],board[1][4],board[0][5]],
            [board[5][1],board[4][2],board[3][3],board[2][4],board[1][5],board[0][6]],
            [board[5][2],board[4][3],board[3][4],board[2][5],board[1][6]],
            [board[5][3],board[4][4],board[3][5],board[2][6]],
            [board[0][3],board[1][4],board[2][5],board[3][6]],
            [board[0][2],board[1][3],board[2][4],board[3][5],board[4][6]],
            [board[0][1],board[1][2],board[2][3],board[3][4],board[4][5],board[5][6]],
            [board[0][0],board[1][1],board[2][2],board[3][3],board[4][4],board[5][5]],
            [board[1][0],board[2][1],board[3][2],board[4][3],board[5][4]],
            [board[2][0],board[3][1],board[4][2],board[5][3]] ]
    return diags

def count_sequence(token,seq_length):
    count = 0
    for row in board:
        if find_sequence(row,token,seq_length):
            count+=1
    for j in range(7):
        col = []
        for i in range(6):
            col.append(board[i][j])
        if find_sequence(col,token,seq_length):
            count+=1 
    diags=get_diagonals()
    for diag in diags:     
        if find_sequence(diag,token,seq_length):
            count+=1
    return count

def utility_value():
    human_count3 = count_sequence(players[0],3)
    human_count2 = count_sequence(players[0],2)
    ai_count3 = count_sequence(players[1],3)
    ai_count2 = count_sequence(players[1],2)
    human_score=1000*human_count3+100*human_count2
    ai_score=1000*ai_count3+100*ai_count2
    return ai_score - human_score

def check_win(nums):
    for i in range(len(nums)-3):
        if (nums[i]==nums[i+1]==nums[i+2]==nums[i+3] and
           nums[i]!=" "):
           return nums[i]
    return "N"

def find_winner():
    for row in board:
        win = check_win(row)
        if win!="N":
            return win
    for j in range(7):
        col = []
        for i in range(6):
            col.append(board[i][j])
        win = check_win(col)
        if win!="N":
            return win
    diags = get_diagonals()
    for diag in diags:
        #print(diag)      
        win = check_win(diag)
        if win!="N":
            return win            
    return "N"

def board_is_full():
    for i in range(7):
        if board[0][i]==" ":
            return False
    return True

def get_possible_plays():
    plays=[]
    for j in range(7):
        if board[0][j]==" ":
            plays.append(j)
    return plays 

def update_board(play,token):
    found_row = False
    j=5
    while not found_row:
        if board[j][play] == " ":
            board[j][play] = token
            found_row = True
        else:
            j-=1
    return j    

def minimax(is_maximizing, maximizing_player, depth):
    """
    Minimax algorithm implementation
    Returns the best score possible for the current board state
    """
    ai_player = players[maximizing_player]
    human_player = players[(maximizing_player+1)%2]
    # Base cases
    winner = find_winner()
    if winner == ai_player:
        return float("inf")
    if winner == human_player:
        return float("-inf")
    if board_is_full():
        return 0
    if depth == 4:
        return utility_value()

    # minimax algorithm
    plays = get_possible_plays()
    if is_maximizing:
       best_score = float("-inf")
       for play in plays:
           # Make a calculating move
           j = update_board(play,ai_player)
           # Recursively call minimax 
           # with the next depth and the minimizing player
           score = minimax(False, maximizing_player, depth + 1)
           # Reset the move
           board[j][play] = " "
           # Update the best score
           best_score = max(score, best_score)
       return best_score
    else:
       # if it is the minimizing player's turn (human), 
       # we want to minimize the score
       best_score = float("inf")
       for play in plays:
           # Make a calculating move
           j = update_board(play,human_player)
           # Recursively call minimax with 
           # the next depth and the maximizing player
           score = minimax(True, maximizing_player, depth + 1)
           # Reset the move
           board[j][play] = " "
           # Update the best score
           best_score = min(score, best_score)
       return best_score

def get_computer_play(i) -> int:
    intelligence = 2
    plays=get_possible_plays()
    random.shuffle(plays)
    if intelligence == 0:
        return random.choice(plays)
    elif intelligence == 1:
        # Win if we can win
        for play in plays:
            j = update_board(play,players[i])
            if find_winner() == players[i]:
                board[j][play] = " "
                return play
            board[j][play]=" "
        k = (i + 1) % 2
        # Block if we can't win
        for play in plays:
            j = update_board(play,players[k])
            if find_winner() == players[k]:
                board[j][play] = " "
                return play
            board[j][play] = " "
        # Otherwise random
        return random.choice(plays)
    else:
        best_score = float("-inf")
        best_move = plays[0]
        for play in plays:
            j = update_board(play,players[i])
            score = minimax(False, i, 0)
            board[j][play]=" "
            if score >= best_score:
               best_score = score
               best_move = play
        return best_move

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((width,game_height))
font = pygame.font.Font(None, 50)
bgo_surface = pygame.image.load("board_c4_transparent.png")
bg_overlay = pygame.transform.scale(bgo_surface, (width, height))
surface1 = pygame.image.load("Red.png")
player1 = pygame.transform.scale(surface1, (size, size))
surface2 = pygame.image.load("Yellow.png")
player2 = pygame.transform.scale(surface2, (size, size))

if players[0]=="R":
    pieces=[player1,player2]
    colors=["red","yellow"]
else:
    pieces=[player2,player1]
    colors=["yellow","red"]

surface1 = font.render(f'{names[0]}, your turn.', True, colors[0])
surface2 = font.render(f'{names[1]}, your turn.', True, colors[1])
surfaces=[surface1,surface2]

def move_token_into_position(i,j,play):
    x = the_xs[play]
    y_0 = offset-60
    y_final = the_ys[j]
    delta_y = 30
    steps = int((y_final-y_0)/delta_y)
    y = y_0
    for k in range(steps):
        pygame.draw.rect(screen,'gray',(x,y,size+8,size+8))
        y += delta_y
        screen.blit(pieces[i],(x,y))
        screen.blit(bg_overlay,(0,offset))
        pygame.time.delay(15)
        pygame.display.flip()

def update():
    pygame.draw.rect(screen,'gray',(0,0,width,game_height))
    screen.blit(message_surface,(235,15)) 
    j=0
    for row in board:
        for spot in row:
            if spot==players[0]:
                screen.blit(pieces[0],locations[j])
            elif spot==players[1]:
                screen.blit(pieces[1],locations[j])
            j+=1
    screen.blit(bg_overlay,(0,offset))
    pygame.display.flip()

running = True
playing = True
quit = False
i=0  # turns
while running:
    clock.tick(60)
    while playing:
        message_surface=surfaces[i]
        play=-1
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                playing = False
                quit = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # left click
                    mouse_pos = pygame.mouse.get_pos()
                    play = int((mouse_pos[0])/112)                  
        if names[i]=="Computer":
            update()
            #pygame.time.delay(100)
            play = get_computer_play(i) 
        if play!=-1:
            j=update_board(play,players[i])
            move_token_into_position(i,j,play)
            play=-1
            i = (i + 1) % 2
        update()
        #print_board()
        winner = find_winner()
        if winner!="N" or board_is_full():
            playing = False
    if winner!="N":
        if winner==players[0]:
            message_surface=font.render(
                f'{names[0]}, you won!', True, colors[0])
        else:
            message_surface=font.render(
                f'{names[1]}, you won!', True, colors[1])
    else:
        message_surface=font.render(
            "It's a tie.", True, "black")
    if not quit:
        update()
        pygame.time.delay(3000)
    running = False
pygame.quit()
sys.exit()
