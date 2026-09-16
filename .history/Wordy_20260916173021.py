"""
This is called Wordy.

Two word lists are connected alongside this script which include answers.txt and valid_guesses.txt.
- answers.txt will contain approx 3000 common english words that almost everyone knows.
- valid_guesses.txt on the other hand will have around 16000 english words that are also accepted as guesses.
"""

import random 
import time
from collections import Counter
import requests

MAX_GUESSES = 6
WORD_LENGTH = 5

DATAMUSE_URL = "https://api.datamuse.com/words"
DICTIONARY_URL = "https://api.dictionaryapi.dev/api/v2/entries/en"
MIN_WORD_FREQUENCY = 3.0 # the higher the frequency more common words because theres a datamuse of "f" which I learned from MOSh youtube so hopefully this works.

# these are the ansi colours that I have gotten from a website on google called stack overflow

GREEN = "\033[42;30m"  # This means that the letter is in the correct spot
# This means that the letter is in the word but not in the correct spot
YELLOW = "\033[43;30m"
GRAY = "\033[100;37m"  # This means that the letter is not in the word at all

RESET = "\033[0m"  # this makes the colour go back to normal

def fetch_secret_word_pool():
    """
    Ask Datamuse for five letter words. sp=?????" means "5 letters,
    any letters" and each ? is basically a single wildcard slot. "md=f" asks Datamuse to
    also include a frequency score for every single word, so we can throw out
    random ones and only pick a secret one each time from pretty common words.
    """

    params = {"sp": "?" * WORD_LENGTH, "max": 1000, "md": "f"}
    response = requests.get(DATAMUSE_URL, params=params, timeout=10)
    response.raise_for_status()
    common_words = []
    for entry in response.json():
        word = entry["word"].lower()
        if len(word) != WORD_LENGTH or not word.isalpha():
            continue
        frequency = 0.0
        for tag in entry.get("tags", []):
            if tag.startswith("f:"):
                frequency = float(tag[2:])
        if frequency >= MIN_WORD_FREQUENCY:
            common_words.append(word)
    return common_words
# Goes into the POOL of words and it picks out a random one that will meet the requirements
def choose_secret(word_pool):
    return random.choice(word_pool)


def compute_feedback(guess, secret):
    """
    This will return a list of green, yellow, and gray for each letter in guesses. A letter only lights up as many times as it actually appears in the secret word.
    """
    # This is actually really important because it puts the 5 word blocks because word_length is 5
    feedback = ["gray"] * WORD_LENGTH
    remaining = Counter(secret)

    for i in range(WORD_LENGTH):
        if guess[i] == secret[i]:
            feedback[i] = "green"
            remaining[guess[i]] -= 1

    for i in range(WORD_LENGTH):
        if feedback[i] == "green":
            continue
        letter = guess[i]
        if remaining[letter] > 0:
            feedback[i] = "yellow"
            remaining[letter] -= 1

    return feedback

def colorize(letter, status):
    color = {"green": GREEN, "yellow": YELLOW, "gray": GRAY}[status]
    return f"{color} {letter.upper()} {RESET}"

def render_row(guess, feedback):
    return " ".join(colorize(letter, status) for letter, status in zip(guess, feedback))

def render_keyboard(letter_status):
    """Show every single letter on the keyboard and colours each key based on their best guesses so far."""
    rows = ["qwertyuiop", "asdfghjkl", "zxcvbnm"]
    lines = []
    for row in rows :
        tiles = [
        ]
        for letter in row:
            status = letter_status.get(letter)
            if status:
                tiles.append(colorize(letter, status))
            else:
                tiles.append(f" {letter.upper()} ")
        lines.append(" ".join(tiles))
    return "\n".join(lines)

def update_letter_status(letter_status, guess, feedback):

    # the green beats the yellow and the yellow beats the gray so a letter never gets downgraded in the system
    for letter, status in zip(guess, feedback):
        if letter not in letter_status:
            letter_status[letter] = status
            continue
        current_status = letter_status[letter]

        #once a leter is green it stays green no matter what
        if current_status == "green":
            continue
        if status == "green":
            letter_status[letter] = "green"
        #the green basically overwrites what was there and a new yellow only overwrites gray
        elif status == "yellow" and current_status == "gray":
            letter_status[letter] = "yellow"
def is_real_word(word):
    """Ask a real online dictionary whether this word actually exists or not."""
    # Try up to 3 times, since the dictionary service sometimes has a bad
    # moment and just needs a second chance rather than being treated as
    # "not a word."
    for attempt in range(3):
        try:
            response = requests.get(f"{DICTIONARY_URL}/{word}", timeout=10)
        except requests.RequestException:
            time.sleep(1)
            continue

        if response.status_code == 200:
            return True
        if response.status_code == 404:
            # This is the dictionary actually saying "not a word" - trust it.
            return False

        # Anything else (500, 522, 429, etc.) means the SERVICE messed up,
        # not that your word is wrong. Wait a second and try again.
        time.sleep(1)

    # Still no clear answer after 3 tries - the service is probably down.
    # Don't punish the player for that, so let the guess through.
    print("The dictionary seems to be having issues right now, so I'll let this one through.")
    return True
def get_guess():
    while True:
        guess = input(f"\nGuess ({WORD_LENGTH} letters): ").strip().lower()
        if len(guess) != WORD_LENGTH or not guess.isalpha():
            print(f"Enter exactly {WORD_LENGTH} letters.")
            continue
        print("Checking the dictionary gimme a sec...")
        if not is_real_word(guess):
            print(f"'{guess}' isn't in the dictionary sadly so try another word. ")
            continue
        return guess
def play():
    print("Fetching todays word from the dictionary....")
    try:
        word_pool = fetch_secret_word_pool()
    except requests.RequestException:
        print("I could not reach Datamuse --- Can you check your internet connection?")
        return
    if not word_pool:
        print("Did not get any usable words. Sorry. Try running it again.")
        return
    
    secret = choose_secret(word_pool)
    guesses_made = []
    letter_status = {}
    # I just added a visual divider to make it look more neat
    print("=" * 35)
    print("WORDLE")
    print(f"You have {MAX_GUESSES} tries to guess the {WORD_LENGTH}-letter word. You got this.")
    print("=" * 35)

    # THIS will basically be the guesses for example if u guessed apple then visually it would look like this: ("APPLE", ["green","gray","yellow","gray","gray"]),

    for attempt in range(1, MAX_GUESSES + 1):
        guess = get_guess()
        feedback = compute_feedback(guess, secret)
        guesses_made.append((guess, feedback))
        update_letter_status(letter_status, guess, feedback)

        print()
        for g, fb in guesses_made:
            print(render_row(g, fb))
        print()
        print(render_keyboard(letter_status))

        if guess == secret:
            print(f"\nYou got it in {attempt}/{MAX_GUESSES}!")
            return
        remaining = MAX_GUESSES - attempt
        if remaining > 0:
            print(f"\n{remaining} guesses left. You can do this!")
    print(f"\nSorry, the word was '{secret.upper()}'. Better luck next time!")

if __name__ == "__main__":
    play_again = True
    while play_again:
        play()
        again = input("\nWanna play again? (y/n): ").strip().lower()
        play_again = again.startswith("y")
    print("Thank you so much for playing Wordy!!!")