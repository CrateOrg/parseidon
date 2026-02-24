from parsimonious import Grammar, NodeVisitor
from typing import Any
from parseidon.handlers.content import Content, PagePositionContext, ContentContext
from parseidon.handlers.match import Match
from parseidon.handlers.matcher_handlers.matcher_handler import (
    MatcherHandler,
    _get_image_position,
)


class PegParseMatcherHandler(MatcherHandler):
    """
    Class for finding and handling matches in Pegaparsemode

    Attributes:
        grammar (Grammar): Current Parsimonious grammar used to find matches
        skip_list (set): Possible matches that should be ignored
    """

    def __init__(self, grammar: Grammar, skip_list: set[str]) -> None:
        """
        Initializes PegParseMatcherHandler object

        Parameters:
            grammar (Grammar): Current Parsimonious grammar used to find matches
            skip_list (set): Possible matches that should be ignored
        """
        super().__init__(lambda file: self.__get_matches(file))
        self.grammar = grammar
        self.skip_list = skip_list

    def __get_matches(self, curr_content: Content) -> list[Match]:
        """
        Finds pegparsemode match-objects from current document content

        Parameters:
            curr_content (Content): The current page/document content

        Returns:
            List: List of matches (if there are any)
        """
        matches = []
        context_info = curr_content.context
        text = curr_content.content
        if not text:
            return []
        parser = self.grammar.parse(text)
        visitor_matches = self._Visitor(
            file_path=curr_content.owner_file.file_path(),
            file=curr_content.owner_file,
            context_info=context_info,
            all_text=text,
        ).visit(parser)
        matches += [
            match
            for match in visitor_matches
            if match.found_object not in self.skip_list and match is not None
        ]

        return matches

    class _Visitor(NodeVisitor):
        """
        Subclass to NodeVisitor, to implement visitor methods for
        Parsimonious rules.

        Attributes:
            file_path (str): Current filepath
            file (Any): Current file
            context_info (ContentContext): Current context information
            all_text (str): Current page/section text

        """

        def __init__(
            self, file_path: str, file: Any, context_info: ContentContext, all_text: str
        ) -> None:
            """
            Initializes Visitor objects

            Attributes:
                file_path (str): Current filepath
                file (Any): Current file
                context_info (ContentContext): Current context information
                all_text (str): Current page/section text
            """
            super().__init__()
            self.file_path = file_path
            self.file = file
            self.context_info = context_info
            self.all_text = all_text

        def _node_match(self, type: str, node: Any) -> Match | None:
            """
            Creates match objects from objects found by Parsimonious

            Parameters:
                type (str): Matched object type
                node (Any): Current AST node

            Returns:
                Match | None: Found match object or None
            """
            if isinstance(self.context_info, PagePositionContext):
                image_pos = _get_image_position(
                    node.start, node.end, self.all_text, self.context_info
                )
                if not image_pos:
                    return
                return Match(
                    type,
                    node.text,
                    self.file_path,
                    (self.context_info.page, image_pos),
                    "",
                )
            else:
                return Match(
                    type,
                    node.text,
                    self.file_path,
                    self.file.get_position_for_context(self.context_info, node.start),
                    self.file.get_neighbor_context_for(
                        self.context_info, node.start, node.end
                    ),
                )

        def visit_mult(self, node, visited_children):
            return [c[0] for c in visited_children if isinstance(c[0], Match)]

        def visit_doc_id(self, node, visited_children):
            return self._node_match("Doc_ID", node)

        def visit_email(self, node, visited_children):
            return self._node_match("Email", node)

        def visit_ip(self, node, visited_children):
            return self._node_match("IPv4", node)

        def visit_mac(self, node, visited_children):
            return self._node_match("MAC", node)

        def visit_wifi(self, node, visited_children):
            return self._node_match("WiFi", node)

        def visit_tech_prot(self, node, visited_children):
            return self._node_match("Tech/Protocol", node)

        def visit_unit(self, node, visited_children):
            return self._node_match("Unit", node)

        def visit_date(self, node, visited_children):
            return self._node_match("Date", node)

        def visit_ipv6(self, node, visited_children):
            return self._node_match("IPv6", node)

        def visit_phonenumber(self, node, visited_children):
            return self._node_match("Phonenumber", node)

        def visit_url(self, node, visited_children):
            return self._node_match("URL", node)

        def generic_visit(self, node, visited_children):
            return visited_children or node
