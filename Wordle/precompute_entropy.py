import collections
import itertools
import csv
import os
import numpy as np
from math import log2
from multiprocessing import Pool, cpu_count

# Get the directory of the current script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Load a word list from a file containing five-letter words.
word_list_path = os.path.join(SCRIPT_DIR, "wordlist_5.csv")
with open(word_list_path) as f:
    WORD_LIST = [word.strip() for word in f if len(word.strip()) == 5]

def generate_all_patterns():
    """Generate all possible 3^5 Wordle feedback patterns."""
    return ["".join(p) for p in itertools.product("GYB", repeat=5)]

def compute_entropy(word, words, all_possible_patterns):
    """Compute entropy for a word considering all 3^5 possible feedback patterns."""
    feedback_patterns = collections.defaultdict(int)
    
    for possible_word in words:
        pattern = "".join(
            "G" if word[i] == possible_word[i] else
            "Y" if word[i] in possible_word else "B"
            for i in range(5)
        )
        feedback_patterns[pattern] += 1
    
    total_patterns = sum(feedback_patterns.values())
    probabilities = [(feedback_patterns[pattern] / total_patterns) if pattern in feedback_patterns else 0 for pattern in all_possible_patterns]
    
    entropy = -sum(p * log2(p) for p in probabilities if p > 0)
    return word, entropy

def precompute_entropy_scores(output_file="entropy_scores.csv"):
    """Precompute entropy scores for all words in the dictionary using multiprocessing and save to CSV."""
    all_possible_patterns = generate_all_patterns()  # Generate once and pass to function
    
    with Pool(cpu_count()) as pool:
        results = pool.starmap(compute_entropy, [(word, WORD_LIST, all_possible_patterns) for word in WORD_LIST])
    
    output_path = os.path.join(SCRIPT_DIR, output_file)
    with open(output_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["word", "entropy"])
        for word, entropy in results:
            writer.writerow([word, entropy])
    
    print(f"Entropy scores saved to {output_path}")

if __name__ == "__main__":
    precompute_entropy_scores()
