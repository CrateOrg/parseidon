from dataclasses import dataclass
from typing import Any, Sequence, Tuple

import pymupdf


@dataclass
class ExcelContext:
    row: int
    col: int
    sheetnum: str | int


@dataclass
class PagePositionContext:
    page: int
    words: Sequence[Tuple[str, Sequence[pymupdf.Rect]]]
    rotation: int


ContentContext = str | ExcelContext | PagePositionContext | None


@dataclass
class Content:
    context: ContentContext
    content: str
    owner_file: Any
