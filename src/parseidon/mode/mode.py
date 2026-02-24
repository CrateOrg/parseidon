import os
from argparse import ArgumentParser
import argparse
from typing import Protocol
from abc import ABC, abstractmethod
from parseidon.helpers.resource_loader import open_file
from parseidon.handlers.output_handler import OutputFormat


class ModeConfig(Protocol):
    output: str
    num_threads: int
    image_extract: bool
    skip_list: str | None
    trie_file: str


class ProgramMode(ABC):

    command: str

    @classmethod
    def from_args(cls, args):
        ProgramMode._validate_args(args)
        cls._validate_args(args)
        config = cls._config_from_args(args)
        return cls(config)

    @classmethod
    @abstractmethod
    def _config_from_args(cls, args) -> ModeConfig: ...

    @abstractmethod
    def __init__(self, config: ModeConfig):
        self.output = config.output
        self.num_threads = config.num_threads
        self.image_extract = config.image_extract
        self.skip_list = self._get_skip_list(config.skip_list)
        self.trie = config.trie_file

    @staticmethod
    def _add_general_settings(mode_subparser: ArgumentParser):
        mode_subparser.add_argument("input_path", help="Path to input files", nargs="+")
        mode_subparser.add_argument(
            "-o", "--output", help="Path to output files", default="./"
        )
        mode_subparser.add_argument(
            "-n",
            "--num-threads",
            dest="num_threads",
            help="Number of threads spawned for content extraction",
            type=int,
            default=1,
        )
        mode_subparser.add_argument(
            "-i",
            "--image-extract",
            dest="image_extract",
            action=argparse.BooleanOptionalAction,
            help="Use flag to extract text from images. Can not be combined with --draw-boxes.",
            default=False,
        )
        mode_subparser.add_argument(
            "-l", "--skip_list", help="Path to file containing skip list"
        )
        mode_subparser.add_argument(
            "-t",
            "--trie-file",
            dest="trie_file",
            help="Path to trie structure file",
            default="trie/swedish.marisa",
        )

    @staticmethod
    def _add_output_group(parent_parser: ArgumentParser):
        output_group = parent_parser.add_argument_group("Output Format")
        output_group.add_argument(
            "-d",
            "--draw-boxes",
            dest="draw_boxes",
            action=argparse.BooleanOptionalAction,
            help="Use flag if you want visual output with colored squares around matches",
            default=False,
        )
        output_group.add_argument(
            "-f",
            "--output-format",
            type=OutputFormat.from_format_arg,
            choices=[
                OutputFormat.CSV,
                OutputFormat.JSON,
            ],  # PDF is only valid for draw boxes
            dest="output_format",
            help="Set output format",
        )

    @staticmethod
    @abstractmethod
    def add_sub_mode_parser(parent_parser): ...

    @staticmethod
    @abstractmethod
    def _validate_args(args):
        if args.output != "-":
            if args.output == os.path.basename(args.output):
                args.output = os.path.join("./", args.output)
            if not os.path.exists(os.path.dirname(args.output)):
                raise FileNotFoundError(f"Output path: {args.output} does not exist")

        for path in args.input_path:
            dir_path = os.path.dirname(path)
            if path.endswith("*"):
                if not os.path.exists(dir_path):
                    raise FileNotFoundError(
                        f"Input path: {args.input_path} does not exist"
                    )
            else:
                if not os.path.exists(path) or path.endswith("/"):
                    raise FileNotFoundError(
                        f"Input path: {args.input_path} does not exist"
                    )

        if hasattr(args, "draw_boxes") and args.draw_boxes:
            if hasattr(args, "output_format") and args.output_format:
                raise argparse.ArgumentError(
                    None, "Argument --draw-boxes is not allowed with --output-format!"
                )

        if args.num_threads < 1:
            raise argparse.ArgumentError(None, "Number of threads must be more than 0!")

    @staticmethod
    def _get_skip_list(skip_list: str | None) -> list[str]:
        """
        Fetches potential matches that should be skipped from
        skip_list file

        Parameters:
            skip_list (str): Filepath to skip list

        Returns:
            list: List of potential matches to be ignored
        """
        if skip_list is None:
            return []
        with open_file(skip_list, "r") as file:
            return file.read().splitlines()

    @abstractmethod
    def run(self, inputs): ...
