import os
import shutil
import subprocess
import tempfile
from typing import Sequence, Tuple
import pymupdf

from parseidon.files.file import File
from parseidon.files.pdf_file import PdfFile
from parseidon.handlers.content import Content
from parseidon.handlers.file_handler import FileHandlerOutput
from parseidon.handlers.handler import Handler
from parseidon.plugin_manager import load_plugins

ContentHandlerInput = FileHandlerOutput
ContentHandlerOutput = Sequence[Tuple[File | pymupdf.Document, Sequence[Content]]]


class ContentHandler(Handler[ContentHandlerInput, ContentHandlerOutput]):
    """
    Class for finding and handling matches in Pegaparsemode

    Attributes:
        draw_boxes (bool): Determines if output should be text format or
                            visual rectangles in pdf-format
        num_threads (int): Number of threads to be utilized
    """

    def __init__(self, draw_boxes: bool, num_threads: int, trie=None) -> None:
        """
        Initializes ContentHandler object

        Parameters:
            draw_boxes (bool): Determines if output should be text format or
                                visual rectangles in pdf-format
            num_threads (int): Number of threads to be utilized
        """
        super().__init__()
        self.draw_boxes = draw_boxes
        self.num_threads = num_threads
        self.pm = load_plugins()
        self.trie = trie

    def handle_input(
        self, input: Sequence[File]
    ) -> Sequence[Tuple[File | pymupdf.Document, Sequence[Content]]]:
        """
        For each file in the input list, get the correct content.

        Parameters:
            input (sequence): List of files to retrieve content from

        Returns:
            Sequence: List of tuples, (file, list of contents)
        """
        output: ContentHandlerOutput = []
        for file in input:
            if not self.draw_boxes:
                output.append((file, file.content_with_context()))  # type: ignore
                continue
            file_to_ocr, is_tmp_file = self.convert_to_pdf(file)  # type: ignore
            output += file_to_ocr.document_content(self.num_threads)
            if is_tmp_file:
                shutil.rmtree(file_to_ocr.path)
        self.pm.hook.post_process_content(output=output, trie_file=self.trie)

        return output

    def convert_to_pdf(self, file: File) -> Tuple[PdfFile, bool]:
        """
        If needed, convert file into a pdf

        Parameters:
            file (File): file to be converted(if needed)

        Returns:
            Tuple: PdfFile, if file has been converted to pdf(is temp)
        """
        if isinstance(file, PdfFile):
            file_to_ocr = file  # No need to convert
            is_tmp_file = False
        else:
            # Convert to pdffile
            with tempfile.TemporaryDirectory(delete=False) as temp_dir:
                subprocess.call(
                    [
                        "soffice",
                        "--headless",
                        "--convert-to",
                        "pdf",
                        "--outdir",
                        temp_dir,
                        file.file_path(),
                    ],
                    stderr=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                )
                name = os.path.splitext(file.name)[0] + ".pdf"
                file_to_ocr = PdfFile(name, ".pdf", temp_dir, file.image_extract)
                is_tmp_file = True
        return file_to_ocr, is_tmp_file
