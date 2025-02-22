import praw
import re
import os
import time
from collections import Counter

def load_subreddits_from_file(filename="ListOfSubreddits_Alphabetical.txt"):
    """Load a list of subreddits from a file."""
    try:
        with open(filename, "r") as f:
            subreddits = [line.strip().replace("/r/", "") for line in f if line.strip()]
        return subreddits
    except FileNotFoundError:
        print(f"Error: {filename} not found.")
        return []

def scrape_reddit_subreddits(subreddits):
    """Scrape the top 10 posts and their comments from a list of subreddits for five-letter words using PRAW."""
    reddit = praw.Reddit(
        client_id="Gw8wjM_sawoofQ5L_PFmLA",
        client_secret="4uwVVm7vmzlTnP6e-cUzMYPYRHALxQ",
        user_agent="wordle_scraper/1.0 by RelaxYDF"
    )
    
    blocked_keywords = ["porn", "dick", "lesbian", "wife", "twink", "gay", "anal", "NSFW", "phile", "BDSM", "fetish", "boob", "gonewild", "hentai", "xxx"]
    
    word_counts = Counter()
    
    for subreddit_name in subreddits:
        if any(keyword.lower() in subreddit_name.lower() for keyword in blocked_keywords):
            print(f"Skipping subreddit: r/{subreddit_name} (contains blocked keyword)")
            continue
        print(f"Searching...{subreddit_name}")
        try:
            subreddit = reddit.subreddit(subreddit_name)
            for post in subreddit.top(limit=1):
                text = post.title + " " + (post.selftext or "")
                
                # Scrape up to 100 comments
                post.comments.replace_more(limit=0)
                comments = post.comments.list()[:1]
                
                for comment in comments:
                    text += " " + (comment.body or "")
                
                words = re.findall(r'\b[a-z]{5}\b', text.lower())
                word_counts.update(words)
            
            time.sleep(2)  # Prevents excessive requests to Reddit
        except Exception as e:
            print(f"Error fetching data from r/{subreddit_name}: {e}")
    
    output_dir = os.path.join("DataFiles", "scowl-2020.12.07", "final", "english_dicts_txt")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "word_frequencies.txt")
    
    with open(output_file, "w") as f:
        for word, count in word_counts.items():
            f.write(f"{word} {count}\n")
    
    print(f"Successfully stored {len(word_counts)} unique five-letter words in {output_file}.")

if __name__ == "__main__":
    subreddits = load_subreddits_from_file()
    if subreddits:
        scrape_reddit_subreddits(subreddits)
