from typing import Any
from parseidon.handlers.content import Content, PagePositionContext
from parseidon.handlers.match import Match
from parseidon.handlers.matcher_handlers.matcher_handler import (
    MatcherHandler,
    _get_image_position,
)
import logging

logger = logging.getLogger(__name__)


class RegexMatcherHandler(MatcherHandler):
    """
    Class for finding and handling matches in Regexmode

    Attributes:
        patterns (dict): Dictionary with regexpatterns to find matches
        skip_list (set): Possible matches that should be ignored
    """

    def __init__(self, patterns: dict, skip_list: set[str]) -> None:
        """
        Initializes RegexMatcherHandler object

        Parameters:
            patterns (dict): Dictionary with regexpatterns to find matches
            skip_list (set): Possible matches that should be ignored
        """
        super().__init__(lambda file: self.__get_matches(file))
        self.patterns = patterns
        self.skip_list = skip_list

    def __get_matches(self, curr_content: Content) -> Any:
        """
        Finds regex match-objects from current document content

        Parameters:
            curr_content (Content): The current page/document content

        Returns:
            Any: List of matches (if there are any)
        """
        matches = []

        for pattern in self.patterns:
            context_info = curr_content.context
            text = curr_content.content
            regex_matches = list(self.patterns[pattern].finditer(text))
            for match in regex_matches:
                found_object = match.group()
                if found_object in self.skip_list:
                    continue
                if isinstance(context_info, PagePositionContext):
                    image_pos = _get_image_position(
                        match.start(), match.end(), text, context_info
                    )
                    if not image_pos:
                        logger.error(
                            f"Could not find image position of '{found_object}'"
                        )
                        continue
                    m = Match(
                        pattern,
                        found_object,
                        curr_content.owner_file.file_path(),
                        (context_info.page, image_pos),
                        "",
                    )
                else:
                    m = Match(
                        pattern,
                        found_object,
                        curr_content.owner_file.file_path(),
                        curr_content.owner_file.get_position_for_context(
                            context_info, match.start()
                        ),
                        curr_content.owner_file.get_neighbor_context_for(
                            context_info, match.start(), match.end()
                        ),
                    )
                matches.append(m)

        return matches
