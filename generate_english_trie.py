from urllib import request
from marisa_trie import Trie
import ftfy


def process_word(word):
    return ftfy.fix_encoding(word.lower().strip())


def clean_words(words):
    return [process_word(word) for word in words]


def main():
    urls = [
        "https://raw.githubusercontent.com/dwyl/english-words/refs/heads/master/words.txt",
        "https://raw.githubusercontent.com/jeremy-rifkin/Wordlist/refs/heads/master/master.txt",
        "https://raw.githubusercontent.com/david47k/top-english-wordlists/refs/heads/master/top_english_words_mixed_1000000.txt",
    ]
    words = set()
    for url in urls:
        with request.urlopen(url) as response:
            lines = response.read().decode("utf-8").splitlines()
        words.update({word for word in lines if word})
    trie = Trie(clean_words(words))
    trie.save("./src/parseidon/data/trie/english.marisa")


if __name__ == "__main__":
    main()
