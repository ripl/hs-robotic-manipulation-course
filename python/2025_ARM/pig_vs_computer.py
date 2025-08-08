import random

def get_computer_choice(total_for_round,which_roll_number):
    if total_for_round>=15 or which_roll_number>=4:
        return 'b'
    return 'r'

score = [0,0]
names = ["Player 1", "Computer"]
round = 0
playing = True
print("Let's play pig! Try to bank 100 points or more. If you roll a 1 you lose your round total.")

while playing:
    round = round + 1
    print(f'\nRound {round}:')
    for i in range(2):
        round_total = 0
        print(f'\n{names[i]}, your turn.')
        rolling = True
        roll_number = 0
        while rolling:
            roll_number = roll_number + 1
            print(f'Your total score would be {score[i]+round_total} if you banked.')
            if i==0:  # human player
                choice = input("Would you like to roll (r) or bank (b)? ")
            else:     # computer player
                choice = get_computer_choice(round_total,roll_number)
            if choice == 'r':
                print(f'You chose to roll. This is roll number {roll_number}.')
                die_roll = random.randint(1,6)
                print(f'You rolled a {die_roll}.')
                if die_roll != 1:
                    round_total = round_total + die_roll
                    print(f'Your new round total is {round_total}.')
                else:
                    rolling = False
            elif choice == 'b':
                print('You chose to bank.')
                score[i] = score[i] + round_total
                rolling = False
            else:
                print("Please choose 'r' or 'b'")
        if (score[i]>=100):
            playing = False
print(f'{names[0]}: You banked {score[0]} points in {round} rounds.')
print(f'{names[1]}: You banked {score[1]} points in {round} rounds.')
if score[0]>score[1]:
    print(f'{names[0]}, you won!')
elif score[1]>score[0]:
    print(f'{names[1]}, you won!')
else:
    print("Whoa! Cool! It's a tie. You both won!")
