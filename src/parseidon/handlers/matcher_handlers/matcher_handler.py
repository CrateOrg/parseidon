from collections import Counter
from typing import Callable, Sequence, Tuple

import pymupdf
from parseidon.files.file import File
from parseidon.handlers.content import Content, PagePositionContext
from parseidon.handlers.content_handler import ContentHandlerOutput
from parseidon.handlers.handler import Handler
from parseidon.handlers.match import Match


MatcherHandlerInput = ContentHandlerOutput
MatcherHandlerOutput = Sequence[Tuple[File | pymupdf.Document, Sequence[Match]]]


# TODO: Fix. Same as in content handler..
def _is_new_row(last_position: pymupdf.Rect, current_position: pymupdf.Rect) -> bool:
    """
    Checks if we are on a new row

    Parameters:
       last_position (Rect): Previous known position
       current_position (Rect): Current position

    Returns:
        bool: Wheter we are on a new row or not
    """
    y_diff = abs(last_position.bl.y - current_position.bl.y)
    half_height = abs(min(last_position.height, current_position.height))
    if y_diff > (half_height / 2):
        return True
    return False


def _get_image_position(
    start: int, end: int, text: str, context_info: PagePositionContext
) -> Sequence[pymupdf.Rect]:
    """
    Gets image bounding box position from start and end string position

    Parameters:
        start (int): Starting position in string
        end (int): End position in string
        text (str): Current textblock
        context_info (PagePositionContext): Context for position on the page

    Returns:
        Sequence: Rectangles representing the bounding boxes of images
    """
    spaces = text[:start].count(" ")
    new_lines = text[:start].count("\n")
    start_index = spaces + new_lines
    end_index = start_index + text[start:end].count(" ") + text[start:end].count("\n")
    positions = []
    current_row = []
    for i in range(start_index, end_index + 1):
        for position in context_info.words[i][1]:
            if not current_row:
                current_row.append(position)
            else:
                last_pos = current_row[-1]
                if _is_new_row(last_pos, position):
                    positions += current_row
                    current_row = [position]
                else:
                    current_row[-1] = last_pos.include_rect(position)  # Expand rect
    positions += current_row

    return positions


class MatcherHandler(Handler[MatcherHandlerInput, MatcherHandlerOutput]):
    """
    Class for finding and handling matches

    Attributes:
        match_alg (Callable): matching algorithm, defined by
                                subclasses
    """

    def __init__(self, match_alg: Callable[[Content], Sequence[Match]]) -> None:
        """
        Initializes MatcherHandler object

        Parameters:
            match_alg (Callable): matching algorithm, defined by
                                    subclasses
        """
        super().__init__()
        self.match_alg = match_alg

    def handle_input(
        self, input: Sequence[Tuple[File | pymupdf.Document, Sequence[Content]]]
    ) -> Sequence[Tuple[File | pymupdf.Document, Sequence[Match]]]:
        """
        Loops through the input to find matches with the match_alg

        Parameters:
            input (Sequence): Content, sorted per document

        Returns:
            Sequence: Matches, sorted per document
        """
        output: MatcherHandlerOutput = []
        for context, contents in input:
            matches_in_context = []
            for content in contents:
                matches_in_context += self.match_alg(content)
            output.append((context, matches_in_context))

        objects = [match.found_object for _, matches in output for match in matches]
        match_counts = Counter(objects)
        for context_idx, (context, matches) in enumerate(output):
            for match_idx, match in enumerate(matches):
                matches = output[context_idx][1]
                matches[match_idx].count = match_counts[match.found_object]

        return output
