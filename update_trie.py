import argparse
import ftfy
import marisa_trie as MT


def process_word(word):
    return ftfy.fix_encoding(word.lower().strip())  # Could add ftfy fix encoding


def clean_words(words):
    return [process_word(word) for word in words]


def load_wordlist(filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        return {word for word in clean_words(file.readlines()) if word}


def create_trie(filepath, words):
    print(f"Total number of words: {len(words)}")
    mt = MT.Trie(words)
    mt.save(filepath)


def load_trie(filepath):
    trie = MT.Trie()
    with open(filepath, "rb") as file:
        trie.frombytes(file.read())
    return set(trie.keys())


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("trie_path", help="Path to existing Trie file")
    parser.add_argument("input_paths", help="Path to input text files", nargs="+")
    args = parser.parse_args()
    return args.trie_path, args.input_paths


def main():
    trie_path, in_paths = get_args()
    words = load_trie(trie_path)
    for ip in in_paths:
        words.update(load_wordlist(ip))
    create_trie(trie_path, words)


if __name__ == "__main__":
    main()
