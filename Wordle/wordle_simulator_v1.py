import collections
import itertools
import random
import csv
import os
import matplotlib.pyplot as plt
import numpy as np
from compute_entropy import ComputeEntropy
from multiprocessing import Pool, cpu_count

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

def simulate_game(WORD_LIST, WORD_FREQUENCY, entropy_scores, w_base=0.4, w_positional=0.4, w_entropy = 0.2):
    """Simulate a game of Wordle by selecting a random word and solving it."""
    answer = random.choice(WORD_LIST)
    words = WORD_LIST.copy()
    remaining_guesses = 6
    guesses = []
    for _ in range(6):
        guess = best_guess(words, remaining_guesses, entropy_scores)
        guesses.append(guess)
        if guess == answer:
            return answer, guesses, len(guesses)
        result = "".join("G" if guess[i] == answer[i] else ("Y" if guess[i] in answer else "B") for i in range(5))
        words = filter_words(words, guess, result)
        entropy_scores = compute_entropy_instance.compute_entropy_scores(words, multi = 0)
    return answer, guesses, 0  # 0 indicates failure

# def simulate(args):
#     """Run a single game simulation and return the number of attempts."""
#     return simulate_game(*args)[2]  # Return only the number of attempts

# def init_worker_entropy():
#     """Initialize compute_entropy_instance for multiprocessing workers."""
#     global compute_entropy_instance
#     compute_entropy_instance = ComputeEntropy()

# def evaluate_weights_parallel(WORD_LIST, WORD_FREQUENCY, entropy_scores, w_base, w_positional, w_entropy, num_simulations=50):
#     """Evaluate the average number of guesses required for a given weighting using multiprocessing."""
    
#     with Pool(cpu_count(), initializer=init_worker_entropy, initargs=()) as pool:
#         attempts = pool.map(simulate, [(WORD_LIST, WORD_FREQUENCY, entropy_scores, w_base, w_positional, w_entropy) for _ in range(num_simulations)])

#     valid_attempts = [a for a in attempts if a > 0]
#     return sum(valid_attempts) / len(valid_attempts) if valid_attempts else float('inf')

def store_simulation_results(WORD_LIST, WORD_FREQUENCY, entropy_scores, w_base=0.4, w_positional=0.4, w_entropy = 0.2, filename="simulation_results.csv", num_simulations=100):
    """Run multiple simulations and store results in a CSV file."""
    with open(filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["answer", "guess1", "guess2", "guess3", "guess4", "guess5", "guess6", "attempts"])
        for _ in range(num_simulations):
            answer, guesses, attempts = simulate_game(WORD_LIST, WORD_FREQUENCY, entropy_scores, w_base, w_positional, w_entropy)
            row = [answer] + guesses + ["" for _ in range(6 - len(guesses))] + [attempts]
            writer.writerow(row)

def generate_histogram():
    """Generate a histogram of the number of attempts required to solve Wordle."""
    results_path = os.path.join(SCRIPT_DIR, "simulation_results.csv")
    if not os.path.exists(results_path):
        print("Error: simulation_results.csv not found.")
        return
    
    attempts = []
    with open(results_path, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if int(row["attempts"]) > 0:  # Exclude failed games
                attempts.append(int(row["attempts"]))
    
    if not attempts:
        print("No valid attempts found in the results.")
        return
    
    mean_attempts = np.mean(attempts)
    median_attempts = np.median(attempts)
    
    plt.figure(figsize=(8, 6))
    plt.hist(attempts, bins=range(1, 8), edgecolor='black', alpha=0.7)
    plt.axvline(mean_attempts, color='red', linestyle='dashed', linewidth=2, label=f'Mean: {mean_attempts:.2f}')
    plt.axvline(median_attempts, color='blue', linestyle='dashed', linewidth=2, label=f'Median: {median_attempts:.2f}')
    plt.xlabel("Number of Attempts")
    plt.ylabel("Frequency")
    plt.title("Histogram of Wordle Solver Performance")
    plt.legend()
    
    histogram_path = os.path.join(SCRIPT_DIR, "wordle_solver_histogram.png")
    plt.savefig(histogram_path)
    plt.close()
    print(f"Histogram saved as {histogram_path}")

if __name__ == "__main__":
    WORD_LIST, WORD_FREQUENCY, entropy_scores, w_base, w_positional, w_entropy = load_data()
    compute_entropy_instance = ComputeEntropy()  # ✅ Initialize globally
    store_simulation_results(WORD_LIST, WORD_FREQUENCY, entropy_scores, w_base, w_positional, w_entropy, num_simulations=200)
    generate_histogram()
