import random
# file of state capitals from 
# https://www.britannica.com/topic/list-of-state-capitals-in-the-United-States-2119210

lines = []
with open("state_capitals.csv") as file:
    for line in file: 
        line = line.strip() #or some other preprocessing
        lines.append(line) #storing everything in memory!

state_capitals={}
for line in lines:
    pair=line.split(",")
    state_capitals[pair[0]] = pair[1]

print("\nWelcome to state capitals quiz!")
print("I will quiz you on the capitals of 10 states.")
score = 0
for i in range(10):
    state=random.choice(list(state_capitals.keys()))
    capital=state_capitals[state]
    del state_capitals[state]
    answer = input(f"\nWhat is the capital of {state}? ")
    if answer==capital:
        print("\nYes! You got it.")
        score+=1
    else:
        print(f"\nAlas, no, it was {capital}.")
print(f"\nYou got {score} out of 10.\n")