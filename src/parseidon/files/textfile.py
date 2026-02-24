import os

import ftfy
from typing import Any, Sequence
from parseidon.files.file import File
from parseidon.handlers.content import Content


class TextFile(File):
    """
    Subclass for representing plaintext files

    Attributes:
        name (str): Filename
        filetype (str): File-extension/type
        path (str): Path to file
    """

    def __init__(self, name: str, filetype: str, path: str) -> None:
        """
        Initializes an textfile object

        Parameters:
            name (str): Filename
            filetype (str): File-extension/type
            path (str): Path to file
        """
        super().__init__(name, filetype, path, False)
        self._content = self._get_content()

    def _get_content(self) -> str:
        """
        Reads file content into string

        Parameters: -

        Returns:
            str: Contents of current plaintext file
        """
        curr_path = os.path.join(self.path, self.name)
        with open(curr_path, mode="r") as file:
            return ftfy.fix_text(
                file.read()
            )  # this fixes the issue of reading text that is not unicode (and hence takes two bytes for e.g. 'ä')

    def content_with_context(self) -> Sequence[Content]:
        """
        Gets context which is the content for plaintext files

        Parameters: -

        Returns:
            Sequence[Content]: A list with the document
                                content as element
        """
        return [Content(None, self._content, self)]

    def get_position_for_context(self, context: Any, start_pos: int) -> str:
        """
        Get line number of current context

        Parameters:
            context (Any): Not used in plaintext files
            start_pos (int): Starting position of current word

        Returns:
            str: Line number of current context
        """
        line_num = self._content[0:start_pos].count("\n") + 1
        return f"Line: {line_num}"

    def get_neighbor_context_for(
        self, context: Any, start_pos: int, end_pos: int
    ) -> str:
        """
        Get neighbor context for current context

        Parameters:
            context (Any): Not used in plaintext files
            start_pos (int): Starting position of current word
            end_pos (int): End position of current word

        Returns:
            str: neighboring context of current word

        """
        return self.get_context(self._content, start_pos, end_pos)
