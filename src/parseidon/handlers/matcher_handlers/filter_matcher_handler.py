import re
from string import punctuation
from typing import Any
from parseidon.handlers.content import Content, PagePositionContext
from parseidon.handlers.match import Match
from parseidon.handlers.matcher_handlers.matcher_handler import MatcherHandler
from marisa_trie import Trie
from parseidon.helpers.resource_loader import open_file


class FilterMatcherHandler(MatcherHandler):
    """
    Class for finding and handling matches in filtermode

    Attributes:
        trie (Trie): Trie datastructure used for looking up valid words
        ignore_punctuation (bool): Wheter punctuation
                                    should be considered or not
    """

    def __init__(
        self, trie_file: str, ignore_punctuation: bool, skip_list: list
    ) -> None:
        """
        Initializes FilterMatcherHandler object

        Parameters:
            trie (Trie): Trie datastructure used for looking up valid words
            ignore_punctuation (bool): Wheter punctuation
                                        should be considered or not
        """
        super().__init__(lambda content: self.__get_filtered_content(content))
        self.trie = Trie()
        with open_file(trie_file, "rb") as file:
            self.trie.frombytes(file.read())
        self.ignore_punctuation = ignore_punctuation
        self.punctuation_trie = Trie()
        self.skip_list = skip_list
        with open_file("trie/punctuation.marisa", "rb") as file:
            self.punctuation_trie.frombytes(file.read())

    def __get_filtered_content(self, curr_content: Content) -> Any:
        """
        Finds filtermode match-objects from current document content

        Parameters:
            curr_content (Content): The current page/document content

        Returns:
            Any: List of matches (if there are any)
        """
        output_list = []
        context_info = curr_content.context
        if isinstance(context_info, PagePositionContext):
            for word, pos in context_info.words:
                clean_word = self.__clean_word(word)
                if self.__find_word(word, clean_word):
                    if self.__skip_specials(clean_word):
                        continue
                    m = Match(
                        "Non-word",
                        word.strip(),
                        curr_content.owner_file.file_path(),
                        (context_info.page, pos),
                        "",
                    )
                    output_list.append(m)
        else:
            text = curr_content.content
            word_matches = re.finditer(r"\S+", text)
            for word_match in word_matches:
                word = word_match.group(0)
                clean_word = self.__clean_word(word)
                if self.__find_word(word, clean_word):
                    if self.__skip_specials(clean_word):
                        continue
                    start = word_match.start()
                    end = word_match.end()
                    m = Match(
                        "Non-word",
                        word.strip(),
                        curr_content.owner_file.file_path(),
                        curr_content.owner_file.get_position_for_context(
                            context_info, start
                        ),
                        curr_content.owner_file.get_neighbor_context_for(
                            context_info, start, end
                        ),
                    )
                    output_list.append(m)
        return output_list

    def __find_word(self, word: str, clean_word: str) -> bool:
        """
        Attempts to determine if a word is in the trie (False) or if
        it should be matched as a non-word (True)

        Parameters:
            word (str): The current word to be matched
            clean_word (str): A cleaned up version of word

        Returns:
            bool: Returns True if the word is a word but is not
                    in the trie
        """
        in_skiplist = any(w in self.skip_list for w in [word, clean_word])
        has_len = len(clean_word) > 0
        all_parts_valid = all(w in self.trie for w in clean_word.split("/"))
        word_valid = word in self.trie
        return not in_skiplist and has_len and not all_parts_valid and not word_valid

    def __skip_specials(self, clean_word: str) -> bool:
        """
        Skips "words" consisting of only a special chars if
        ignore_punctuation is True

        Parameters:
            clean_word (str): Cleaned version of word to be checked

        Returns:
            bool: If the word should be skipped or not
        """
        return self.ignore_punctuation and clean_word in self.punctuation_trie

    def __clean_word(self, word: str) -> str:
        """
        Finds filtermode match-objects from current document content

        Parameters:
            word (str): Current word

        Returns:
            str: Clean version of the word
        """

        def _clean(word):
            return word.strip().strip(punctuation).strip('’"“”„»-—§…?·*').lower()

        def _is_number(word):
            if not word or len(re.findall(r"\.", word)) > 1:
                return False
            no_dots = word.replace(".", ",")
            if no_dots[0] == "-":
                return all(c.isdigit() for c in no_dots[1:].split(","))
            return all(c.isdigit() for c in no_dots.split(","))

        def _try_clean_parts(word):
            if word and not word.isalnum():
                res = re.search(r"[^a-zA-Z0-9üåäöÅÄÖ.,#&/!\"“”„»§…?·*]", word)
                if res and all(
                    self.__clean_word(w) in self.trie for w in word.split(res.group())
                ):
                    word = word[: res.start()]
            return word

        stripped_word = _clean(word)
        while True:
            stripped = _clean(stripped_word)
            if stripped == stripped_word:
                break
            stripped_word = stripped
        if _is_number(stripped_word):
            stripped_word = ""

        return _try_clean_parts(stripped_word)
