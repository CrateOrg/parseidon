import os
import subprocess
import tempfile

from parseidon.files.wordfile import WordFile


class LegacyWordFile(WordFile):
    """
    Subclass to WordFile that simply converts unparsable files
    to a .docx file in order to parse it.
    """

    def __init__(
        self, name: str, filetype: str, path: str, image_extract: bool
    ) -> None:
        """
        Initializes an legacywordfile object and converts it to
        an wordfile object

        Parameters:
            name (str): Filename
            filetype (str): File-extension/type
            path (str): Path to file
            image_extract (bool): Determines if OCR should be used
        """
        self.original_name = os.path.join(path, name)
        with tempfile.TemporaryDirectory() as temp_dir:
            subprocess.call(
                [
                    "soffice",
                    "--headless",
                    "--convert-to",
                    "docx",
                    "--outdir",
                    temp_dir,
                    os.path.join(path, name),
                ],
                stderr=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
            )
            name = os.path.splitext(name)[0] + ".docx"
            super().__init__(name, filetype, temp_dir, image_extract)
            temp_file = os.path.join(temp_dir, name)
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def file_path(self) -> str:
        return self.original_name
