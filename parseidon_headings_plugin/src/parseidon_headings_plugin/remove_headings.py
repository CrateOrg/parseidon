import re

import pluggy
from parseidon.handlers.content import PagePositionContext

hookimpl = pluggy.HookimplMarker(project_name="parseidon")


class RemoveHeadingPlugin:
    @hookimpl
    def post_process_content(self, output):
        """
        Hook for post processing the output from content_handler

        Parameters:
            output: list of tuples containing documents and their contents

        Returns:
            The post processed content_handler output, without
            IPv4-like headings
        """
        for _, list_of_contents in output:
            potential_headings = set()
            for content in list_of_contents:
                if isinstance(content.context, PagePositionContext):
                    content, potential_headings = self.process_wordlist(
                        content, potential_headings
                    )

                content, potential_headings = self.process_content_string(
                    content, potential_headings
                )

        return output

    def process_wordlist(self, content, potential_headings):
        """
        Helper for processing words in text-output mode

        Parameters:
            content: Content

        Returns: Content without IPv4-like headings
        """
        words = content.context.words
        heading_re = re.compile(r"(\d{1,2}\.)*\d{1,2}\.?")
        prev = "\n"
        for ix, word in enumerate(words):
            word_text = word[0].strip().strip(".")
            if heading_re.match(word_text) and prev.endswith("\n"):
                parent = word_text.rsplit(".", 1)[0]
                if parent == word_text:
                    potential_headings.add(word_text)
                    continue
                if parent in potential_headings:
                    potential_headings.add(word_text)
                    words[ix] = ("", [])
            prev = word[0]
        return content, potential_headings

    def process_content_string(self, content, potential_headings):
        """
        Helper for processing words in text-output mode

        Parameters:
            content: Content

        Returns: Content without IPv4-like headings
        """
        text = content.content
        heading_re = re.compile(r"(?:(?<=\n)|^)(\d{1,2}\.)*\d{1,2}(?=(\.?(\s+|$)))")
        for match in heading_re.finditer(text):
            word = match.group()
            word_text = word.strip().strip(".")
            parent = word_text.rsplit(".", 1)[0]
            if word_text == parent:
                potential_headings.add(word_text)
                continue
            if parent in potential_headings:
                potential_headings.add(word_text)
                text = re.sub(word, "\u200b" * len(word), text, 1)
        content.content = text
        return content, potential_headings
