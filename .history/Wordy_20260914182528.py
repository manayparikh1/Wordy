"""
This is called Wordy.

Two word lists are connected alongside this script which include answers.txt and valid_guesses.txt.
- answers.txt will contain approx 3000 common english words that almost everyone knows.
- valid_guesses.txt on the other hand will have around 16000 english words that are also accepted as guesses.
"""

import random
from collections import Counter
from pathlib import Path

MAX_GUESSES = 6
WORD_LENGTH = 5

# these are the ansi colours that I have gotten from a website on google called stack overflow

GREEN = "\033[42;30m"  # This means that the letter is in the correct spot
# This means that the letter is in the word but not in the correct spot
YELLOW = "\033[43;30m"
GRAY = "\033[100;37m"  # This means that the letter is not in the word at all

RESET = "\033[0m"  # this makes the colour go back to normal

DATA_DIR = Path(__file__).resolve().parent


def load_word_list(filename):
    path = DATA_DIR / filename
    with open(path) as f:
        return {line.strip().lower() for line in f if line.strip()}
# This goes into the file and pulls out a random word


def choose_secret(answers):
    return random.choice(list(answers))


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
        