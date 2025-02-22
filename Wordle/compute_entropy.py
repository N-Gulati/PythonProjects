import collections
import itertools
import numpy as np
from math import log2
from multiprocessing import Pool, cpu_count

class ComputeEntropy:
    def __init__(self):
        """Initialize with a word list."""
        self.ALL_POSSIBLE_PATTERNS = self.generate_all_patterns()  # Precompute once

    @staticmethod
    def generate_all_patterns():
        """Generate all possible 3^5 Wordle feedback patterns."""
        return ["".join(p) for p in itertools.product("GYB", repeat=5)]

    @staticmethod
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
        probabilities = [
            (feedback_patterns[pattern] / total_patterns) if pattern in feedback_patterns else 0 
            for pattern in all_possible_patterns
        ]
        
        entropy = -sum(p * log2(p) for p in probabilities if p > 0)
        return word, entropy

    def compute_entropy_scores(self, words, multi=1):
        """Precompute entropy scores for all words in the dictionary, with optional multiprocessing."""
        if multi == 1:
            with Pool(cpu_count()) as pool:
                results = pool.starmap(self.compute_entropy, 
                                       [(word, words, self.ALL_POSSIBLE_PATTERNS) for word in words])
        else:
            results = [self.compute_entropy(word, words, self.ALL_POSSIBLE_PATTERNS) for word in words]
        
        return {word: entropy for word, entropy in results}
