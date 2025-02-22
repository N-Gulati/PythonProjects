#try to figure out a way to implement "strategic disambiguation" where when you have a circumstance like BGGGG and more possible words than remaining guesses you must guess words that don't necessarily have all of the Gs but rather use as many of the possible options for the B
#this reduces the guess ambiguity by sarcrificing a guess or two (need to assess for situation and need to track remaining guesses relative to count of ambiguous options)

# possible prompt
#"given that you are allow 6 guesses, update Wordle Solver, when receiving a response from the user where there are 4 Gs and 1 B, and there are 
# more than the remaining number of guesses as options from the dictionary of words, to guess words that reduce those options by using as many of the unique remaining possible 
# letters as possible for no more than half of the remaining guesses, rounded down."

#possible bug if letter in word and guess is double letter might get letter as B and (G or Y) and then its removing all words with that letter
#such as books returned as GBGBB - FIXED

import collections
import itertools

# Load a word list (for real use, replace this with a complete list of 5-letter words)
with open(r"C://Users//nrg63_000//Documents//GitHub//PythonProjects//DataFiles//scowl-2020.12.07//final//english_dicts_txt//wordlist_5.csv") as f:
    WORD_LIST = [word.strip() for word in f if len(word.strip()) == 5]

# Load word frequency data (assumed to be in a file "word_frequencies.txt" with format: word frequency)
WORD_FREQUENCY = {}
try:
    with open(r"C://Users//nrg63_000//Documents//GitHub//PythonProjects//DataFiles//scowl-2020.12.07//final//english_dicts_txt//word_frequencies.txt") as f:
        for line in f:
            word, freq = line.strip().split()
            WORD_FREQUENCY[word] = int(freq)
except FileNotFoundError:
    print("Warning: word_frequencies.txt not found. Frequency weighting will be ignored.")

def get_letter_frequencies(words):
    """Compute letter frequency across all remaining words."""
    freq = collections.Counter(itertools.chain.from_iterable(words))
    return freq

def score_word(word, letter_frequencies):
    """Score a word based on letter frequency analysis and common usage, with normalization."""
    base_score = sum(letter_frequencies[c] for c in set(word))
    max_base_score = max(letter_frequencies.values(), default=1)
    normalized_base_score = base_score / max_base_score  # Normalize to a range of 0 to 1
    print(normalized_base_score)
    frequency_weight = WORD_FREQUENCY.get(word, 1)
    max_frequency_weight = max(WORD_FREQUENCY.values(), default=1)
    normalized_frequency_weight = frequency_weight / max_frequency_weight  # Normalize to a range of 0 to 1
    print(normalized_frequency_weight)

    return normalized_base_score + normalized_frequency_weight  # Sum ensures balanced scoring

def best_guess(words, remaining_guesses, last_feedback=None):
    """Return the best word to guess, prioritizing strategic disambiguation when needed."""
    
    letter_frequencies = get_letter_frequencies(words)

    # If there's no ambiguity, use the original scoring method
    if not last_feedback or remaining_guesses <= 2:
        return max(words, key=lambda word: score_word(word, letter_frequencies))

    # Identify a strategic disambiguation scenario (4 Greens, 1 Black, too many remaining words)
    green_count = last_feedback.count("G")
    black_count = last_feedback.count("B")

    if green_count == 4 and black_count == 1 and len(words) > remaining_guesses:
        # Find which letter is the ambiguous one
        black_letter_index = last_feedback.index("B")
        
        # Find all possible replacements for the black letter across remaining words
        possible_replacements = {word[black_letter_index] for word in words}

        # Find a word that maximizes coverage of these letters
        best_disambiguation_word = None
        best_coverage = 0

        # Check all words in the full dictionary (not just remaining words)
        for candidate in WORD_LIST:
            unique_letters = set(candidate) & possible_replacements
            coverage = len(unique_letters)  # Count how many black-letter candidates it includes

            if coverage > best_coverage:
                best_coverage = coverage
                best_disambiguation_word = candidate

        if best_disambiguation_word:
            return best_disambiguation_word  # Use the most efficient eliminator word

    # Default to normal best guess selection if no disambiguation is needed
    return max(words, key=lambda word: score_word(word, letter_frequencies))

def filter_words(words, guess, result):
    """Filter words based on feedback from Wordle.
    result: 'G' (green), 'Y' (yellow), 'B' (black/gray) for each letter in the guess.
    """
    new_words = []
    for word in words:
        match = True
        for i, (g_letter, r) in enumerate(zip(guess, result)):
            if (r == 'G' and word[i] != g_letter) or \
               (r == 'Y' and (g_letter not in word or word[i] == g_letter)) or \
               (r == 'B' and g_letter in word and guess.count(g_letter) == 1):
                match = False
                break
        if match:
            new_words.append(word)
    return new_words

def wordle_solver():
    """Main Wordle-solving function."""
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
                break  # Proceed to the next round

if __name__ == "__main__":
    wordle_solver()


