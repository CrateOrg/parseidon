import argparse
import logging
import os
import sys

from parseidon.factory.program_factory import program_factory
from parseidon.mode.filter_mode import FilterMode
from parseidon.mode.find_mode import FindMode
from parseidon.mode.mode import ProgramMode
from parseidon.mode.pegparse_mode import PegParseMode
from parseidon.mode.regex_mode import RegexMode

logger = logging.getLogger(__name__)


def get_inputs(input_paths):
    inputs = set()
    for path in input_paths:
        dir_path = os.path.dirname(path)
        if path.endswith("*") and os.path.exists(dir_path):
            for f in os.listdir(dir_path):
                inputs.add(os.path.join(dir_path, f))
            continue
        if not os.path.exists(path) or path.endswith("/"):
            input_paths.remove(path)
            if input_paths:
                logger.fatal(f"Input path: {path} does not exist")
            else:
                raise FileNotFoundError(f"Input path: {path} does not exist")
        else:
            inputs.add(path)
    return inputs


def parse_args(args, modes: list[type[ProgramMode]]):
    """
    Parses all arguments from the terminal.
    Ensures paths and filenames are valid.
    """
    parser = argparse.ArgumentParser()

    # Parser for choosing what type of parsing is done
    mode_parser = parser.add_subparsers(
        title="Parsing Type", dest="command", required=True, help="CMD help"
    )

    for mode in modes:
        mode.add_sub_mode_parser(mode_parser)

    return parser.parse_args(args)


program_modes: list[type[ProgramMode]] = [RegexMode, PegParseMode, FilterMode, FindMode]


def main():
    logging.basicConfig(stream=sys.stderr, level=logging.WARNING)
    args = parse_args(sys.argv[1:], program_modes)

    inputs = get_inputs(args.input_path)
    program = program_factory(args)
    program.run(inputs)  # type: ignore
