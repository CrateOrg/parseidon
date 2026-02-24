import io
import logging
import os
from multiprocessing import Pool
from typing import Sequence

import pymupdf
from PIL import Image

from parseidon.files.file import File
from parseidon.handlers.content import Content, PagePositionContext
from parseidon.helpers.image_helper import (
    data_from_image_bytes,
    rect_is_at_new_line,
    word_count,
    word_from_data,
    word_positions,
)

logger = logging.getLogger(__name__)


class PdfFile(File):
    """
    Subclass for representing PDFs

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
        Initializes an PDF object

        Parameters:
            name (str): Filename
            filetype (str): File-extension/type
            path (str): Path to file
            image_extract (bool): Determines if OCR should be used
        """
        super().__init__(name, filetype, path, image_extract)

    def _get_content(self) -> Sequence[Content]:
        """
        Read content from PDF pages
        using helper function page_texts()

        Parameters: -

        Returns:
            Sequence[Content]: A list with the content
            of each page
        """
        pdf = self.pdf()
        page_content = []
        for ix in range(pdf.page_count):
            page_content += self.page_texts(ix, False)

        return page_content

    def pdf(self) -> pymupdf.Document:
        """
        Create a pymupdf instance from the
        filepath

        Parameters: -

        Returns:
            pymupdf document
        """
        return pymupdf.open(os.path.join(self.path, self.name))

    def document_content(self, num_threads: int) -> Sequence[tuple]:
        """
        Read content from PDF document with parallell threads.

        Parameters:
        num_threads (int): The number of threads to use

        Returns:
            Sequence[tuple]: (document, current text content)
        """
        output = []
        pdf = self.pdf()

        with Pool(processes=num_threads) as pool:
            args = [(ix, True) for ix in range(pdf.page_count)]
            text_contents = [
                res
                for contents in pool.starmap(self.page_texts, args, chunksize=1)
                for res in contents
            ]
            output.append((pdf, text_contents))
        return output

    def content_with_context(self) -> Sequence[Content]:
        """
        Get content for entire file

        Parameters: -

        Returns:
            Sequence[Content]: sequence of content

        """
        self._content = self._get_content()
        return self._content

    def get_position_for_context(self, context: str, start_pos: int) -> str:
        """
        Get position for current context

        Parameters:
            context (str): Context page number
            start_pos (int): Starting position of current context

        Returns:
            str: page and line number

        """
        page = context
        line_pos = ""
        if "Image" not in context:
            text = [ctx.content for ctx in self._content if ctx.context == page]
            if len(text) != 1:
                raise RuntimeError(
                    f"FIXME {len(text)}, ctx: {context}, txt: {text}"
                )  # Context was not unique
            text = "".join(text)
            line_num = text[0:start_pos].count("\n") + 1
            line_pos = f" Line: {line_num}" if "Page" in page else ""
        return f"{page}{line_pos}"

    def get_neighbor_context_for(
        self, context: str, start_pos: int, end_pos: int
    ) -> str:
        """
        Get neighboring context for current content
        Using inherited get_context()

        Parameters:
            context (str): Context page number
            start_pos (int): Starting position of current context
            end_pos (int): End position of current context

        Returns:
            str: Current neighboring context

        """
        page = context
        text = [ctx.content for ctx in self._content if ctx.context == page]
        if len(text) != 1:
            raise RuntimeError(f"FIXME {len(text)}")  # Context was not unique
        text = "".join(text)

        return self.get_context(text, start_pos, end_pos)

    def page_texts(
        self,
        page_index: int,
        use_image_context: bool,
    ) -> Sequence[Content]:
        """
        Get all text from page, including images and links

        Parameters:
            page_index (int): Page number
            use_image_context (bool): Determine if context for images
                                        should be included

        Returns:
            Sequence[Content]: sequence of content

        """
        page_content: list[Content] = []
        text_content = self.get_page_text_content(page_index, use_image_context)
        if text_content:
            page_content.append(text_content)

        links_contents = self.get_page_links(page_index, use_image_context)
        if links_contents:
            page_content.append(links_contents)

        if self.image_extract:
            image_contents = self.get_words_from_page_images(
                page_index, use_image_context
            )
            if image_contents:
                page_content += image_contents

        return page_content

    def get_page_text_content(self, ix: int, use_image_context: bool) -> Content | None:
        """
        Get text content from given page

        Parameters:
            ix (int): Page index
            use_image_context (bool): Determine if context for images
                                        should be included

        Returns:
            Content: Text content on the page

        """
        pdf = self.pdf()
        page = pdf[ix]
        words: list[tuple[str, list[pymupdf.Rect]]] = []
        # Find words in the PDF
        last_line = None
        last_block = None
        for word in page.get_text("words", delimiters=None):  # type: ignore
            word_text = word[4]
            current_line = word[6]
            current_block = word[5]
            if (
                last_line is not None
                and last_block is not None
                and (current_line > last_line or current_block > last_block)
                and (len(words) > 0)
            ):
                # Add new line to last word since we fall into a new block
                new_word = words[-1][0].strip() + "\n"
                words[-1] = (new_word, words[-1][1])
            elif len(words) > 0 and words[-1][0][-1] != "\n":
                # Add space separation between two words in the same block
                new_word = words[-1][0].strip() + " "
                words[-1] = (new_word, words[-1][1])
            last_line = current_line
            last_block = current_block
            rect = pymupdf.Rect(word[:4])
            words.append((word_text, [rect]))
        if not words:
            return None

        page_text = "".join([w[0] for w in words])
        ctx = (
            PagePositionContext(ix, words, page.rotation)
            if use_image_context
            else f"Page: {ix + 1}"
        )
        return Content(
            ctx,
            page_text,
            self,
        )

    def get_page_links(self, ix: int, use_image_context: bool) -> Content | None:
        """
        Get text from links on given page

        Parameters:
            ix (int): Page index
            use_image_context (bool): Determine if context for
                                        images should be included

        Returns:
            Content: Text content of page links

        """
        pdf = self.pdf()
        page = pdf[ix]
        words: list[tuple[str, list[pymupdf.Rect]]] = []
        # Get embedded links as content too
        for link in page.links(kinds=[pymupdf.LINK_URI]):
            words.append((link["uri"], [link["from"]]))
        if not words:
            return None
        page_links_text = " ".join([w[0] for w in words])
        ctx = (
            PagePositionContext(ix, words, page.rotation)
            if use_image_context
            else f"Link at Page: {ix + 1}"
        )
        return Content(
            ctx,
            page_links_text,
            self,
        )

    @staticmethod
    def get_pix(
        image: tuple, image_dict: dict, pdf: pymupdf.Document
    ) -> pymupdf.Pixmap:
        """
        Get image pixmap

        Parameters:
            image (tuple): image information tuple
            image_dict (dict): image information dict
            pdf (Document): pymupdf document object of the pdf

        Returns:
            Pixmap: image pixmap

        """

        image_mask = image[1]
        colorspace = image[5]
        pix1 = pymupdf.Pixmap(image_dict["image"])
        if colorspace not in [
            "DeviceRGB",
            "DeviceGray",
        ]:  # if colorspace not supported in png
            pix1 = pymupdf.Pixmap(pymupdf.csRGB, pix1)  # set colorspace to RGB
        if image_mask == 0:  # No alpha channel
            pix = pix1
        else:
            im_mask = pdf.extract_image(image_mask)  # Get alpha mask
            mask = pymupdf.Pixmap(im_mask["image"])
            if pix1.alpha:
                pix1 = pymupdf.Pixmap(
                    pix1, 0
                )  # Remove alpha channel to use the separate transparency mask instead
            pix = pymupdf.Pixmap(pix1, mask)
        return pix

    @staticmethod
    def get_bbox_pos(
        data: dict, image_w: int, image_h: int, image_bbox: pymupdf.Rect, idx: int
    ) -> tuple:
        """
        Get bounding box starting point coordinates,
        width and height of word by index

        Parameters:
            data (dict): image data
            image_w (int): image width
            image_h (int): image height
            image_bbox (Rect): image bounding box
            idx (int): word index in image wordlist

        Returns:
            tuple: words bounding box x0, y0, width and height

        """
        (
            word_in_image_x,
            word_in_image_y,
            word_in_image_w,
            word_in_image_h,
        ) = word_positions(data, idx)
        proc_x = word_in_image_x / image_w
        proc_y = word_in_image_y / image_h

        scale_w = image_bbox.width / image_w
        scale_h = image_bbox.height / image_h

        bbox_x = image_bbox.tl.x + image_bbox.width * proc_x
        bbox_y = image_bbox.tl.y + image_bbox.height * proc_y
        bbox_w = word_in_image_w * scale_w
        bbox_h = word_in_image_h * scale_h
        return bbox_x, bbox_y, bbox_w, bbox_h

    @staticmethod
    def separate_words(
        rect: pymupdf.Rect, last_rect: pymupdf.Rect | None, words: list
    ) -> list:
        """
        Separate current and previous word

        Parameters:
            rect (Rect): bounding box of current word
            last_rect (Rect | None): bounding box of previous image
            words (list): list of found words

        Returns:
            list: list of with correct separator

        """
        if last_rect is not None and rect_is_at_new_line(last_rect, rect):
            # Add new line
            new_word = words[-1][0] + "\n"
            words[-1] = (new_word, words[-1][1])
        elif len(words) > 0 and words[-1][0][-1] != "\n":
            # Add space to separate words
            new_word = words[-1][0].strip() + " "
            words[-1] = (new_word, words[-1][1])
        return words

    def get_image_words(
        self, pix: pymupdf.Pixmap, image_dict: dict, image_bbox: pymupdf.Rect
    ) -> list:
        """
        Get text specific image

        Parameters:
            pix (Pixmap): Image pixmap
            image_dict (dict): dictionary representation of image
            image_bbox (Rect): bounding box of image

        Returns:
            list: words found in the image

        """
        with Image.open(io.BytesIO(pix.tobytes("png"))) as image_copy:
            data = data_from_image_bytes(image_copy)
        words: list[tuple[str, list[pymupdf.Rect]]] = []
        last_rect = None
        for j in range(word_count(data)):
            word = word_from_data(data, j)
            if not word:
                continue

            image_width = image_dict["width"]
            image_height = image_dict["height"]
            bbox_x, bbox_y, bbox_w, bbox_h = self.get_bbox_pos(
                data,
                image_width,
                image_height,
                image_bbox,
                j,
            )
            rect = pymupdf.Rect(
                x0=bbox_x, y0=bbox_y, x1=bbox_x + bbox_w, y1=bbox_y + bbox_h
            )
            words = self.separate_words(rect, last_rect, words)
            last_rect = rect
            words.append((word, [rect]))
        return words

    def get_words_from_page_images(
        self, ix: int, use_image_context: bool
    ) -> Sequence[Content] | None:
        """
        Get text from images on given page

        Parameters:
            ix (int): Page index
            use_image_context (bool): Determine if context for
                                        images should be included

        Returns:
            Sequence[Content]: Text contents of images on page

        """
        pdf = self.pdf()
        page = pdf[ix]
        image_contents = []
        # Find images in the page
        images = page.get_images(full=True)
        for image_ix, image_in_page in enumerate(images):
            if not page.get_image_rects(image_in_page):  # type: ignore
                continue  # continue if page holds ref to image, but the image is not drawn on the page

            image_xref = image_in_page[0]
            ima = pdf.extract_image(image_xref)
            # Transformed image (respects rotation)
            image_bbox: pymupdf.Rect = page.get_image_rects(image_in_page)[0]  # type: ignore
            pix = self.get_pix(image_in_page, ima, pdf)
            try:
                words = self.get_image_words(pix, ima, image_bbox)
                if not words:
                    continue
                all_text = "".join([word[0] for word in words])
                ctx = (
                    PagePositionContext(ix, words, page.rotation)
                    if use_image_context
                    else f"Page: {ix + 1}, Image: {image_ix + 1}"
                )
                image_contents.append(
                    Content(
                        ctx,
                        all_text,
                        self,
                    )
                )
            except Exception as e:
                logger.error("Error when processing image", e)
        return image_contents
