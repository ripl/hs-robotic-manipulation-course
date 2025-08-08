import random
round = 0
playing = True
number = random.randint(1,100)

print("Guess my number between 1 and 100, inclusive.")
while playing:
    round += 1
    print(f"\nRound {round}")
    guess = int(input("Guess: "))
    if guess>number:
        print("Lower")
    elif guess<number:
        print("Higher")
    else:
        print("You got it!")
        playing = False
print(f"You got it in {round} rounds.")