from typing import Sequence

import pymupdf


class Match(object):
    """
    Match-class, containing information about each match

    Attributes:
        object_type (str): Pattern/rule triggering the match
        found_object (str): The actual matched string/word
        file_path (str): Path to file
        position (str or tuple[int, Sequence[pymupdf.Rect]]):
                        The position of the matched word in the file
        context (str): Words surrounding the match, to give context
        count (int or None = None): Number of instances
                                    of match in input
    """

    def __init__(
        self,
        object_type: str,
        found_object: str,
        file_path: str,
        position: str | tuple[int, Sequence[pymupdf.Rect]],
        context: str,
        count: int | None = None,
    ) -> None:
        """
        Initializes Match object

        Parameters:
            object_type (str): Pattern/rule triggering the match
            found_object (str): The actual matched string/word
            file_path (str): Path to file
            position (str or tuple[int, Sequence[pymupdf.Rect]]):
                            The position of the matched word in the file
            context (str): Words surrounding the match, to give context
            count (int or None = None): Number of instances
                                        of match in input
        """
        self.object_type = object_type
        self.found_object = found_object
        self.file_path = file_path
        self.position = position
        self.context = context
        self.count = count

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return f"Found: {self.found_object}"
