import csv
import os
import pytest

from parseidon.handlers.content import Content
from parseidon.handlers.file_handler import FileHandler
from tests.helpers import (
    DummyFile,
    filter_matcher,
    peg_matcher,
    regex_matcher,
    skip_list,
    testfiles_path,
    pegs_ind_path,
    val_path,
)


def assert_matches_equals_expected(matcher, input, expected):
    file = DummyFile("", "", "", "")
    res = matcher.handle_input([(file, [Content("", input, file)])])
    print(f"Input: {input} Expected: {expected}")
    assert len(res) == 1
    if expected != None:
        assert len(res[0][1]) == 1  # One match only
        assert res[0][1][0].found_object == expected
    else:
        assert len(res[0][1]) == 0  # No matches


@pytest.fixture
def read_patterns(request):
    filename, pattern = request.param
    testpatterns = []
    patterns_path = os.path.join(testfiles_path, "patterns")
    source_file = os.path.join(patterns_path, filename)
    with open(source_file, "r", newline="") as csv_file:
        reader = csv.reader(csv_file, delimiter=",", quotechar="|")
        for row in reader:
            input = row[0]
            expected = row[1] if row[1].strip() != "" else None
            testpatterns.append((input, expected))

    return testpatterns, pattern


@pytest.mark.parametrize(
    "read_patterns",
    [
        ("units.csv", "Unit"),
        ("ipv4.csv", "IPv4"),
        ("ipv6.csv", "IPv6"),
        ("mac.csv", "MAC"),
        ("doc_id.csv", "Doc_ID"),
        ("dates.csv", "Date"),
        ("url.csv", "URL"),
        ("phone.csv", "Phonenumber"),
        ("prot_tech.csv", "Tech/Protocol"),
        ("email.csv", "Email"),
        ("wifi.csv", "WiFi"),
    ],
    indirect=True,
)
def test_regex_patterns(read_patterns):
    """
    --- Testing different regex patterns
    """

    tests, pattern = read_patterns
    matcher = regex_matcher(pattern)

    for input, expected in tests:
        assert_matches_equals_expected(matcher, input, expected)


@pytest.mark.parametrize(
    "read_patterns",
    [
        ("dates.csv", "date_peg.txt"),
        ("doc_id.csv", "doc_id_peg.txt"),
        ("email.csv", "email_peg.txt"),
        ("ipv4.csv", "ipv4_peg.txt"),
        ("ipv6.csv", "ipv6_peg.txt"),
        ("mac.csv", "mac_peg.txt"),
        ("phone.csv", "phonenumber_peg.txt"),
        ("prot_tech.csv", "tech_protocol_peg.txt"),
        ("units.csv", "unit_peg.txt"),
        ("url.csv", "url_peg.txt"),
        ("wifi.csv", "wifi_peg.txt"),
    ],
    indirect=True,
)
def test_pegparse_patterns(read_patterns):
    """
    --- Testing different regex patterns
    """

    tests, peg_file = read_patterns
    peg_path = os.path.join(pegs_ind_path, peg_file)
    matcher = peg_matcher(peg_path)
    print(tests)
    for input, expected in tests:
        assert_matches_equals_expected(matcher, input, expected)


@pytest.mark.parametrize(
    "filename, expected_file, kwargs",
    [
        ("filter_text.txt", "filter_exp.txt", {}),
        ("slashed.txt", "slashed_exp.txt", {}),
    ],
)
def test_filter(filename, expected_file, kwargs):
    matcher = filter_matcher(**kwargs)
    with open(os.path.join(val_path, expected_file), "r") as f:
        expected_output = f.read().splitlines()

    file_path = os.path.join(testfiles_path, filename)
    file = FileHandler._file_from_filepath(file_path)
    output = matcher.handle_input([(file, file.content_with_context())])
    matches = [match for _, matches in output for match in matches]
    sorted_expected = sorted(expected_output)
    sorted_found = sorted([match.found_object for match in matches])
    print(f"Expected: '{sorted_expected}'")
    print(f"Found: '{sorted_found}'")
    assert sorted_found == sorted_expected


@pytest.mark.parametrize(
    "matcher", [regex_matcher(None, skip_list()), peg_matcher(skip_list=skip_list())]
)
@pytest.mark.parametrize(
    "read_patterns",
    [
        ("ipv4_skips.csv", "NA"),
    ],
    indirect=True,
)
def test_skip_list(matcher, read_patterns):
    """
    --- Tests removing matches with skiplist
    """
    tests, _ = read_patterns
    for input, expected in tests:
        assert_matches_equals_expected(matcher, input, expected)


@pytest.mark.parametrize("matcher", [regex_matcher(None), peg_matcher()])
@pytest.mark.parametrize(
    "read_patterns",
    [
        ("ipv4_skips.csv", "NA"),
    ],
    indirect=True,
)
def test_skip_list_fails(matcher, read_patterns):
    """
    --- Tests removing matches with skiplist
    """
    tests, _ = read_patterns
    for input, expected in tests:
        with pytest.raises(AssertionError):
            assert_matches_equals_expected(matcher, input, expected)
