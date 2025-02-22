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

def score_word(word, letter_frequencies, positional_frequencies, w_base=0.5, w_positional=0.5):
    """Score a word based on letter frequency, positional information, and uniqueness with dynamic weighting."""
    
    base_score = sum(letter_frequencies[c] for c in set(word))  
    positional_score = sum(positional_frequencies[i][c] for i, c in enumerate(word))
    
    uniqueness_penalty = (len(set(word)) / len(word)) ** 2   # Closer to 1 for unique words, lower for repeats
    
    return (w_base * base_score) + (w_positional * positional_score) * uniqueness_penalty

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

def best_guess(words, remaining_guesses, last_feedback=None, w_base=0.5, w_positional=0.5):
    """Return the best word to guess based on scoring criteria."""
    letter_frequencies = get_letter_frequencies(words)
    positional_frequencies = compute_positional_frequencies(words)
    return max(words, key=lambda word: score_word(word, letter_frequencies, positional_frequencies, w_base, w_positional))

def evaluate_weights(w_base, w_positional, num_simulations=50):
    """Evaluate the average number of guesses required for a given weighting."""
    total_attempts = 0
    valid_simulations = 0
    
    for _ in range(num_simulations):
        _, _, attempts = simulate_game(w_base, w_positional)
        if attempts > 0:  # Ignore failed games
            total_attempts += attempts
            valid_simulations += 1
    
    return total_attempts / valid_simulations if valid_simulations > 0 else float('inf')  # Avoid division by zero

def store_optimal_weights(w_base, w_positional):
    """Store the optimal weights in a file."""
    weights_path = os.path.join(SCRIPT_DIR, "optimal_weights.txt")
    with open(weights_path, "w") as f:
        f.write(f"w_base={w_base:.2f}\n")
        f.write(f"w_positional={w_positional:.2f}\n")
    print(f"Optimal weights saved to {weights_path}")

def optimize_weights():
    """Optimize the weighting of base score and positional score using Grid Search."""
    best_w_base, best_w_positional = 0, 0
    best_avg_guesses = float('inf')

    weight_range = np.linspace(0, 1, 11)  # Generate values from 0 to 1 in steps of 0.1

    for w_base in weight_range:
        w_positional = 1 - w_base  # Ensure the sum is always 1
        avg_guesses = evaluate_weights(w_base, w_positional, num_simulations=50)
        
        print(f"Testing w_base={w_base:.2f}, w_positional={w_positional:.2f} -> Avg Guesses: {avg_guesses:.2f}")
        
        if avg_guesses < best_avg_guesses:
            best_avg_guesses = avg_guesses
            best_w_base, best_w_positional = w_base, w_positional

    print(f"Optimal Weights: w_base={best_w_base:.2f}, w_positional={best_w_positional:.2f} with {best_avg_guesses:.2f} guesses on average")
    store_optimal_weights(best_w_base, best_w_positional)
    return best_w_base, best_w_positional

def simulate_game(w_base=0.5, w_positional=0.5):
    """Simulate a game of Wordle by selecting a random word and solving it."""
    answer = random.choice(WORD_LIST)
    words = WORD_LIST.copy()
    remaining_guesses = 6
    guesses = []
    for _ in range(6):
        guess = best_guess(words, remaining_guesses, w_base=w_base, w_positional=w_positional)
        guesses.append(guess)
        if guess == answer:
            return answer, guesses, len(guesses)
        result = "".join("G" if guess[i] == answer[i] else ("Y" if guess[i] in answer else "B") for i in range(5))
        words = filter_words(words, guess, result)
    return answer, guesses, 0  # 0 indicates failure

if __name__ == "__main__":
    best_w_base, best_w_positional = optimize_weights()
    print(f"Optimized weights: w_base={best_w_base}, w_positional={best_w_positional}")
