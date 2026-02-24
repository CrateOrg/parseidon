import pymupdf

from parseidon.handlers.image_painter_handler import ImagePainterHandler
from parseidon.handlers.match import Match


def test_draw_annotations():
    handler = ImagePainterHandler()

    doc = pymupdf.Document()
    doc.new_page(0)  # type: ignore

    rect = pymupdf.Rect(10, 10, 15, 15)
    matches = [Match("TEST", "IDK", "some path", (0, [rect]), "context", 0)]
    painted = handler.handle_input([(doc, matches)])
    assert len(painted) == 1
    document = painted[0]
    page = document[0]
    annotations = page.annots()
    for annot in annotations:
        assert annot.rect.contains(rect)

