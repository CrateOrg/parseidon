import argparse
import re
from argparse import ArgumentParser, _SubParsersAction
from dataclasses import dataclass
from typing import Sequence

import yaml

from parseidon.handlers.chain import Chain
from parseidon.handlers.content_handler import ContentHandler
from parseidon.handlers.conversion_handler import MatcherHandlerToOutputHandlerConverter
from parseidon.handlers.file_handler import FileHandler
from parseidon.handlers.image_painter_handler import ImagePainterHandler
from parseidon.handlers.matcher_handlers.regex_matcher_handler import (
    RegexMatcherHandler,
)
from parseidon.handlers.output_handler import OutputFormat, OutputHandler, OutputMode
from parseidon.helpers.resource_loader import file_exists, open_file
from parseidon.mode.mode import ModeConfig, ProgramMode


@dataclass
class RegexModeConfig(ModeConfig):
    output: str
    num_threads: int
    output_format: OutputFormat
    image_extract: bool
    column_context: bool
    draw_boxes: bool
    grammar_file: str
    skip_list: str | None
    type_filter: list | None
    trie_file: str


class RegexMode(ProgramMode):
    """
    Class representing the FilterMode

    Attributes:
        config (FilterModeConfig): Configuration from user
    """

    command = "regex"

    @classmethod
    def _config_from_args(cls, args) -> ModeConfig:
        args.output_format = (
            OutputFormat.CSV if args.output_format is None else args.output_format
        )
        return RegexModeConfig(
            args.output,
            args.num_threads,
            OutputFormat.PDF if args.draw_boxes else args.output_format,
            args.image_extract,
            args.column_context,
            args.draw_boxes,
            args.grammar_file,
            args.skip_list,
            None,
            args.trie_file,
        )

    def __init__(self, config: RegexModeConfig) -> None:
        """
        Initializes FilterMode objects

        Parameters:
            config (FilterModeConfig): Configuration from user
        """
        super().__init__(config)
        self.column_context = config.column_context
        self.draw_boxes = config.draw_boxes
        self.patterns = self._compile_patterns(config.grammar_file, config.type_filter)
        self.output_format = config.output_format

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
        reg_parser = parent_parser.add_parser(  # type: ignore
            RegexMode.command, help="RegEx parsing mode."
        )
        reg_parser.add_argument(
            "-c",
            "--column-context",
            dest="column_context",
            action=argparse.BooleanOptionalAction,
            help="Use flag if spreadsheets also gets context from rows",
            default=False,
        )
        reg_parser.add_argument(
            "-g",
            "--regex-file",
            dest="grammar_file",
            help="Path to regex file",
            default="regex_files/main_regex.yaml",
        )
        ProgramMode._add_output_group(reg_parser)
        ProgramMode._add_general_settings(reg_parser)

    @staticmethod
    def _validate_args(args):
        if not file_exists(args.grammar_file):
            raise FileNotFoundError(
                f"Grammar filepath: {args.grammar_file} does not exist"
            )
        if args.skip_list is not None and not file_exists(args.skip_list):
            raise FileNotFoundError(
                f"Skip list filepath: {args.skip_list} does not exist"
            )

    def run(self, inputs: Sequence) -> None:
        """
        Run the programmode by creating a chain of handlers then handle
        the data

        Parameters:
            inputs (Sequence): List of filepaths of files to be handled
        """
        chain = Chain()

        chain.add_handler(FileHandler(self.image_extract, self.column_context))
        chain.add_handler(ContentHandler(self.draw_boxes, self.num_threads, self.trie))
        chain.add_handler(RegexMatcherHandler(self.patterns, set(self.skip_list)))

        if self.draw_boxes:
            chain.add_handler(ImagePainterHandler())
        else:
            chain.add_handler(MatcherHandlerToOutputHandlerConverter())

        chain.add_handler(
            OutputHandler(
                OutputMode.from_output_arg(self.output),
                self.output_format,
            )
        )

        chain.handle_input(inputs)
