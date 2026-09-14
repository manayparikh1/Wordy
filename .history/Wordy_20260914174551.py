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
