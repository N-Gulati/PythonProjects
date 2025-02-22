import collections
import itertools
import random
import csv
import os
import matplotlib.pyplot as plt
import numpy as np
from math import log2

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

def compute_entropy(word, words):
    """Compute the entropy of a given word based on feedback patterns."""
    feedback_patterns = collections.defaultdict(int)
    
    for possible_word in words:
        pattern = "".join(
            "G" if word[i] == possible_word[i] else
            "Y" if word[i] in possible_word else "B"
            for i in range(5)
        )
        feedback_patterns[pattern] += 1
    
    total_patterns = sum(feedback_patterns.values())
    entropy = -sum((count / total_patterns) * log2(count / total_patterns) for count in feedback_patterns.values())
    return entropy

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

def score_word(word, letter_frequencies, positional_frequencies, words, w_base=0.4, w_positional=0.4, w_entropy=0.2):
    """Score a word based on letter frequency, positional information, uniqueness, and entropy."""
    base_score = sum(letter_frequencies[c] for c in set(word))  
    positional_score = sum(positional_frequencies[i][c] for i, c in enumerate(word))
    uniqueness_penalty = (len(set(word)) / len(word)) ** 1.5  # Adjusted penalty for duplicate letters
    entropy_score = compute_entropy(word, words)  # New entropy-based scoring
    
    return (w_base * base_score) + (w_positional * positional_score) * uniqueness_penalty + (w_entropy * entropy_score)

def best_guess(words, remaining_guesses, last_feedback=None, w_base=0.4, w_positional=0.4, w_entropy=0.2):
    """Return the best word to guess based on scoring criteria."""
    letter_frequencies = get_letter_frequencies(words)
    positional_frequencies = compute_positional_frequencies(words)
    return max(words, key=lambda word: score_word(word, letter_frequencies, positional_frequencies, words, w_base, w_positional, w_entropy))

def evaluate_weights(w_base, w_positional, w_entropy, num_simulations=50):
    """Evaluate the average number of guesses required for a given weighting."""
    total_attempts = 0
    valid_simulations = 0
    
    for _ in range(num_simulations):
        _, _, attempts = simulate_game(w_base, w_positional, w_entropy)
        if attempts > 0:  # Ignore failed games
            total_attempts += attempts
            valid_simulations += 1
    
    return total_attempts / valid_simulations if valid_simulations > 0 else float('inf')

def simulate_game(w_base=0.4, w_positional=0.4, w_entropy=0.2):
    """Simulate a game of Wordle by selecting a random word and solving it."""
    answer = random.choice(WORD_LIST)
    words = WORD_LIST.copy()
    remaining_guesses = 6
    guesses = []
    for _ in range(6):
        guess = best_guess(words, remaining_guesses, w_base=w_base, w_positional=w_positional, w_entropy=w_entropy)
        guesses.append(guess)
        if guess == answer:
            return answer, guesses, len(guesses)
        result = "".join("G" if guess[i] == answer[i] else ("Y" if guess[i] in answer else "B") for i in range(5))
        words = filter_words(words, guess, result)
    return answer, guesses, 0  # 0 indicates failure

if __name__ == "__main__":
    best_w_base, best_w_positional, best_w_entropy = optimize_weights()
    print(f"Optimized weights: w_base={best_w_base}, w_positional={best_w_positional}, w_entropy={best_w_entropy}") 
