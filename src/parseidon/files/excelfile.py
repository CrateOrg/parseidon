import io
import logging
import os
from typing import Any, Sequence

import pandas as pd
from openpyxl import load_workbook
from PIL import Image

from parseidon.files.file import File
from parseidon.handlers.content import Content, ExcelContext
from parseidon.helpers.image_helper import get_text_from_image_bytes

logger = logging.getLogger(__name__)


class ExcelFile(File):
    """
    Subclass for representing excel files

    Attributes:
        name (str): Filename
        filetype (str): File-extension/type
        path (str): Path to file
        column_context (bool): Determines direction of reading context
        image_extract (bool): Determines if OCR should be used
    """

    def __init__(
        self,
        name: str,
        filetype: str,
        path: str,
        column_context: bool,
        image_extract: bool,
    ) -> None:
        """
        Initializes an excel file object

        Parameters:
            name (str): Filename
            filetype (str): File-extension/type
            path (str): Path to file
            column_context (bool): Determines direction of reading context
            image_extract (bool): Determines if OCR should be used
        """
        super().__init__(name, filetype, path, image_extract)
        self.column_context = column_context
        self.sheets_dict = pd.read_excel(
            os.path.join(self.path, self.name),
            engine="openpyxl",
            sheet_name=None,
            header=None,
        )
        self._content = self._get_content()

    def _get_content(self) -> dict[Any, str]:
        """
        Read content from excelfile into dataframe

        Parameters: -

        Returns:
            dict: position of cell, content of cell
        """
        strings_dict = {}
        for sheetnum, df in self.sheets_dict.items():
            sheet_number = int(sheetnum[5:])
            for row in range(df.shape[0]):
                for col in range(df.shape[1]):
                    if df.iat[(row, col)] == df.iat[(row, col)]:  # leave out NaNs
                        strings_dict[(row, col, sheet_number)] = str(df.iat[row, col])
            if self.image_extract:
                strings_dict.update(self.get_images())

        return strings_dict

    def get_images(self) -> dict[Any, str]:
        """
        Finds all images in excel sheets and extracts text from them
        using Tesseract.

        This functionality is only used if --image_extract flag is set

        Parameters: -

        Returns:
            dict: {position of image: content of image}
        """
        image_texts = {}
        workbook = load_workbook(os.path.join(self.path, self.name))
        # 1: loop over sheets in document
        for sheet_index, sheet_name in enumerate(workbook.sheetnames, start=1):
            sheet = workbook[sheet_name]
            # 2: loop through images in sheet, try to extract text and position
            for img in sheet._images:  # type: ignore
                pos = ("-", "-")
                with io.BytesIO(img._data()) as byte_stream:
                    try:
                        anc = img.anchor._from
                        pos = (anc.row + 1, anc.col + 1)
                        with Image.open(byte_stream) as image:
                            text = get_text_from_image_bytes(image)
                            if not text:
                                continue
                            image_texts[
                                (pos[0], pos[1], f"Image in Sheet: {sheet_index}")
                            ] = text
                    except Exception as e:
                        logger.error(f"Error when processing image: {e}")
        return image_texts

    def get_neighbor_context(
        self, content: dict, row: int, col: int, sheetnum: int
    ) -> str:
        """
        Get neigboring context of current cell(row, col).
        Gets context from column- or row-based neighbors
        depending on the --column_context flag.

        Parameters:
            content (dict): Current content
            row (int): Row number
            col (int): Column number
            sheetnum (int): Sheet number

        Returns:
            str: neighboring context of current cell(row, col)

        """
        if not self.column_context:
            return " ".join(
                [
                    content[(row, c, sheetnum)]
                    for c in range(col - 1, col + 2)
                    if (row, c, sheetnum) in content
                ]
            )
        return " ".join(
            [
                content[(r, col, sheetnum)]
                for r in range(row - 1, row + 2)
                if (r, col, sheetnum) in content
            ]
        )

    def content_with_context(self) -> Sequence[Content]:
        """
        Get content with its context for entire file

        Parameters: -

        Returns:
            Sequence[Content]: sequence of contents, with context

        """
        return [
            Content(ExcelContext(cell[0], cell[1], cell[2]), self._content[cell], self)
            for cell in self._content
        ]

    def get_position_for_context(self, context: ExcelContext, start_pos: Any) -> str:
        """
        Get position for current context

        Parameters:
            context (ExcelContext): Current context
            start_pos (Any): not used by excelfiles

        Returns:
            str: sheet, row and column number for current context.

        """
        return f"Sheet: {context.sheetnum}, Row: {context.row}, Column: {context.col}"

    def get_neighbor_context_for(
        self, context: ExcelContext, start_pos: Any, end_pos: Any
    ) -> str:
        """
        Get neighbor context for current content

        Parameters:
            context (ExcelContext): current context
            start_pos: not used by excelfiles
            end_pos: not used by excelfiles

        Returns:
            str: neighboring context of current cell(row, col)

        """
        return self.get_neighbor_context(
            self._content,
            row=context.row,
            col=context.col,
            sheetnum=int(context.sheetnum),
        )
