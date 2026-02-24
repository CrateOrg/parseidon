import os
from typing import Any, Sequence

import magic

from parseidon.files.excelfile import ExcelFile
from parseidon.files.file import File
from parseidon.files.image_file import ImageFile
from parseidon.files.legacy_excelfile import LegacyExcelFile
from parseidon.files.legacy_wordfile import LegacyWordFile
from parseidon.files.pdf_file import PdfFile
from parseidon.files.textfile import TextFile
from parseidon.files.wordfile import WordFile
from parseidon.handlers.handler import Handler

FileHandlerInput = Sequence[str]
FileHandlerOutput = Sequence[File]


class FileHandler(Handler[FileHandlerInput, FileHandlerOutput]):
    """
    Class for handling files

    Attributes:
        image_extract (bool): Determines if OCR should be used
        column_context (bool): Determines direction of reading context
                                Only for ExcelFiles
    """

    def __init__(self, image_extract: bool, column_context: bool) -> None:
        """
        Initializes a FileHandler object

        Parameters:
            image_extract (bool): Determines if OCR should be used
            column_context (bool): Determines direction of reading context
                                    Only for ExcelFiles
        """
        super().__init__()
        self.image_extract = image_extract
        self.column_context = column_context

    def handle_input(self, input: FileHandlerInput) -> FileHandlerOutput:
        """
        For each filepath in the input, open the corresponding file
        using a filefactory

        Parameters:
            input (FileHandlerInput): List of filenames

        Returns:
            FileHandlerOutput: List of Files
        """
        files = []
        for input_path in input:
            files.append(
                FileHandler._file_from_filepath(
                    input_path,
                    image_extract=self.image_extract,
                    column_context=self.column_context,
                )
            )
        return files

    @staticmethod
    def _file_from_filepath(filepath: str, **kwargs) -> File:
        """
        Implementation of the factory-pattern for creating different
        file objects from the given filepath

        Parameters:
            filepath (str): Path to file
        Keyword arguments:
            image_extract (bool): Determines if OCR should be used
            column_context (bool): Determines direction of reading context

        Returns:
            File: File object created in factory
        """
        file_name = os.path.basename(filepath)
        file_dir = os.path.dirname(filepath)
        ext = os.path.splitext(file_name)[1]
        similar_docs = {".ods": ".xls", ".odt": ".doc", ".eps": ".png"}
        sub_classes: dict[str, tuple[type[File], Any]] = {
            ".txt": (TextFile, set()),
            ".docx": (WordFile, {"image_extract"}),
            ".doc": (LegacyWordFile, {"image_extract"}),
            ".xlsx": (ExcelFile, {"column_context", "image_extract"}),
            ".xls": (LegacyExcelFile, {"column_context", "image_extract"}),
            ".pdf": (PdfFile, {"image_extract"}),
            ".png": (ImageFile, {"image_extract"}),
        }
        class_type = similar_docs.get(ext, ext)
        if class_type not in sub_classes:
            f = magic.Magic(mime=True)
            filetype = f.from_file(filepath)
            if filetype == "text/plain":
                class_type = ".txt"
            elif filetype.startswith("image"):
                class_type = ".png"
            else:
                raise RuntimeError(f"Unable to handle file {filepath}")

        obj, op_args = sub_classes[class_type]
        cur_kwargs = {key: val for key, val in kwargs.items() if key in op_args}
        return obj(file_name, ext, file_dir, **cur_kwargs)
