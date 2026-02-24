import os
import pytest
import pymupdf

from parseidon.handlers.output_handler import (
    OutputFormat,
    OutputMode,
    OutputHandler,
)

from parseidon.handlers.match import Match


def test_output_format():
    arg = "-"
    mode = OutputMode.from_output_arg(arg)
    assert mode == OutputMode.STDOUT
    with pytest.raises(AttributeError):
        print(mode.path)

    arg = "somedir/andPath.csv"
    mode = OutputMode.from_output_arg(arg)
    assert mode == OutputMode.FILE
    assert mode.path == "somedir/andPath.csv"

    format_arg = "csv"
    format = OutputFormat.from_format_arg(format_arg)
    assert format == OutputFormat.CSV
    assert format.file_ending() == format_arg
    format_arg = "json"
    format = OutputFormat.from_format_arg(format_arg)
    assert format == OutputFormat.JSON
    assert format.file_ending() == format_arg
    with pytest.raises(ValueError):
        format_arg = "pdf"
        format = OutputFormat.from_format_arg(format_arg)  # So we cant set PDF from cli


@pytest.mark.parametrize(
    "output_format, expected_output",
    [
        (
            OutputFormat.CSV,
            "Object type|Object found|Filepath|Position|Context|Count\nTYPE|FOUND|PATH|POS|CONTEXT|12345\nTYPE2|FOUND2|PATH2|POS2|CONTEXT2|1\n",
        ),
        (
            OutputFormat.JSON,
            '[\n  {\n    "Object type": "TYPE",\n    "Object found": "FOUND",\n    "Filepath": "PATH",\n    "Position": "POS",\n    "Context": "CONTEXT",\n    "Count": 12345\n  },\n  {\n    "Object type": "TYPE2",\n    "Object found": "FOUND2",\n    "Filepath": "PATH2",\n    "Position": "POS2",\n    "Context": "CONTEXT2",\n    "Count": 1\n  }\n]',
        ),
    ],
)
def test_output_handler_file(capfd, output_format, expected_output):
    mode = OutputMode.FILE
    mode.path = "tmp.file"

    handler = OutputHandler(mode, output_format)
    matches = [
        Match("TYPE", "FOUND", "PATH", "POS", "CONTEXT"),
        Match("TYPE2", "FOUND2", "PATH2", "POS2", "CONTEXT2"),
    ]
    matches[0].count = 12345
    matches[1].count = 1
    handler.handle_input(matches)
    out, err = capfd.readouterr()
    print(f"out: {out}")

    assert out == ""
    assert err == ""

    with open("tmp.file", "r") as temp_file:
        content = temp_file.read()

    try:
        os.remove("tmp.file")
    except OSError:
        pass

    assert content == expected_output


@pytest.mark.parametrize(
    "output_format, expected_output",
    [
        (
            OutputFormat.CSV,
            "Object type|Object found|Filepath|Position|Context|Count\r\nTYPE|FOUND|PATH|POS|CONTEXT|12345\r\nTYPE2|FOUND2|PATH2|POS2|CONTEXT2|1\r\n",
        ),
        (
            OutputFormat.JSON,
            '[\n  {\n    "Object type": "TYPE",\n    "Object found": "FOUND",\n    "Filepath": "PATH",\n    "Position": "POS",\n    "Context": "CONTEXT",\n    "Count": 12345\n  },\n  {\n    "Object type": "TYPE2",\n    "Object found": "FOUND2",\n    "Filepath": "PATH2",\n    "Position": "POS2",\n    "Context": "CONTEXT2",\n    "Count": 1\n  }\n]',
        ),
    ],
)
def test_output_handler_stdout(capfd, output_format, expected_output):
    handler = OutputHandler(OutputMode.STDOUT, output_format)
    matches = [
        Match("TYPE", "FOUND", "PATH", "POS", "CONTEXT"),
        Match("TYPE2", "FOUND2", "PATH2", "POS2", "CONTEXT2"),
    ]
    matches[0].count = 12345
    matches[1].count = 1
    handler.handle_input(matches)
    out, err = capfd.readouterr()
    print(f"out: {out}")
    assert out == expected_output
    assert err == ""


def test_output_handler_pdf_stdout(capfd):
    handler = OutputHandler(OutputMode.STDOUT, OutputFormat.PDF)
    doc = pymupdf.Document()
    doc.new_page()  # type: ignore
    handler.handle_input([doc])
    out, err = capfd.readouterr()
    print(f"out: {out}")

    assert err == ""
    assert out.startswith("%PDF-")
    assert len(out) > 100  # Creation dates etc. differ
