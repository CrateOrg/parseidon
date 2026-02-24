import os
import sys

import pytest
from parseidon.main import main
from tests.helpers import testfiles_path, val_path


@pytest.mark.parametrize("program_mode", ["regex", "pegparse"])
@pytest.mark.parametrize(
    "filename",
    [
        ("docx_test.docx"),
        ("doc_test.doc"),
        ("xlsx_test.xlsx"),
        ("xls_test.xls"),
        ("ods_test.ods"),
        ("pdf_test.pdf"),
        ("plaintext_test"),
        ("md_test.md"),
        ("test_all_pat.txt"),
        ("odt_test.odt"),
        ("header_footer_test.docx"),
        ("table_test.docx"),
        ("footnote_test.docx"),
        ("chart_test.docx"),
        ("inline_shape_test.docx"),
    ],
)
def test_output_csv(monkeypatch, capfd, program_mode, filename):
    input_path = os.path.join(testfiles_path, filename)
    csv_file_path = os.path.join(val_path, "csv_files")
    expected_file_path = os.path.join(csv_file_path, f"{filename}.csv")

    # Test save output to file
    temp_file = "tmp.csv"
    try:
        os.remove(temp_file)
    except OSError:
        pass

    with monkeypatch.context() as mp:
        mp.setattr(
            sys, "argv", [sys.argv[0], program_mode, "-o", temp_file, "-i", input_path]
        )
        main()

    with open(expected_file_path, "r") as f:
        with open(temp_file, "r") as tmp:
            expected_output = f.read().splitlines()
            output = tmp.read().splitlines()
            assert sorted(output) == sorted(expected_output)

    try:
        os.remove(temp_file)
    except OSError:
        pass

    # Test print output to stdout

    with monkeypatch.context() as mp:
        mp.setattr(
            sys, "argv", [sys.argv[0], program_mode, "-o", "-", "-i", input_path]
        )
        main()

    out, err = capfd.readouterr()
    print(f"out: {out}")
    assert sorted(out.splitlines()) == sorted(expected_output)
    assert err == ""
