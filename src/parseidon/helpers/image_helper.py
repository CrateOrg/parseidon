import pymupdf
from pytesseract import pytesseract
from typing import Any


def data_from_image_bytes(bytes):
    return pytesseract.image_to_data(bytes, output_type="dict", lang="swe+eng")


def word_count(data):
    return len(data["level"])


def word_from_data(data, index):
    return data["text"][index].strip()


def word_positions(data, index):
    return (
        data["left"][index],
        data["top"][index],
        data["width"][index],
        data["height"][index],
    )


def rect_is_at_new_line(last_rect: pymupdf.Rect, curr_rect: pymupdf.Rect) -> bool:
    """
    Check if image rectangle is on another line than previous rectangle

    Parameters:
        last_rect (Rect): Previous pymupdf rectangle
        curr_rect (Rect): Current pymupdf rectangle

    Returns:
        bool: If rectangles are on different lines
    """
    y_diff = abs(last_rect.bl.y - curr_rect.bl.y)
    half_height = abs(min(last_rect.height, curr_rect.height))
    if y_diff > (half_height / 2):
        return True
    else:
        return False


def get_text_from_image_bytes(bytes: Any) -> str:
    """
    Get image text, from bytes

    Parameters:
        bytes (bytes): Images bytes

    Returns:
        str: Text in image
    """
    data = data_from_image_bytes(bytes)
    last_rect = None
    text = ""
    for i in range(word_count(data)):
        word = word_from_data(data, i)
        if not word:
            continue
        x, y, w, h = word_positions(data, i)
        rect = pymupdf.Rect(x, y, x + w, y + h)
        if last_rect is not None and rect_is_at_new_line(last_rect, rect):
            text += "\n" + word
        elif last_rect is None:
            text += word
        else:
            text += " " + word
        last_rect = rect
    return text
