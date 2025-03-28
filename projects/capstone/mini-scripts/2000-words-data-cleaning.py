import re
import json


def parse_strict_korean_vocab(filepath):
    words = []
    sentences = []
    word_id = 1

    with open(filepath, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    i = 0
    while i < len(lines):
        # Skip junk lines
        if re.match(r"(?i)^page|\blingo mastery\b", lines[i]):
            i += 1
            continue

        # Vocabulary line
        line = lines[i]
        match = re.match(
            r"^(\d+)[–\-\.]?\s+([가-힣]+)\s*/\s*([\w\-]+)\s*\[([a-zA-Z\. ]+)\]\s+(.+)",
            line,
        )
        if not match:
            i += 1
            continue

        _, word, romanization, pos_raw, meaning_text = match.groups()
        pos = pos_raw.strip().lower().rstrip(".")
        meanings = [m.strip() for m in meaning_text.split(",")]

        # Example sentences
        example_kr = lines[i + 1] if i + 1 < len(lines) else ""
        example_en = lines[i + 2] if i + 2 < len(lines) else ""

        if pos == "n":
            pos == "noun"
        elif pos == "num":
            pos = "number"
        elif pos == "pron":
            pos = "pronoun"
        elif pos == "v":
            pos = "verb"
        elif pos == "a":
            pos = "adjective"
        elif pos == "adv":
            pos = "adverb"
        elif pos == "determiner":
            pos = "determiner"
        elif pos == "assistant v":
            pos = "assistant verb"
        elif pos == "adj":
            pos = "adjective"
        elif pos == "determine":
            pos = "determiner"
        elif pos == "p":
            pos = "pronoun"

        for meaning in meanings:
            words.append(
                {
                    "id": word_id,
                    "word": word,
                    "romanization": romanization,
                    "pos": pos,
                    "meaning": meaning,
                }
            )

            if example_kr and example_en:
                sentences.append(
                    {
                        "word_id": word_id,
                        "example_kr": example_kr,
                        "example_en": example_en,
                    }
                )

            word_id += 1

        i += 3  # move to next vocab block

    return words, sentences


words, sentences = parse_strict_korean_vocab(
    "txt_path=../../../assets/data/raw/words/2000 Most Common Korean Words i - Lingo Mastery.txt"
)

# Save words to a JSON file
with open(
    "../assets/data/processed/korean_words_2000.json", "w", encoding="utf-8"
) as words_file:
    json.dump(words, words_file, ensure_ascii=False, indent=4)

# Save sentences to a JSON file
with open(
    "../assets/data/processed/korean_sentences_2000.json",
    "w",
    encoding="utf-8",
) as sentences_file:
    json.dump(sentences, sentences_file, ensure_ascii=False, indent=4)
