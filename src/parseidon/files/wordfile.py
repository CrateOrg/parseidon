import io
import logging
import os
import zipfile
from typing import Any, Sequence

from docx import Document
from docx.table import Table
from lxml import etree as ET
from PIL import Image

from parseidon.files.file import File
from parseidon.handlers.content import Content
from parseidon.helpers.image_helper import get_text_from_image_bytes

logger = logging.getLogger(__name__)


class WordFile(File):
    """
    Subclass for representing wordfiles
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
        Initializes an wordfile object

        Parameters:
            name (str): Filename
            filetype (str): File-extension/type
            path (str): Path to file
            column_context (bool): Determines direction of reading context
            image_extract (bool): Determines if OCR should be used
        """
        super().__init__(name, filetype, path, image_extract)
        self.doc = Document(os.path.join(self.path, self.name))
        self._content = self._get_content()

    def _get_content(self) -> dict[Any, str]:
        """
        Read content wordfile into dictionary

        Parameters: -

        Returns:
            dict: {Position: content}
        """
        paragraphs = {}
        index = 1
        for para in self.doc.paragraphs:
            if not para.text.strip():
                continue
            paragraphs[f"Paragraph: {index}"] = para.text.strip()
            index += 1
        paragraphs.update(self.get_special_content())

        return paragraphs

    def get_special_content(self) -> dict[Any, str]:
        """
        Helper to get special content

        Parameters: -

        Returns:
            dict: containing all special content
        """
        return (
            self.get_footers()
            | self.get_headers()
            | self.get_tables()
            | self.get_footnotes()
            | self.get_images(self.image_extract)
            | self.get_inline_shapes()
            | self.get_figures()
        )

    def get_table_content(self, table: Table) -> str:
        """
        Get text content from specified table

        Parameters:
            table (Table): Current wordfile table

        Returns:
            str: Contents of table
        """
        visited_cells = set()
        table_content = []
        for row in table.rows:
            for i in range(len(row.cells)):
                # check that cell xml element has not been visited
                if row.cells[i]._tc not in visited_cells:
                    table_content.append(row.cells[i].text.strip())
                    visited_cells.add(row.cells[i]._tc)
        return "\n".join(table_content)

    def get_tables(self) -> dict[Any, str]:
        """
        Helper function to get data from every table

        Parameters: -

        Returns:
            dict[Any, str]: {Table number: table content}
        """
        all_table_text = {}
        for index, table in enumerate(self.doc.tables):
            all_table_text[f"Table: {index+1}"] = self.get_table_content(table)
        return all_table_text

    def get_headers(self) -> dict[Any, str]:
        """
        Get text content from headers

        Parameters: -

        Returns:
            dict[Any, str]: {Section number, header type: header content}
        """
        header_text = {}
        visited = set()

        for section_index, section in enumerate(self.doc.sections):
            headers = {
                section.first_page_header: "first page header",
                section.header: "default header",
                section.even_page_header: "even page header",
            }

            for header in headers:
                text = " ".join(
                    para.text for para in header.paragraphs if para.text.strip()
                )
                if text and text not in visited:
                    header_text[f"Section: {section_index + 1}, {headers[header]}"] = (
                        text
                    )
                    visited.add(text)

        return header_text

    def get_footers(self) -> dict[Any, str]:
        """
        Get text content from footers

        Parameters: -

        Returns:
            dict[Any, str]: {Section number, footer type: footer content}
        """
        footer_text = {}
        visited = set()

        for section_index, section in enumerate(self.doc.sections):
            footers = {
                section.first_page_footer: "first page footer",
                section.footer: "default footer",
                section.even_page_footer: "even page footer",
            }

            for footer in footers:
                text = " ".join(
                    para.text for para in footer.paragraphs if para.text.strip()
                )
                if text and text not in visited:
                    footer_text[f"Section: {section_index + 1}, {footers[footer]}"] = (
                        text
                    )
                    visited.add(text)

        return footer_text

    def get_footnotes(self) -> dict[Any, str]:
        """
        Method that opens docx file as a zip and reads the footnotes
        xml structure to find all footnotes tags and extract text from all
        text tags inside each footnote tag.

        Parameters: -

        Returns:
            dict[Any, str]: {Footnote number: footnote text}
        """
        footnotes = {}
        # 1: open wordfile as a zip
        with zipfile.ZipFile(os.path.join(self.path, self.name), "r") as zip:
            # 2: check if footnotes.xml exists in the zip
            # print(zip.namelist())
            if "word/footnotes.xml" in zip.namelist():
                # 3: Create a XML-tree from footnotes.xml
                xml_fn = zip.read("word/footnotes.xml")
                tree = ET.fromstring(xml_fn)
                namespaces: dict[str, str] = tree.nsmap  # type: ignore
                index = 1
                # 4: find all footnote tags and extract the text tags within
                for footnote in tree.findall(".//w:footnote", namespaces=namespaces):
                    text_tags = footnote.xpath(".//w:t", namespaces=namespaces)
                    full_text = "".join(
                        text.text for text in text_tags if text is not None  # type: ignore
                    )
                    if full_text.strip():
                        footnotes[f"Footnote: {index}"] = full_text.strip()
                        index += 1
        return footnotes

    def get_images(self, image_extract: bool) -> dict[Any, str]:
        """
        Method that opens docx file as a zip and reads the
        xml structure to find all image and extract text from them
        using Tesseract.

        This functionality is only used if --image_extract flag is set

        Parameters:
            image_extract (bool): determine if OCR should be used

        Returns:
            dict: {Image number: content of image}
        """
        if not image_extract:
            return {}

        image_texts = {}
        # 1: Open wordfile as a zip
        with zipfile.ZipFile(os.path.join(self.path, self.name), "r") as zip:
            # 2: Get all files from media folder
            image_files = [f for f in zip.namelist() if f.startswith("word/media/")]
            index = 1
            for file in image_files:
                # 3: loop over all image files, try to open them as PIL images
                # and extract text with Tesseract
                with zip.open(file) as img:
                    try:
                        byte_stream = io.BytesIO(img.read())
                        with Image.open(byte_stream) as image:
                            image_text = get_text_from_image_bytes(image)
                            if not image_text:
                                continue
                            image_texts[f"Image: {index}"] = image_text
                        index += 1
                    except Exception as e:
                        logger.error(f"Error when processing image: {e}")
        return image_texts

    def get_figures(self) -> dict[Any, str]:
        """
        Method that opens docx file as a zip and reads the
        xml structure to find all charts and diagrams, and
        extract text from them

        Parameters:-

        Returns:
            dict: {Figure number: content of figure}
        """
        figure_texts = {}
        # 1: Open wordfile as a zip
        with zipfile.ZipFile(os.path.join(self.path, self.name), "r") as zip:
            # 2: Get all charts and diagram files
            figures_files = [
                f
                for f in zip.namelist()
                if (f.startswith("word/charts/") or f.startswith("word/diagrams/data"))
                and f.endswith(".xml")
            ]
            index = 1
            for file in figures_files:
                xml_fn = zip.read(file)
                tree = ET.fromstring(xml_fn)
                namespaces: dict[str, str] = tree.nsmap  # type: ignore
                titles = [
                    t.text
                    for t in tree.iterfind(".//a:t", namespaces=namespaces)
                    if t.text
                ]
                fields = (
                    [t.text for t in tree.iterfind(".//c:v", namespaces=namespaces)]
                    if "c" in namespaces
                    else []
                )
                unique_fields = list(
                    key if key is not None else ""
                    for key in dict.fromkeys(fields).keys()
                )
                texts = titles + unique_fields
                if texts:
                    figure_texts[f"Figure: {index}"] = " ".join(texts)

                index += 1
            return figure_texts

    def get_inline_shapes(self) -> dict[Any, str]:
        """
        Method that gets text from textboxes inside inline shapes

        Parameters:-

        Returns:
            dict: {Inline shape number: content of inline shape}
        """
        # 1: get all inline shapes
        inline_shapes = self.doc.inline_shapes._body.xpath(".//w:txbxContent")
        prev_text = ""
        shapes_dict = {}
        # 2: loop over inline shapes and get the child objects
        for index, shape in enumerate(inline_shapes):
            children = shape.getchildren()
            shape_text = ""
            # 3 : loop over children and save the text
            for child in children:
                shape_text += child.text
            # ensure shape has text and is not duplicated(VML)
            if shape_text == prev_text or not shape_text:
                continue
            prev_text = shape_text
            shapes_dict[f"Inline shape: {index + 1}"] = shape_text

        return shapes_dict

    def content_with_context(self) -> Sequence[Content]:
        """
        Get content with its context for every paragraph
        in the document

        Parameters: -

        Returns:
            Sequence[Content]: sequence of paragraph contents,
                                with context

        """
        return [
            Content(paragraph, self._content[paragraph], self)
            for paragraph in self._content
        ]

    def get_position_for_context(self, context: str, start_pos: Any) -> str:
        """
        Simply returns the current context

        Parameters:
            context (str): Current context
            start_pos (Any): not used by wordfiles

        Returns:
            str: Current context
        """
        return context

    def get_neighbor_context_for(
        self, context: str, start_pos: int, end_pos: int
    ) -> str:
        """
        Gets the neighbor context for current content

        Parameters:
            context (str): Current context
            start_pos (int): Start position of current content
            end_pos (int): End position of current content

        Returns:
            str: Neighbor context
        """
        paragraph = context
        return self.get_context(self._content[paragraph], start_pos, end_pos)
