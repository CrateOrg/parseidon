import re
from parsimonious import Grammar
import pymupdf
import pytest

from parseidon.handlers.content_handler import ContentHandler
from parseidon.handlers.file_handler import FileHandler
from parseidon.handlers.matcher_handlers.peg_parse_matcher_handler import (
    PegParseMatcherHandler,
)
from parseidon.handlers.matcher_handlers.regex_matcher_handler import (
    RegexMatcherHandler,
)
from tests.helpers import (
    DummyFile,
    filter_matcher,
    peg_matcher,
    regex_matcher,
    use_hyphen_plugin,
    remove_ip_headings,
)


def dummy_file_and_matches():
    return (
        DummyFile(
            "TestFileName.txt",
            ".txt",
            "testpath/TestFileName.txt",
            "TESTSTARTWORD Jag är ett test \tTESTMID med lite text TESTEND\n\nTESTNEWLINESTART lite grann i mitten TESTNEWLINEEND",
        ),
        [
            "TESTSTARTWORD",
            "TESTMID",
            "TESTEND",
            "TESTNEWLINESTART",
            "TESTNEWLINEEND",
            "TESTSTARTWORD",
            "TESTMID",
            "TESTEND",
            "TESTNEWLINESTART",
            "TESTNEWLINEEND",
        ],
    )


def pos_regex_matcher():
    patterns = r"TESTSTARTWORD|TESTMID|TESTEND|TESTNEWLINESTART|TESTNEWLINEEND"
    regex = re.compile(patterns)
    return RegexMatcherHandler({"test": regex}, set())


def pos_peg_matcher():
    grammar = r"""
    mult = (email / any)+ 
    email = 'TESTSTARTWORD' / 'TESTMID' / 'TESTEND' / 'TESTNEWLINESTART' / 'TESTNEWLINEEND'
    any = ~r"(.|\s)+?(?=((?<=[\s\"\”(])|^).)" / ~r"(.|\s)+"
    """
    return PegParseMatcherHandler(Grammar(grammar), set())


@pytest.mark.parametrize(
    "matcher_handler", [filter_matcher(), pos_regex_matcher(), pos_peg_matcher()]
)
@pytest.mark.parametrize("file, expected_matches", [dummy_file_and_matches()])
def test_matcher_handler_position(matcher_handler, file, expected_matches):
    content = file.content_with_context()
    matches = [
        match
        for _, matches in matcher_handler.handle_input([(None, content)])
        for match in matches
    ]
    assert len(matches) == len(
        expected_matches
    )  # Duplicated matches on two "pages". Tests bug where only one context is read...

    for i in range(len(expected_matches)):
        assert matches[i].found_object == expected_matches[i]
        assert (
            matches[i].context == expected_matches[i]
        )  # Test that start and end pos are correct


@pytest.mark.parametrize(
    "matcher_handler", [filter_matcher(), pos_regex_matcher(), pos_peg_matcher()]
)
def test_matcher_count(matcher_handler):
    file = DummyFile(
        "TestFileName.txt",
        ".txt",
        "testpath/TestFileName.txt",
        "TESTSTARTWORD Jag är ett test \tTESTSTARTWORD TESTEND med lite text TESTSTARTWORD\n\nTESTNEWLINESTART lite grann i mitten TESTNEWLINESTART",
    )
    content = file.content_with_context()
    matches = [
        match
        for _, matches in matcher_handler.handle_input([(None, content)])
        for match in matches
    ]
    for m in matches:
        match m.found_object:
            case "TESTSTARTWORD":
                assert m.count == 6  # 3 occurrances * 2 content
            case "TESTNEWLINESTART":
                assert m.count == 4  # 2 occurrances * 2 content
            case "TESTEND":
                assert m.count == 2  # 1 occurrances * 2 content
            case _:
                print(f"{m.found_object} not handled")
                assert False


@pytest.mark.parametrize(
    "matcher_handler",
    [
        filter_matcher(),
        regex_matcher(),
        peg_matcher(),
    ],
)
def test_image_pos_context(matcher_handler):
    files = FileHandler(True, False).handle_input(["tests/test_files/hyphenation.pdf"])
    handler = ContentHandler(True, 1)
    contents = use_hyphen_plugin(handler.handle_input(files))
    matches = matcher_handler.handle_input(contents)
    file_matches = matches[0][1]
    print(matches)
    assert (
        len(matches) == 1
        and len(file_matches) == 6
        and all([match.found_object == "192.168.200.200" for match in file_matches])
    )


@pytest.mark.parametrize(
    "matcher_handler",
    [
        filter_matcher(),
        regex_matcher(),
        peg_matcher(),
    ],
)
def test_ip_headings(matcher_handler):
    files = FileHandler(True, False).handle_input(["tests/test_files/ip_headings.pdf"])
    handler = ContentHandler(True, 1)
    contents = remove_ip_headings(handler.handle_input(files))
    matches = matcher_handler.handle_input(contents)
    file_matches = matches[0][1]
    found_objects = [m.found_object for m in file_matches]
    print(matches)
    assert (
        len(matches) == 1
        and len(file_matches) == 4
        and found_objects == ["0.0.0.0", "3.3.3.3", "2.2.2.2", "1.1.1.1"]
    )


@pytest.mark.parametrize(
    "matcher_handler",
    [
        filter_matcher(),
        regex_matcher(),
        peg_matcher(),
    ],
)
def test_ip_heading_positions(matcher_handler):
    files = FileHandler(True, False).handle_input(
        ["tests/test_files/test_heading_positions.odt"]
    )
    handler = ContentHandler(True, 1)
    contents = remove_ip_headings(handler.handle_input(files))
    matches = matcher_handler.handle_input(contents)
    file_matches = matches[0][1]
    found_objects = [m.found_object for m in file_matches]
    positions = [m.position[1] for m in file_matches]
    words = contents[0][1][0].context.words
    true_pos = [w[1] for w in words if w[0].strip() == "0.0.0.0"]
    print(f"matches: {matches}")
    print(f"positions: {positions}")
    assert (
        len(matches) == 1
        and len(file_matches) == 1
        and found_objects == ["0.0.0.0"]
        and positions == true_pos
    )
