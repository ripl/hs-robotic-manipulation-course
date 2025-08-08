import random
options = ['r','p','s']
# Dictionary  {key:value}
d = {'r':"rock", 'p':"paper", 's':"scissors"}

wins=[0,0]
game_over = False
round = 0

print("\nLet's play rock paper scissors! Best 2 out of 3 wins.")
while not game_over:
    round += 1
    print(f'\nRound {round}:')
    playing = True
    while playing:
        computer = random.choice(options)
        player = input("Choose rock (r), paper (p), or scissors (s): ")
        if ( (computer=='r' and player =='s') or
            (computer=='s' and player =='p') or
            (computer=='p' and player =='r') ):
            print(f'Computer wins because {d[computer]} beats {d[player]}.')
            wins[1] += 1
            playing = False
        elif ( (computer=='s' and player =='r') or
            (computer=='p' and player =='s') or
            (computer=='r' and player =='p') ):
            print(f'Player wins because {d[player]} beats {d[computer]}.')
            wins[0] += 1
            playing = False
        elif computer==player:
            print(f'Tie! Both computer and player chose {d[computer]}.')
        else:
            print("Please type 'r', 'p', or 's'.")
    if wins[0]==2:
        print("\nCongratulations! You beat the computer.")
        game_over=True
    elif wins[1]==2:
        print("\nOh, no! The computer beat you.")
        game_over=True
    else:
        print("\nThe game continues....")
print("\nThanks for playing rock paper scissors.\n")