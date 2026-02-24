import os
from abc import abstractmethod
from typing import Sequence

from parseidon.handlers.content import Content


class File:
    """
    Superclass for representing different filetypes

    Attributes:
        name (str): Filename
        filetype (str): File-extension/type
        path (str): Path to file
        image_extract (bool): Determines if OCR should be used
    """

    def __init__(
        self, name: str, filetype: str, path: str, image_extract: bool
    ) -> None:
        """
        Initializes a file object

        Parameters:
            name (str): Filename
            filetype (str): File-extension/type
            path (str): Path to file
            image_extract (bool): Determines if OCR should be used
        """
        self.name = name
        self.filetype = filetype
        self.path = path
        self.image_extract = image_extract

    def file_path(self) -> str:
        """
        Get path to file

        Parameters: -

        Returns:
            str: path to current file
        """
        return os.path.join(self.path, self.name)

    @abstractmethod
    def content_with_context(self) -> Sequence[Content]: ...

    @abstractmethod
    def get_position_for_context(self, context, start_pos) -> str: ...

    @abstractmethod
    def get_neighbor_context_for(self, context, start_pos, end_pos) -> str: ...

    def get_context(self, text: str, start: int, end: int) -> str:
        """
        Get context(previous and upcoming words) of given
        word.

        Parameters:
            text (str): Current content
            start (int): Start index of match/word in content
            end (int): End index of match/word in content

        Returns:
            str: The context of the word located from start to end
            in the text(content)
        """
        start_index = max(0, len(text[:start].split()) - 3)
        end_index = min(len(text.split()), len(text[:end].split()) + 3)
        return " ".join(text.split()[start_index:end_index])
