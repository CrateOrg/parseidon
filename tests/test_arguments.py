from types import SimpleNamespace
import pytest
import os
from parseidon.handlers.output_handler import OutputFormat
from parseidon.main import parse_args, program_modes
from parseidon.mode.find_mode import FindMode
from parseidon.mode.pegparse_mode import PegParseMode
from parseidon.mode.regex_mode import RegexMode
from parseidon.mode.filter_mode import FilterMode
from parseidon.factory.program_factory import program_factory
from tests.helpers import (
    regex_file,
    peg_file,
    trie_file,
    testfiles_path,
    val_path,
    skip_list_file,
)
from parsimonious.exceptions import ParseError

test_path = os.path.join(testfiles_path, "*")


@pytest.mark.parametrize(
    "program, valid_grammar", [(RegexMode, regex_file), (PegParseMode, peg_file)]
)
@pytest.mark.parametrize(
    "in_path, out_path, skip",
    [
        ("./test_files/invalid_in_folder/", val_path, skip_list_file),
        (test_path, "./test_files/invalid_out_folder/", skip_list_file),
        (test_path, val_path, "./not_existing_skip_list.txt"),
    ],
)
def test_invalid_path(program, valid_grammar, in_path, out_path, skip):
    args = SimpleNamespace()
    args.input_path = [in_path]
    args.output = out_path
    args.num_threads = 1
    args.output_format = "csv"
    args.skip_list = skip
    args.grammar_file = valid_grammar
    args.image_extract = False
    args.column_context = False
    args.draw_boxes = False
    args.trie_file = trie_file

    # Test invalid args with valid grammar
    with pytest.raises(FileNotFoundError):
        program.from_args(args)


@pytest.mark.parametrize(
    "program, invalid_grammar",
    [
        ("regex", "./not_existing_regex.yaml"),
        ("pegparse", "./not_existing_peg.txt"),
    ],
)
def test_invalid_grammar(program, invalid_grammar):
    # Tests valid args with invalid grammar
    args = SimpleNamespace()
    args.input_path = [test_path]
    args.output = "-"
    args.num_threads = 1
    args.output_format = "csv"
    args.skip_list = None
    args.grammar_file = invalid_grammar
    args.image_extract = False
    args.column_context = False
    args.draw_boxes = False
    args.command = program
    args.trie_file = trie_file
    with pytest.raises(FileNotFoundError):
        program_factory(args)


@pytest.mark.parametrize(
    "in_path, out_path",
    [
        ("./test_files/invalid_in_folder/", val_path),
        (test_path, "./test_files/invalid_out_folder/"),
    ],
)
def test_filter_mode_args(in_path, out_path):
    args = SimpleNamespace()
    args.input_path = [in_path]
    args.output = out_path
    args.num_threads = 1
    args.output_format = "csv"
    args.trie_file = trie_file
    args.image_extract = False
    args.column_context = False
    args.command = "filter"

    # Test invalid args with valid grammar
    with pytest.raises(FileNotFoundError):
        program_factory(args)


def test_filter_mode_valid_args():
    args = SimpleNamespace()
    args.input_path = [test_path]
    args.output = "-"
    args.num_threads = 2
    args.trie_file = trie_file
    args.image_extract = False
    args.column_context = False
    args.ignore_punctuation = False
    args.draw_boxes = True
    args.output_format = None
    args.skip_list = None

    mode = FilterMode.from_args(args)
    assert mode.output == args.output
    assert mode.trie != None
    assert mode.image_extract == args.image_extract
    assert mode.column_context == args.column_context
    assert mode.ignore_punctuation == args.ignore_punctuation
    assert mode.draw_boxes == args.draw_boxes
    assert mode.num_threads == 2
    assert mode.output_format == OutputFormat.PDF


@pytest.mark.parametrize(
    "program, grammar_file", [("regex", "bad_re.yaml"), ("pegparse", "bad_peg.txt")]
)
def test_bad_grammar(program, grammar_file):
    grammar_filepath = os.path.join(testfiles_path, grammar_file)
    args = SimpleNamespace()
    args.input_path = [test_path]
    args.output = "-"
    args.num_threads = 1
    args.output_format = "csv"
    args.skip_list = None
    args.grammar_file = grammar_filepath
    args.image_extract = False
    args.column_context = False
    args.draw_boxes = False
    args.command = program
    args.trie_file = trie_file
    with pytest.raises((ValueError, ParseError)):
        program_factory(args)


def test_invalid_command():
    with pytest.raises(SystemExit):
        parse_args(["invalid_command"], program_modes)


def test_argparse_no_command_fails():
    with pytest.raises(SystemExit):
        parse_args([], program_modes)


def test_find_mode_args():
    args = SimpleNamespace()
    args.input_path = [test_path]
    args.output = "-"
    args.num_threads = 2
    args.image_extract = True
    args.regex = True
    args.trie_file = trie_file
    args.skip_list = None
    args.match_grammar_file = None
    args.command = "find"

    mode = program_factory(args)
    assert type(mode) == FindMode
    assert mode.output == args.output
    assert mode.trie != None
    assert mode.num_threads == 2
    assert mode.mode == "regex"
    assert mode.grammar != None
