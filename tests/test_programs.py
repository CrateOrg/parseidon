import argparse
import pytest
from parseidon.mode.filter_mode import FilterMode
from parseidon.mode.pegparse_mode import PegParseMode
from parseidon.mode.regex_mode import RegexMode
from tests.helpers import *


def parsers():
    parser = argparse.ArgumentParser()
    sub_parser = parser.add_subparsers(
        title="Parsing Type", dest="command", required=True, help="CMD help"
    )
    return parser, sub_parser


@pytest.mark.parametrize("program_mode", [RegexMode, PegParseMode, FilterMode])
def test_test(program_mode):
    parser, sub_parser = parsers()
    program_mode.add_sub_mode_parser(sub_parser)
    args = parser.parse_args([program_mode.command, "some_input_path"])
    assert args.input_path == ["some_input_path"]


@pytest.mark.parametrize("program_mode", [RegexMode, PegParseMode, FilterMode])
def test_general_arguments(program_mode):
    parser, sub_parser = parsers()
    program_mode.add_sub_mode_parser(sub_parser)

    args = parser.parse_args([program_mode.command, "some_input_path"])
    assert args.input_path == ["some_input_path"]
    assert args.output == "./"
    assert args.image_extract == False
    assert args.column_context == False

    args = parser.parse_args([program_mode.command, "-o", "-", "some_input_path"])
    assert args.input_path == ["some_input_path"]
    assert args.output == "-"
    assert args.image_extract == False
    assert args.column_context == False

    args = parser.parse_args([program_mode.command, "-i", "-c", "some_input_path"])
    assert args.input_path == ["some_input_path"]
    assert args.image_extract == True
    assert args.column_context == True


def test_regex_arguments():
    parser, sub_parser = parsers()
    RegexMode.add_sub_mode_parser(sub_parser)
    args = parser.parse_args([RegexMode.command, "some_input_path"])
    assert args.grammar_file == "regex_files/main_regex.yaml"
    assert args.skip_list == None

    args = parser.parse_args(
        [RegexMode.command, "-g", "REG", "-l", "SKIP", "some_input_path"]
    )
    assert args.grammar_file == "REG"
    assert args.skip_list == "SKIP"


def test_pegparse_arguments():
    parser, sub_parser = parsers()
    PegParseMode.add_sub_mode_parser(sub_parser)
    args = parser.parse_args([PegParseMode.command, "some_input_path"])
    assert args.grammar_file == "peg_files/peg_grammars.txt"
    assert args.skip_list == None

    args = parser.parse_args(
        [PegParseMode.command, "-g", "PEG", "-l", "SKIP", "some_input_path"]
    )
    assert args.grammar_file == "PEG"
    assert args.skip_list == "SKIP"


def test_filter_arguments():
    parser, sub_parser = parsers()
    FilterMode.add_sub_mode_parser(sub_parser)
    args = parser.parse_args([FilterMode.command, "some_input_path"])
    assert args.trie_file == "trie/swedish.marisa"
    assert args.ignore_punctuation == True
    assert args.draw_boxes == False

    args = parser.parse_args(
        [
            FilterMode.command,
            "-t",
            "TRIE",
            "--no-ignore-punctuation",
            "-d",
            "some_input_path",
        ]
    )
    assert args.trie_file == "TRIE"
    assert args.ignore_punctuation == False
    assert args.draw_boxes == True

    args = parser.parse_args(
        [FilterMode.command, "-t", "TRIE", "-p", "-d", "some_input_path"]
    )
    assert args.trie_file == "TRIE"
    assert args.ignore_punctuation == True
    assert args.draw_boxes == True
