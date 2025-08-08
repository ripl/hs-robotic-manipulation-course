import random
answers=["mission impossible","superman","legally blonde","black panther","tron"]
answer=random.choice(answers)
# player must guess all the letters before making 6 wrong guesses

current=""
for i in range(len(answer)):
    if answer[i:i+1]==" ":
        current+=" "
    else:
        current+="_"

misses=0
playing = True
while playing:
    correct_guess=False
    print("Guess my movie title with fewer than 6 wrong guesses.")
    print(current)
    letter = input("What letter would you like to guess?")
    previous = current
    current = ""
    for i in range(len(answer)):
        if answer[i:i+1]==letter:
            current+=letter
            correct_guess=True
        else:
            current+=previous[i:i+1]
    if not correct_guess:
        misses+=1
        print("Sorry, that guess is not one of the letters.")
        print(f"That is wrong guess #{misses}.")
    if current==answer:
        playing=False
        print("Congratulations! You got it.")
    elif misses==6:
        playing=False
        print("Sorry, you didn't get before making 6 wrong guesses.")
print("It was " + answer + ".")
    
    


