import os
import csv
import re

def extract_five_letter_words(directory):
    """Extracts five-letter words from text files in the given directory and saves them to a CSV."""
    
    five_letter_words = set()  # Use a set to avoid duplicates
    word_pattern = re.compile(r"^[a-zA-Z]{5}$")  # Regex for exactly 5 letters (a-z)

    def read_file_with_fallback(path):
        """Try reading as utf-8; if that fails, fallback to latin-1."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except UnicodeDecodeError:
            with open(path, "r", encoding="latin-1") as f:
                return f.read()

    # Loop through all files in the directory
    for filename in os.listdir(directory):
        if "english-words" in filename:  # or any condition you want
            file_path = os.path.join(directory, filename)
            try:
                file_contents = read_file_with_fallback(file_path)
                for line in file_contents.split("\n"):
                    words = line.strip().split()
                    for word in words:
                        word = word.lower()  # Convert to lowercase
                        if word_pattern.match(word):  # Check if it's a 5-letter word
                            five_letter_words.add(word)
            except Exception as e:
                print(f"Error reading {file_path}: {e}")

    # Save to CSV in the same directory
    output_path = os.path.join(directory, "wordlist_5.csv")
    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["word"])  # Header
        for word in sorted(five_letter_words):  # Sort words alphabetically
            writer.writerow([word])

    print(f"Five-letter words saved to {output_path}")

if __name__ == "__main__":
    directory_path = input("Enter the directory path: ").strip()
    extract_five_letter_words(directory_path)
