import collections
import itertools
import random
import csv
import os
import matplotlib.pyplot as plt
import numpy as np

# Get the directory of the current script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Load a word list from a file containing five-letter words.
word_list_path = os.path.join(SCRIPT_DIR, "wordlist_5.csv")
with open(word_list_path) as f:
    WORD_LIST = [word.strip() for word in f if len(word.strip()) == 5]

# Load word frequency data from a file, if available.
WORD_FREQUENCY = {}
word_freq_path = os.path.join(SCRIPT_DIR, "word_frequencies.txt")
try:
    with open(word_freq_path) as f:
        for line in f:
            word, freq = line.strip().split()
            WORD_FREQUENCY[word] = int(freq)
except FileNotFoundError:
    print("Warning: word_frequencies.txt not found. Frequency weighting will be ignored.")

def get_letter_frequencies(words):
    """Compute letter frequency across all remaining words."""
    return collections.Counter(itertools.chain.from_iterable(words))

def compute_positional_frequencies(words):
    """Compute the frequency of letters in each position (0-4) across all remaining words."""
    positional_freq = [collections.Counter() for _ in range(5)]
    for word in words:
        for i, letter in enumerate(word):
            positional_freq[i][letter] += 1
    return positional_freq

def score_word(word, letter_frequencies, positional_frequencies):
    """Score a word based on letter frequency, positional information, and uniqueness."""
    
    # Score based on how common each letter is
    base_score = sum(letter_frequencies[c] for c in set(word))  
    
    # Positional frequency score: Words that match high-frequency positions are preferred
    positional_score = sum(positional_frequencies[i][c] for i, c in enumerate(word))
    
    # Penalize words with duplicate letters since they provide less new information
    uniqueness_penalty = len(set(word)) / len(word)  # Closer to 1 for unique words, lower for repeats
    
    return (base_score * 0.5) + (positional_score * 0.5) * uniqueness_penalty

def best_guess(words, remaining_guesses, last_feedback=None):
    """Return the best word to guess based on scoring criteria."""
    letter_frequencies = get_letter_frequencies(words)
    positional_frequencies = compute_positional_frequencies(words)
    return max(words, key=lambda word: score_word(word, letter_frequencies, positional_frequencies))

def filter_words(words, guess, result):
    """Filter words based on feedback from Wordle (G = green, Y = yellow, B = black/gray)."""
    new_words = []
    for word in words:
        match = True
        for i, (g_letter, r) in enumerate(zip(guess, result)):
            if (r == 'G' and word[i] != g_letter) or \
               (r == 'Y' and (g_letter not in word or word[i] == g_letter)) or \
               (r == 'B' and g_letter in word and guess.count(g_letter) <= result.count("B")):
                match = False
                break
        if match:
            new_words.append(word)
    return new_words

def wordle_solver():
    """Interactively solve Wordle by making and refining guesses based on user feedback."""
    words = WORD_LIST.copy()
    remaining_guesses = 6
    while True:
        guess = best_guess(words, remaining_guesses)
        print(f"Try guessing: {guess}")
        user_input = input("Enter result (G = green, Y = yellow, B = black/gray) or 'N' for next guess: ").upper()
        
        if user_input == 'N':
            words.remove(guess)
            remaining_guesses -= 1
            if not words:
                print("No words left to suggest.")
                return
            continue
        elif user_input == "GGGGG":
            print(f"Wordle solved! The word was {guess}.")
            return
        else:
            words = filter_words(words, guess, user_input)
            remaining_guesses -= 1
            if not words:
                print("No words left. Check input.")
                return

# modify/lift from this to store results from user game into results file called user_results.csv
# def store_simulation_results(filename="simulation_results.csv", num_simulations=100):
#     """Run multiple simulations and store results in a CSV file."""
#     with open(filename, "w", newline="") as csvfile:
#         writer = csv.writer(csvfile)
#         writer.writerow(["answer", "guess1", "guess2", "guess3", "guess4", "guess5", "guess6", "attempts"])
#         for _ in range(num_simulations):
#             answer, guesses, attempts = simulate_game()
#             row = [answer] + guesses + ["" for _ in range(6 - len(guesses))] + [attempts]
#             writer.writerow(row)

if __name__ == "__main__":
    wordle_solver()
