import os
import subprocess
import tempfile

from parseidon.files.excelfile import ExcelFile


class LegacyExcelFile(ExcelFile):
    """
    Subclass to ExcelFile that simply converts unparsable files
    to a .xlsx file in order to parse it.

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
        Initializes an legacyexcel file object and converts it to
        an excelfile object

        Parameters:
            name (str): Filename
            filetype (str): File-extension/type
            path (str): Path to file
            column_context (bool): Determines direction of reading context
            image_extract (bool): Determines if OCR should be used
        """
        self.original_name = os.path.join(path, name)
        with tempfile.TemporaryDirectory() as temp_dir:
            subprocess.call(
                [
                    "soffice",
                    "--headless",
                    "--convert-to",
                    "xlsx",
                    "--outdir",
                    temp_dir,
                    os.path.join(path, name),
                ],
                stderr=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
            )
            name = os.path.splitext(name)[0] + ".xlsx"
            super().__init__(name, filetype, temp_dir, column_context, image_extract)
            temp_file = os.path.join(temp_dir, name)
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def file_path(self) -> str:
        return self.original_name
