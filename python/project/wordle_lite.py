import random

def game_over(secret, guess, score):
    """
    Check if the game is over.

    Inputs:
    secret (str): The secret word.
    guess (str): The guessed word.
    score (int): The current score of Player 2.

    Returns:
    bool: True if the game is over (either guessed correctly or score is zero or below), False otherwise.
    """
    pass

def matching_slots(secret, guess):
    """
    Compare the guessed word with the secret word and return a string showing matching letters.

    Inputs:
    secret (str): The secret word.
    guess (str): The guessed word.

    Returns:
    str: A string of the same length as the secret word, where each position contains the matching letter or '-' if not matching.
    """
    pass

def update_score(current_score, matched_slots):
    """
    Update the score based on the number of matched slots.

    Inputs:
    current_score (int): The current score of Player 2.
    matched_slots (str): The result of the matching slots comparison.

    Returns:
    int: The updated score.
    """
    pass

def main():
    print("Welcome to Wordle™-lite, a word guessing game.")
    secret_word = input("Player 1, enter a secret word: ")
    
    print("Player 2: Time to guess the secret word; you start with a score of 100.")

    print("Wrong guesses cost you 10 but each matched letter earns back 1.")

    print("The game ends when you guess the word or the score gets to 0.")

    player_2_score = 100
    
    while True:
        print(f"\nWhat is your guess? (hint: it's a {len(secret_word)}-letter word)")
        guess_word = input("Player 2: ").lower()
        
        feedback = matching_slots(secret_word, guess_word)
        player_2_score = update_score(player_2_score, feedback)
        
        if game_over(secret_word, guess_word, player_2_score):
            if guess_word == secret_word:
                print(f"'{secret_word}' is correct, great job! Final score: {player_2_score}")
            else:
                print(f"Game over! The secret word was '{secret_word}'. Final score: {player_2_score}")
            break
        else:
            print(f"Player 2: your guess of '{guess_word}' matched {feedback}; your score is now {player_2_score}.")

if __name__ == "__main__":
    main()
