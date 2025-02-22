import collections
import itertools
import random
import csv
import os
import matplotlib.pyplot as plt
import numpy as np
from multiprocessing import Pool, cpu_count
from compute_entropy import ComputeEntropy

# Get the directory of the current script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Load a word list from a file containing five-letter words.
word_list_path = os.path.join(SCRIPT_DIR, "wordlist_5.csv")
word_freq_path = os.path.join(SCRIPT_DIR, "word_frequencies.txt")
entropy_path = os.path.join(SCRIPT_DIR, "entropy_scores.csv")

def load_data():
    global WORD_LIST, WORD_FREQUENCY, entropy_scores
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
    
    return WORD_LIST, WORD_FREQUENCY, entropy_scores

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

# def compute_entropy(word, words):
#     """Compute the entropy of a given word based on feedback patterns."""
#     # feedback_patterns = collections.defaultdict(int)
    
#     # for possible_word in words:
#     #     pattern = "".join(
#     #         "G" if word[i] == possible_word[i] else
#     #         "Y" if word[i] in possible_word else "B"
#     #         for i in range(5)
#     #     )
#     #     feedback_patterns[pattern] += 1
    
#     # total_patterns = sum(feedback_patterns.values())
#     # entropy = -sum((count / total_patterns) * np.log2(count / total_patterns) for count in feedback_patterns.values())
#     # return entropy

#     Compute_Entropy.(word, words)

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

# def evaluate_weights(w_base, w_positional, w_entropy, num_simulations=50):
#     """Evaluate the average number of guesses required for a given weighting."""
#     # print(f'Evaluating {w_base} {w_positional} {w_entropy}')
#     total_attempts = 0
#     valid_simulations = 0
#     cnt = 0 
#     for _ in range(num_simulations):
#         cnt += 1
#         # print(f'Starting simulation {cnt} of {num_simulations}')
#         _, _, attempts = simulate_game(w_base, w_positional, w_entropy)
#         if attempts > 0:  # Ignore failed games
#             total_attempts += attempts
#             valid_simulations += 1
#         # print('Completed Simulation')
    
#     return total_attempts / valid_simulations if valid_simulations > 0 else float('inf')  # Avoid division by zero

def simulate_game(WORD_LIST, WORD_FREQUENCY, entropy_scores, w_base=0.4, w_positional=0.4, w_entropy = 0.2):
    """Simulate a game of Wordle by selecting a random word and solving it."""
    global compute_entropy_instance

    if compute_entropy_instance is None:
        compute_entropy_instance = ComputeEntropy()  # ✅ Instantiate correctly

    answer = random.choice(WORD_LIST)
    words = WORD_LIST.copy()
    remaining_guesses = 6
    guesses = []
    for _ in range(6):
        guess = best_guess(words, remaining_guesses, entropy_scores, w_base=w_base, w_positional=w_positional,  w_entropy= w_entropy)
        remaining_guesses -= 1
        guesses.append(guess)
        if guess == answer:
            return answer, guesses, len(guesses)
        result = "".join("G" if guess[i] == answer[i] else ("Y" if guess[i] in answer else "B") for i in range(5))
        words = filter_words(words, guess, result)
        entropy_scores = compute_entropy_instance.compute_entropy_scores(words, multi = 0)
    return answer, guesses, 0  # 0 indicates failure

def simulate(args):
    """Run a single game simulation and return the number of attempts."""
    return simulate_game(*args)[2]  # Return only the number of attempts

def init_worker_entropy():
    """Initialize compute_entropy_instance for multiprocessing workers."""
    global compute_entropy_instance
    compute_entropy_instance = ComputeEntropy()

def evaluate_weights_parallel(WORD_LIST, WORD_FREQUENCY, entropy_scores, w_base, w_positional, w_entropy, num_simulations=50):
    """Evaluate the average number of guesses required for a given weighting using multiprocessing."""
    
    with Pool(cpu_count(), initializer=init_worker_entropy, initargs=()) as pool:
        attempts = pool.map(simulate, [(WORD_LIST, WORD_FREQUENCY, entropy_scores, w_base, w_positional, w_entropy) for _ in range(num_simulations)])

    valid_attempts = [a for a in attempts if a > 0]
    return sum(valid_attempts) / len(valid_attempts) if valid_attempts else float('inf')


def store_optimal_weights(w_base, w_positional, w_entropy):
    """Store the optimal weights in a file."""
    weights_path = os.path.join(SCRIPT_DIR, "optimal_weights.txt")
    with open(weights_path, "w") as f:
        f.write(f"w_base={w_base:.2f}\n")
        f.write(f"w_positional={w_positional:.2f}\n")
        f.write(f"w_entropy={w_entropy:.2f}\n")
    print(f"Optimal weights saved to {weights_path}")

def optimize_weights(WORD_LIST, WORD_FREQUENCY, entropy_scores):
    """Optimize the weighting of base score, positional score, and entropy using Grid Search."""
    best_w_base, best_w_positional, best_w_entropy = 0, 0, 0
    best_avg_guesses = float('inf')
    weight_range = np.linspace(0, 1, 11)
    
    for w_base in weight_range:
        for w_positional in weight_range:
            w_entropy = 1 - (w_base + w_positional)
            if w_entropy < 0:
                continue
            avg_guesses = evaluate_weights_parallel(WORD_LIST, WORD_FREQUENCY, entropy_scores, w_base, w_positional, w_entropy, num_simulations=50)
            print(f"Testing w_base={w_base:.2f}, w_positional={w_positional:.2f}, w_entropy={w_entropy:.2f} -> Avg Guesses: {avg_guesses:.2f}")
            if avg_guesses < best_avg_guesses:
                best_avg_guesses = avg_guesses
                best_w_base, best_w_positional, best_w_entropy = w_base, w_positional, w_entropy
    
    print(f"Optimal Weights: w_base={best_w_base:.2f}, w_positional={best_w_positional:.2f}, w_entropy={best_w_entropy:.2f} with {best_avg_guesses:.2f} guesses on average")
    store_optimal_weights(best_w_base, best_w_positional, best_w_entropy)
    return best_w_base, best_w_positional, best_w_entropy

if __name__ == "__main__":
    WORD_LIST, WORD_FREQUENCY, entropy_scores = load_data()
    compute_entropy_instance = ComputeEntropy()  # ✅ Initialize globally
    best_w_base, best_w_positional, best_w_entropy = optimize_weights(WORD_LIST, WORD_FREQUENCY, entropy_scores)
    print(f"Optimized weights: w_base={best_w_base}, w_positional={best_w_positional}, w_entropy={best_w_entropy}")
