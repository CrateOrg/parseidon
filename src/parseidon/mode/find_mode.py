import re
from argparse import ArgumentParser, _SubParsersAction
from dataclasses import dataclass
from typing import Sequence, Tuple

import pymupdf
import yaml
from parsimonious import Grammar

from parseidon.files.file import File
from parseidon.handlers.chain import Chain
from parseidon.handlers.content import Content
from parseidon.handlers.content_handler import ContentHandler
from parseidon.handlers.conversion_handler import ConversionHandler
from parseidon.handlers.file_handler import FileHandler
from parseidon.handlers.image_painter_handler import ImagePainterHandler
from parseidon.handlers.matcher_handlers.filter_matcher_handler import (
    FilterMatcherHandler,
)
from parseidon.handlers.matcher_handlers.peg_parse_matcher_handler import (
    PegParseMatcherHandler,
)
from parseidon.handlers.matcher_handlers.regex_matcher_handler import (
    RegexMatcherHandler,
)
from parseidon.handlers.output_handler import OutputFormat, OutputHandler, OutputMode
from parseidon.helpers.resource_loader import file_exists, open_file
from parseidon.mode.mode import ModeConfig, ProgramMode
from parseidon.plugin_manager import PluginManager


@dataclass
class FindModeConfig(ModeConfig):
    output: str
    num_threads: int
    image_extract: bool
    mode: str
    trie_file: str
    skip_list: str | None
    match_grammar_file: str | None
    enable_plugins: bool


class FindMode(ProgramMode):
    """
    Class representing the FindMode

    Attributes:
        config (FindModeConfig): Configuration from user
    """

    command = "find"

    @classmethod
    def _config_from_args(cls, args) -> FindModeConfig:
        if args.regex:
            mode = "regex"
        else:
            mode = "pegparse"
        return FindModeConfig(
            args.output,
            args.num_threads,
            args.image_extract,
            mode,
            args.trie_file,
            args.skip_list,
            args.match_grammar_file,
            args.enable_plugins,
        )

    def __init__(self, config: FindModeConfig) -> None:
        """
        Initializes FindMode objects

        Parameters:
            config (FindModeConfig): Configuration from user
        """
        super().__init__(config)
        self.mode = config.mode
        if self.mode == "regex":
            grammar_file = (
                "regex_files/main_regex.yaml"
                if config.match_grammar_file is None
                else config.match_grammar_file
            )
            self.grammar = self._compile_patterns(grammar_file, None)
        else:
            grammar_file = (
                "peg_files/peg_grammars.txt"
                if config.match_grammar_file is None
                else config.match_grammar_file
            )
            self.grammar = self._read_grammar(grammar_file)

    def _read_grammar(self, grammar_file: str) -> Grammar:
        """
        Fetches PEG-grammar from file

        Parameters:
            grammar_file (str): Filepath to grammar

        Returns:
            Grammar: Parsimonious grammar rules
        """
        with open_file(grammar_file, "r") as f:
            grammar_text = f.read()
        return Grammar(grammar_text)

    def _compile_patterns(self, regex_file: str, type_filter: list | None) -> dict:
        """
        Fetches regex patterns from file and compiles them

        Parameters:
            regex_file (str): Filepath to patterns
            type_fileter (str | None): Patterns to include

        Returns:
            dict: Name, regex patterns
        """

        patterns = {}

        with open_file(regex_file, "r") as file:
            raw_patterns = yaml.safe_load(file)

        for type, regex in raw_patterns.items():
            curr_regex = "".join(regex) if isinstance(regex, list) else regex
            try:
                if type_filter is None or type in type_filter:
                    patterns[type] = re.compile(curr_regex)
            except re.error as e:
                raise ValueError(f"Invalid regex pattern: {curr_regex} Error: {e}")
        return patterns

    @staticmethod
    def add_sub_mode_parser(parent_parser: ArgumentParser | _SubParsersAction):
        """
        Add mode specific subparser to parent parser

        Parameters:
            parent_parser (ArgumentParser): Parent parser, to add
                                            subparser to
        """
        find_parser = parent_parser.add_parser(  # type: ignore
            FindMode.command, help="Word filter mode"
        )
        run_mode_group = find_parser.add_argument_group("Matching Mode")
        mode_group = run_mode_group.add_mutually_exclusive_group(required=True)
        mode_group.add_argument(
            "-r", "--regex", help="Use regex mode to match.", action="store_true"
        )
        mode_group.add_argument(
            "-p", "--pegparse", help="Use pegparse mode to match.", action="store_true"
        )
        find_parser.add_argument(
            "-g",
            "--grammar-file",
            dest="match_grammar_file",
            help="Path to regex/pegparse grammar file",
        )
        ProgramMode._add_general_settings(find_parser)

    @staticmethod
    def _validate_args(args):
        if not file_exists(args.trie_file):
            raise FileNotFoundError(
                f"Grammar filepath: {args.trie_file} does not exist"
            )

    def _paint_filtered_content(
        self, contents: Sequence[Tuple[File | pymupdf.Document, Sequence[Content]]]
    ) -> list[tuple[pymupdf.Document, Sequence[Content]]]:
        """
        Draw rectangles around the word found by filtermode

        Parameters:
            contents (Sequence): List of tuples with files/documents
                                and a list with contents

        Returns:
            list: Tuples with documents and a list of contents
        """
        if self.mode == "regex":
            matches = RegexMatcherHandler(
                self.grammar, set(self.skip_list)
            ).handle_input(contents)
        else:
            matches = PegParseMatcherHandler(self.grammar, set(self.skip_list)).handle_input(contents)  # type: ignore
        painted_images = ImagePainterHandler(color=(255, 0, 255)).handle_input(matches)  # type: ignore

        content = [c for _, c in contents]
        return list(zip(painted_images, content))

    def run(self, inputs: Sequence[str]) -> None:
        """
        Run the programmode by creating a chain of handlers then handle
        the data

        Parameters:
            inputs (Sequence): List of filepaths of files to be handled
        """
        PluginManager.init_plugin_manager(self.enable_plugins)
        chain = Chain()

        chain.add_handler(FileHandler(self.image_extract, False))
        chain.add_handler(ContentHandler(True, self.num_threads, self.trie))
        chain.add_handler(
            ConversionHandler[
                Sequence[Tuple[File | pymupdf.Document, Sequence[Content]]],
                list[tuple[pymupdf.Document, Sequence[Content]]],
            ](converter=self._paint_filtered_content)
        )
        chain.add_handler(FilterMatcherHandler(self.trie, True, self.skip_list))

        chain.add_handler(ImagePainterHandler(color=(255, 105, 0)))
        chain.add_handler(
            OutputHandler(OutputMode.from_output_arg(self.output), OutputFormat.PDF)
        )

        chain.handle_input(inputs)
