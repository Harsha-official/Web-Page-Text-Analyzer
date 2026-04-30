import re
import os
import sys
import requests
from collections import Counter
from bs4 import BeautifulSoup


def scrape_text(url):
    # reject anything that doesn't look like a real url
    if not url.startswith("http://") and not url.startswith("https://"):
        raise ValueError(f"'{url}' doesn't look like a valid URL. Make sure it starts with http:// or https://")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
    except requests.exceptions.ConnectionError:
        raise ValueError(f"Couldn't connect to {url}. Check your internet or the URL.")
    except requests.exceptions.Timeout:
        raise ValueError(f"Request to {url} timed out after 10s.")
    except requests.exceptions.HTTPError as e:
        raise ValueError(f"Got HTTP {e.response.status_code} from {url}")

    soup = BeautifulSoup(resp.text, "html.parser")

    # nuke all the junk tags we don't care about
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()

    raw = soup.get_text(separator=" ")
    cleaned = re.sub(r"\s+", " ", raw).strip()
    return cleaned


def get_word_frequency(text, top_n=10):
    if not text or not text.strip():
        return []

    # words to ignore - mostly just noise in frequency counts
    stop_words = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to",
        "for", "of", "with", "by", "from", "is", "are", "was", "were",
        "be", "been", "being", "have", "has", "had", "do", "does", "did",
        "will", "would", "shall", "should", "may", "might", "can", "could",
        "not", "no", "nor", "so", "yet", "both", "either", "neither",
        "it", "its", "this", "that", "these", "those", "i", "you", "he",
        "she", "we", "they", "me", "him", "her", "us", "them", "my",
        "your", "his", "our", "their", "what", "which", "who", "as",
        "if", "then", "than", "also", "into", "about", "up", "out", "s",
        "more", "all", "just", "over", "after", "before", "between",
    }

    # only grab words 3+ chars so we skip stuff like "ok", "mr", etc.
    words = re.findall(r"[a-zA-Z]{3,}", text.lower())
    filtered = [w for w in words if w not in stop_words]

    counts = Counter(filtered)
    return counts.most_common(top_n)


def compute_text_stats(text):
    if not text or not text.strip():
        return {
            "char_count": 0,
            "word_count": 0,
            "sentence_count": 0,
            "avg_word_length": 0.0,
            "avg_sentence_length": 0.0,
            "readability_level": "N/A",
        }

    words = re.findall(r"[a-zA-Z0-9]+", text)
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]

    word_count = len(words)
    sentence_count = len(sentences) if sentences else 1
    char_count = sum(len(w) for w in words)

    avg_word_len = round(char_count / word_count, 2) if word_count else 0.0
    avg_sent_len = round(word_count / sentence_count, 2)

    # rough readability bucket - not perfect but good enough
    if avg_sent_len < 10:
        level = "Easy"
    elif avg_sent_len < 18:
        level = "Moderate"
    elif avg_sent_len < 25:
        level = "Advanced"
    else:
        level = "Complex"

    return {
        "char_count": char_count,
        "word_count": word_count,
        "sentence_count": sentence_count,
        "avg_word_length": avg_word_len,
        "avg_sentence_length": avg_sent_len,
        "readability_level": level,
    }


def save_report(text, stats, freq, output_path):
    lines = []
    lines.append("=" * 55)
    lines.append("  Page Analysis Report")
    lines.append("=" * 55)
    lines.append("")
    lines.append("Stats:")
    lines.append(f"  words:           {stats.get('word_count', 0)}")
    lines.append(f"  sentences:       {stats.get('sentence_count', 0)}")
    lines.append(f"  characters:      {stats.get('char_count', 0)}")
    lines.append(f"  avg word length: {stats.get('avg_word_length', 0)}")
    lines.append(f"  avg sent length: {stats.get('avg_sentence_length', 0)}")
    lines.append(f"  readability:     {stats.get('readability_level', 'N/A')}")
    lines.append("")
    lines.append("Top words:")

    for i, (word, count) in enumerate(freq, start=1):
        lines.append(f"  {i}. {word} ({count})")

    lines.append("")
    lines.append("Preview (first 500 chars):")
    lines.append(text[:500])
    lines.append("")
    lines.append("=" * 55)

    out = os.path.abspath(output_path)
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return out


def main():
    print("\nWeb Page Text Analyzer")
    print("-" * 25)

    url = input("URL to scrape: ").strip()
    if not url:
        print("No URL given, exiting.")
        sys.exit(1)

    print("Fetching page...")
    try:
        text = scrape_text(url)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    print(f"Got {len(text)} characters of text.\n")

    stats = compute_text_stats(text)
    freq = get_word_frequency(text, top_n=10)

    print("-- Stats --")
    for key, val in stats.items():
        print(f"  {key}: {val}")

    print("\n-- Top 10 words --")
    for i, (word, count) in enumerate(freq, start=1):
        print(f"  {i}. {word} — {count}")

    ans = input("\nSave report? (y/n): ").strip().lower()
    if ans == "y":
        filename = input("Filename [report.txt]: ").strip() or "report.txt"
        saved_to = save_report(text, stats, freq, filename)
        print(f"Saved to {saved_to}")


if __name__ == "__main__":
    main()