from typing import Sequence, Tuple

import pymupdf

from parseidon.handlers.handler import Handler
from parseidon.handlers.match import Match

ImagePainterHandlerInput = Sequence[Tuple[pymupdf.Document, Sequence[Match]]]
ImagePainterHandlerOutput = Sequence[pymupdf.Document]


class ImagePainterHandler(Handler[ImagePainterHandlerInput, ImagePainterHandlerOutput]):
    """
    Class for drawing rectangles around matched words in a pdf

    Attributes:
        color (Tuple): RGB-values, default=red
    """

    def __init__(self, color=(255, 0, 0)) -> None:
        """
        Initializes ContentHandler object

        Parameters:
            color (Tuple): RGB-values, default=red
        """
        super().__init__()
        self.color = color

    def handle_input(
        self, input: ImagePainterHandlerInput
    ) -> ImagePainterHandlerOutput:
        """
        For each document and list of matches, draw rectangles around
        the matched words in the document.

        Parameters:
            input (ImagePainterHandlerInput): List of tuples containing
                                    a pdf-document and a list of matches

        Returns:
            ImagePainterHandlerOutput: List of pdf-documents
        """
        for doc, matches in input:
            for match in matches:
                if not isinstance(match.position, tuple):
                    raise RuntimeError("Wrong type was sent to handler!")
                page: pymupdf.Page = doc[match.position[0]]
                rects = match.position[1]
                if any(
                    annot.rect.intersects(rects[0])
                    and annot.info["title"] != match.object_type
                    for annot in page.annots()
                ):
                    continue
                for r in rects:
                    annot: pymupdf.Annot = page.add_polygon_annot(
                        [r.bl, r.tl, r.tr, r.br]
                    )
                    annot.set_border(width=1)
                    annot.set_colors(stroke=[x / 255 for x in self.color])
                    annot.set_info(content=match.found_object, title=match.object_type)
                    annot.update()  # type: ignore
        return [document for document, _ in input]
