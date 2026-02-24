import re

import pluggy
from marisa_trie import Trie
from string import punctuation
from parseidon.handlers.content import PagePositionContext
from parseidon.helpers.resource_loader import open_file

hookimpl = pluggy.HookimplMarker(project_name="parseidon")


class DehyphenatePlugin:
    def should_patch_words(self, word1, word2):
        """
        Determines if a hyphen should be removed
        and the words get patched together

        Parameters:
            word1: the substring to the left of the hyphen
            word2: the substring to the right of the hyphen

        Returns:
            If the hyphen should be removed(bool)
        """
        word2_stripped = word2.strip(punctuation)
        combined = word1 + word2_stripped
        if (word2_stripped.lower() in self.trie and word1.lower() in self.trie) and (
            combined.lower() not in self.trie
        ):  # only return with hyphen if w1 and w2 are words and w1+w2 is not
            return False
        else:
            return True

    @hookimpl(tryfirst=True)
    def post_process_content(self, output, trie_file):
        """
        Hook for post processing the output from content_handler

        Parameters:
            output: list of tuples containing documents and their contents
            trie_file: filepath to custom data trie
        Returns:
            The post processed content_handler output, with
            correctly dehyphenated words
        """
        if not trie_file:
            trie_file = "trie/swedish.marisa"
        self.trie = Trie()
        with open_file(trie_file, "rb") as file:
            self.trie.frombytes(file.read())
        for _, list_of_contents in output:
            for content in list_of_contents:
                if isinstance(content.context, PagePositionContext):
                    content = self.process_word_list(content)
                content = self.process_content_string(content)

        return output

    def process_content_string(self, content):
        """
        Helper for processing words in text-output mode

        Parameters:
            content: Content

        Returns: Content with correct hyphenation
        """
        text = content.content
        pattern = re.compile(r"(\S+)(-|\xad)\n(\S*)[ \n]?")
        for match in pattern.finditer(text):
            escaped_match = re.escape(match.group())
            left = match.group(1)
            right = match.group(3)
            if self.should_patch_words(left, right):
                text = re.sub(escaped_match, left + right + "\n", text, 1)
            else:
                text = re.sub(escaped_match, left + "-" + right + "\n", text, 1)
        content.content = text
        return content

    def process_word_list(self, content):
        """
        Helper for processing words in draw-on-pdf mode

        Parameters:
            content: Content

        Returns: Content with correct hyphenation
        """
        words = content.context.words
        i = 0
        while i < len(words):
            word = words[i][0]
            hyphen_nl = re.search("(-|\xad)\n", word)
            if hyphen_nl and word != hyphen_nl.group():
                word1, word2 = (
                    word[: hyphen_nl.start()],
                    words[i + 1][0].strip(),
                )
                words[i][1].append(words[i + 1][1][0])
                if self.should_patch_words(word1, word2):
                    words[i] = (word1 + word2 + "\n", words[i][1])
                else:
                    words[i] = (word1 + "-" + word2 + "\n", words[i][1])
                del words[i + 1]
            i += 1
        return content
