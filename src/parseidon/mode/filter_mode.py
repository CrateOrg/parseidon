import argparse
from argparse import ArgumentParser, _SubParsersAction
from dataclasses import dataclass
from typing import Sequence

from parseidon.handlers.chain import Chain
from parseidon.handlers.content_handler import ContentHandler
from parseidon.handlers.conversion_handler import MatcherHandlerToOutputHandlerConverter
from parseidon.handlers.file_handler import FileHandler
from parseidon.handlers.image_painter_handler import ImagePainterHandler
from parseidon.handlers.matcher_handlers.filter_matcher_handler import (
    FilterMatcherHandler,
)
from parseidon.handlers.output_handler import OutputFormat, OutputHandler, OutputMode
from parseidon.helpers.resource_loader import file_exists
from parseidon.mode.mode import ModeConfig, ProgramMode


@dataclass
class FilterModeConfig(ModeConfig):
    output: str
    num_threads: int
    output_format: OutputFormat
    image_extract: bool
    column_context: bool
    draw_boxes: bool
    trie_file: str
    ignore_punctuation: bool
    skip_list: str | None


class FilterMode(ProgramMode):
    """
    Class representing the FilterMode

    Attributes:
        config (FilterModeConfig): Configuration from user
    """

    command = "filter"

    @classmethod
    def _config_from_args(cls, args) -> ModeConfig:
        args.output_format = (
            OutputFormat.CSV if args.output_format is None else args.output_format
        )
        return FilterModeConfig(
            args.output,
            args.num_threads,
            OutputFormat.PDF if args.draw_boxes else args.output_format,
            args.image_extract,
            args.column_context,
            args.draw_boxes,
            args.trie_file,
            args.ignore_punctuation,
            args.skip_list,
        )

    def __init__(self, config: FilterModeConfig) -> None:
        """
        Initializes FilterMode objects

        Parameters:
            config (FilterModeConfig): Configuration from user
        """
        super().__init__(config)
        self.column_context = config.column_context
        self.draw_boxes = config.draw_boxes
        self.ignore_punctuation = config.ignore_punctuation
        self.output_format = config.output_format

    @staticmethod
    def add_sub_mode_parser(parent_parser: ArgumentParser | _SubParsersAction) -> None:
        """
        Add mode specific subparser to parent parser

        Parameters:
            parent_parser (ArgumentParser): Parent parser, to add
                                            subparser to
        """
        filter_parser = parent_parser.add_parser(  # type: ignore
            FilterMode.command, help="Word filter mode"
        )
        filter_parser.add_argument(
            "-c",
            "--column-context",
            dest="column_context",
            action=argparse.BooleanOptionalAction,
            help="Use flag if spreadsheets also gets context from rows",
            default=False,
        )

        filter_parser.add_argument(
            "-p",
            "--ignore-punctuation",
            dest="ignore_punctuation",
            help="Ignores common punctuations",
            action=argparse.BooleanOptionalAction,
            default=True,
        )

        ProgramMode._add_output_group(filter_parser)
        ProgramMode._add_general_settings(filter_parser)

    @staticmethod
    def _validate_args(args):
        if not file_exists(args.trie_file):
            raise FileNotFoundError(f"Trie filepath: {args.trie_file} does not exist")

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
        chain.add_handler(
            FilterMatcherHandler(self.trie, self.ignore_punctuation, self.skip_list)
        )

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
