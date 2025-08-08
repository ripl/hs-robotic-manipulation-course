import random
# file of elements from https://www.bodycote.com/list-chemical-symbols/

lines = []
with open("elements.csv") as file:
    for line in file: 
        line = line.strip() #or some other preprocessing
        lines.append(line) #storing everything in memory!

elements={}
for line in lines:
    pair=line.split(",")
    elements[pair[0]] = pair[1]

print("\nWelcome to element symbol quiz!")
print("I will quiz you on 10 elements.")
score = 0
for i in range(10):
    symbol=random.choice(list(elements.keys()))
    name=elements[symbol]
    del elements[symbol]
    answer = input(f"\nWhat is the symbol for {name}? ")
    if answer==symbol:
        print("\nYes! You got it.")
        score+=1
    else:
        print(f"\nAlas, no, it was {symbol}.")
print(f"\nYou got {score} out of 10.\n")