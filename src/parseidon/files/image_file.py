import io
import logging
import os
from typing import Sequence, Any

from cairosvg import svg2png
from PIL import Image

from parseidon.files.file import File
from parseidon.handlers.content import Content
from parseidon.helpers.image_helper import get_text_from_image_bytes

logger = logging.getLogger(__name__)


class ImageFile(File):
    """
    Subclass for representing image files

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
        Initializes an image file object

        Parameters:
            name (str): Filename
            filetype (str): File-extension/type
            path (str): Path to file
            image_extract (bool): Determines if OCR should be used
        """
        super().__init__(name, filetype, path, image_extract)
        self.image = os.path.join(self.path, self.name)
        self._content = self._get_content()

    def _get_content(self) -> str:
        """
        Getting image text with tesseract.
        Only used if --image_extract flag is set.

        Parameters: -

        Returns:
            str: Imagetext found with OCR
        """
        text = ""
        if not self.image_extract:
            return text
        if self.filetype == ".svg":
            return self.svg_content()
        try:
            with Image.open(self.image) as img:
                image = img.convert("RGB")
                text = get_text_from_image_bytes(image)
        except Exception as e:
            logger.error(f"Error when processing image: {e}")
        return text

    def svg_content(self) -> str:
        """
        Helper to get_content for SVG-images.

        Parameters: -

        Returns:
            str: Imagetext found with OCR
        """
        text = ""
        with open(self.image) as svg:
            byte_stream = svg.read().encode("utf-8")
            png = svg2png(bytestring=byte_stream, dpi=300)
        if not png:
            logger.error("Could not convert SVG to PNG!")
            return text
        image = io.BytesIO(png)
        try:
            with Image.open(image) as img:
                text = get_text_from_image_bytes(img)
        except Exception as e:
            logger.error(f"Error when processing image: {e}")
        return text

    def content_with_context(self) -> Sequence[Content]:
        """
        Simply returns content, since image content has no
        neighboring content for context.

        Parameters: -

        Returns:
            Content: Current content
        """
        return [Content(None, self._content, self)]

    def get_position_for_context(self, context: Any, start_pos: Any) -> str:
        """
        Returns the position of context as being
        part of an image.

        Parameters:
            context (str): Not used
            start_pos (int): Not used

        Returns:
            str: "In image"
        """
        return "In image"

    def get_neighbor_context_for(
        self, context: Any, start_pos: int, end_pos: int
    ) -> str:
        """
        Calls super.get_context()
        Get context(previous and upcoming words) of given
        word.

        Parameters:
            start (int): Start index of match/word in content
            end (int): End index of match/word in content
            context (str): not used

        Returns:
            str: The context of the word located from start to end
            in the text(content)
        """
        return self.get_context(self._content, start_pos, end_pos)
