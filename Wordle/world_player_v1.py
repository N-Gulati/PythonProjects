import collections
import itertools
import random
import csv
import os
import matplotlib.pyplot as plt
import numpy as np
from compute_entropy import ComputeEntropy

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Get the directory of the current script
word_list_path = os.path.join(SCRIPT_DIR, "wordlist_5.csv")
word_freq_path = os.path.join(SCRIPT_DIR, "word_frequencies.txt")
entropy_path = os.path.join(SCRIPT_DIR, "entropy_scores.csv")
weights_path = os.path.join(SCRIPT_DIR, "optimal_weights.txt")

def load_data():
    global WORD_LIST, WORD_FREQUENCY, entropy_scores, w_base, w_positional, w_entropy
    with open(word_list_path) as f:
        WORD_LIST = [word.strip() for word in f if len(word.strip()) == 5]
    print('Loaded Word List')
    # WORD_LIST = random.sample(WORD_LIST, min(100, len(WORD_LIST)))

    # Load word frequency data from a file, if available.
    WORD_FREQUENCY = {}
    try:
        with open(word_freq_path) as f:
            for line in f:
                word, freq = line.strip().split()
                WORD_FREQUENCY[word] = int(freq)
    except FileNotFoundError:
        print("Warning: word_frequencies.txt not found. Frequency weighting will be ignored.")
    
    # Load precomputed entropy scores
    entropy_scores = {}
    try:
        with open(entropy_path, "r") as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for row in reader:
                entropy_scores[row[0]] = float(row[1])
        print("Loaded precomputed entropy scores.")
    except FileNotFoundError:
        print("Warning: entropy_scores.csv not found. Entropy weighting will be ignored.")

    # Load optimal weights
    w_base, w_positional, w_entropy = 0.0, 0.0, 1.0  # Default values
    try:
        with open(weights_path, "r") as f:
            for line in f:
                key, value = line.strip().split("=")
                if key == "w_base":
                    w_base = float(value)
                elif key == "w_positional":
                    w_positional = float(value)
                elif key == "w_entropy":
                    w_entropy = float(value)
        print(f"Loaded optimal weights: w_base={w_base}, w_positional={w_positional}, w_entropy={w_entropy}")
    except FileNotFoundError:
        print("Warning: optimal_weights.txt not found. Using default weights.")
    
    return WORD_LIST, WORD_FREQUENCY, entropy_scores, w_base, w_positional, w_entropy

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

def score_word(remaining_guesses, word, letter_frequencies, positional_frequencies, words, entropy_scores, w_base=0.4, w_positional=0.4, w_entropy=0.2):
    """Score a word based on letter frequency, positional information, uniqueness, and entropy."""
    base_score = sum(letter_frequencies[c] for c in set(word))  
    positional_score = sum(positional_frequencies[i][c] for i, c in enumerate(word))
    uniqueness_penalty = (len(set(word)) / len(word)) ** 1.5  # Adjusted penalty for duplicate letters

    entropy_score = entropy_scores.get(word, 0)  # Use precomputed entropy if available
    
    return (w_base * base_score) + (w_positional * positional_score) * uniqueness_penalty + (w_entropy * entropy_score)

def best_guess(words, remaining_guesses, entropy_scores, last_feedback=None, w_base=0.4, w_positional=0.4, w_entropy=0.2):
    """Return the best word to guess based on scoring criteria."""
    letter_frequencies = get_letter_frequencies(words)
    positional_frequencies = compute_positional_frequencies(words)
    if remaining_guesses != 6:
        entropy_scores = compute_entropy_instance.compute_entropy_scores(words, multi = 1)
    return max(words, key=lambda word: score_word(remaining_guesses, word, letter_frequencies, positional_frequencies, words, entropy_scores, w_base, w_positional, w_entropy)) 

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
        guess = best_guess(words, remaining_guesses, entropy_scores)
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
    WORD_LIST, WORD_FREQUENCY, entropy_scores, w_base, w_positional, w_entropy = load_data()
    compute_entropy_instance = ComputeEntropy()  # ✅ Initialize globally
    wordle_solver()
