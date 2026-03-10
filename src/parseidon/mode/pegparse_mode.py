import argparse
from argparse import ArgumentParser, _SubParsersAction
from dataclasses import dataclass
from typing import Sequence

from parsimonious import Grammar

from parseidon.handlers.chain import Chain
from parseidon.handlers.content_handler import ContentHandler
from parseidon.handlers.conversion_handler import MatcherHandlerToOutputHandlerConverter
from parseidon.handlers.file_handler import FileHandler
from parseidon.handlers.image_painter_handler import ImagePainterHandler
from parseidon.handlers.matcher_handlers.peg_parse_matcher_handler import (
    PegParseMatcherHandler,
)
from parseidon.handlers.output_handler import OutputFormat, OutputHandler, OutputMode
from parseidon.helpers.resource_loader import file_exists, open_file
from parseidon.mode.mode import ModeConfig, ProgramMode
from parseidon.plugin_manager import PluginManager


@dataclass
class PegParseModeConfig(ModeConfig):
    output: str
    num_threads: int
    output_format: OutputFormat
    image_extract: bool
    column_context: bool
    draw_boxes: bool
    grammar_file: str
    skip_list: str | None
    trie_file: str
    enable_plugins: bool


class PegParseMode(ProgramMode):
    """
    Class representing the PegParseMode

    Attributes:
        config (PegParseModeConfig): Configuration from user
    """

    command = "pegparse"

    @classmethod
    def _config_from_args(cls, args) -> ModeConfig:
        args.output_format = (
            OutputFormat.CSV if args.output_format is None else args.output_format
        )
        return PegParseModeConfig(
            args.output,
            args.num_threads,
            OutputFormat.PDF if args.draw_boxes else args.output_format,
            args.image_extract,
            args.column_context,
            args.draw_boxes,
            args.grammar_file,
            args.skip_list,
            args.trie_file,
            args.enable_plugins,
        )

    def __init__(self, config: PegParseModeConfig) -> None:
        """
        Initializes PegParseMode objects

        Parameters:
            config (PegParseModeConfig): Configuration from user
        """
        super().__init__(config)
        self.column_context = config.column_context
        self.draw_boxes = config.draw_boxes
        self.grammar = self._read_grammar(config.grammar_file)
        self.output_format = config.output_format

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

    @staticmethod
    def add_sub_mode_parser(parent_parser: ArgumentParser | _SubParsersAction) -> None:
        """
        Add mode specific subparser to parent parser

        Parameters:
            parent_parser (ArgumentParser): Parent parser, to add
                                            subparser to
        """
        peg_parser = parent_parser.add_parser(  # type: ignore
            PegParseMode.command, help="PEG parsing mode."
        )
        peg_parser.add_argument(
            "-c",
            "--column-context",
            dest="column_context",
            action=argparse.BooleanOptionalAction,
            help="Use flag if spreadsheets also gets context from rows",
            default=False,
        )
        peg_parser.add_argument(
            "-g",
            "--peg-file",
            dest="grammar_file",
            help="Path to PEG grammar file",
            default="peg_files/peg_grammars.txt",
        )
        ProgramMode._add_output_group(peg_parser)
        ProgramMode._add_general_settings(peg_parser)

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
        PluginManager.init_plugin_manager(self.enable_plugins)
        chain = Chain()

        chain.add_handler(FileHandler(self.image_extract, self.column_context))
        chain.add_handler(ContentHandler(self.draw_boxes, self.num_threads, self.trie))
        chain.add_handler(PegParseMatcherHandler(self.grammar, set(self.skip_list)))

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
