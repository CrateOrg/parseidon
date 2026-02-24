import os

import pytest

from parseidon.files.excelfile import ExcelFile
from parseidon.files.image_file import ImageFile
from parseidon.files.legacy_excelfile import LegacyExcelFile
from parseidon.files.legacy_wordfile import LegacyWordFile
from parseidon.files.pdf_file import PdfFile
from parseidon.files.textfile import TextFile
from parseidon.files.wordfile import WordFile
from parseidon.handlers.content import ExcelContext
from parseidon.handlers.file_handler import FileHandler
from parseidon.handlers.content_handler import ContentHandler
from tests.helpers import use_hyphen_plugin


def text_test_data():
    return [
        ("bad_peg.txt", TextFile, [(None, '  digit = ~"[0-9]')]),
        ("bad_peg.md", TextFile, [(None, '# Title\nsomething\n  digit = ~"[0-9]')]),
    ]


def word_test_data():
    return [
        (
            "docx_tes.docx",
            WordFile,
            [
                ("Paragraph: 1", "123.21.0.22"),
                ("Paragraph: 2", "Hej 164.0.2.2"),
                ("Paragraph: 3", "mailuser@usermail"),
                ("Section: 1, first page footer", "FooterText"),
                ("Section: 1, first page header", "HEADER FOI-X--9999--SE"),
                (
                    "Table: 1",
                    "IP\n"
                    "Mail\n"
                    "ID\n"
                    "Mac\n"
                    "URL\n"
                    "162.2.18.0\n"
                    "user@gmail.com\n"
                    "FOI Memo 1234\n"
                    "01:21:45:67:89:AB\n"
                    "https://dummyurl.se/in/a/table",
                ),
            ],
        ),
        ("read_doc_test.doc", LegacyWordFile, word_file_data()),
        ("odt_tes.odt", LegacyWordFile, word_file_data()),
        (
            "test_image.doc",
            LegacyWordFile,
            [
                ("Image: 1", "0.0.0.0\nhttp://localhost\n2 kbit/s"),
                ("Image: 2", "123.123.123.123\nWi-Fi\n500 kg"),
            ],
        ),
        (
            "test_image.docx",
            WordFile,
            [
                ("Image: 1", "0.0.0.0\nhttp://localhost\n2 kbit/s"),
                ("Image: 2", "123.123.123.123\nWi-Fi\n500 kg"),
            ],
        ),
        (
            "header_footer_test.docx",
            WordFile,
            [
                ("Section: 1, first page footer", "first_footer@section1.se"),
                ("Section: 1, default footer", "http://oddfooter.se/section1"),
                ("Section: 1, even page footer", "www.evenfooter.section1.com"),
                ("Section: 2, first page footer", "first_footer@section2.se"),
                ("Section: 3, default footer", "https://oddfooter.nu/section2"),
                ("Section: 3, even page footer", "https://evenfooter.nu/section2"),
                ("Section: 1, first page header", "first_header@section1.se"),
                ("Section: 1, default header", "http://oddheader.se/section1"),
                ("Section: 1, even page header", "www.evenheader.section1.com"),
                ("Section: 2, first page header", "first_header@section2.se"),
                ("Section: 3, default header", "https://oddheader.nu/section2"),
                ("Section: 3, even page header", "https://evenheader.nu/section2"),
            ],
        ),
        (
            "footnote_test.docx",
            WordFile,
            [
                ("Footnote: 1", "footnote_1@gmail.com"),
                ("Footnote: 2", "Footnot_2..notvalid@gmail.com"),
                ("Footnote: 3", "https://footnote3.se"),
            ],
        ),
        (
            "chart_test.docx",
            WordFile,
            [
                (
                    "Figure: 1",
                    "CAT5 dreaminess per protocol in a word chart S1 Wifi Ethernet 802.11Q Bluetooth 4.3 2.5 3.5 4.5 S2 2.4 4.4 1.8 2.8 S3 2 3 5",
                )
            ],
        ),
        (
            "inline_shape_test.docx",
            WordFile,
            [
                (
                    "Inline shape: 1",
                    "Detta är en SHAPE, bara inritad utan någon slags yttre drawing. Den skulle kunna ha IP-adress 18.88.88.192 och ha en inkommande CAT6-kabel.",
                )
            ],
        ),
    ]


def word_file_data():
    return [
        ("Paragraph: 1", "123.21.0.22"),
        ("Paragraph: 2", "Hej 164.0.2.2"),
        ("Paragraph: 3", "mailuser@usermail"),
        ("Section: 1, default footer", "FooterText"),
        ("Section: 1, default header", "HEADER FOI-X--9999--SE"),
        (
            "Table: 1",
            "IP\n"
            "Mail\n"
            "ID\n"
            "Mac\n"
            "URL\n"
            "162.2.18.0\n"
            "user@gmail.com\n"
            "FOI Memo 1234\n"
            "01:21:45:67:89:AB\n"
            "https://dummyurl.se/in/a/table",
        ),
    ]


def excel_test_data():
    return [
        (
            "test_image.xls",
            LegacyExcelFile,
            [
                (
                    ExcelContext(10, 3, "Image in Sheet: 1"),
                    "0.0.0.0\nhttp://localhost\n2 kbit/s",
                ),
                (
                    ExcelContext(1, 1, "Image in Sheet: 2"),
                    "123.123.123.123\nWi-Fi\n500 kg",
                ),
            ],
        ),
        (
            "test_image.xlsx",
            ExcelFile,
            [
                (
                    ExcelContext(10, 3, "Image in Sheet: 1"),
                    "0.0.0.0\nhttp://localhost\n2 kbit/s",
                ),
                (
                    ExcelContext(1, 1, "Image in Sheet: 2"),
                    "123.123.123.123\nWi-Fi\n500 kg",
                ),
            ],
        ),
        ("xlsx_tes.xlsx", ExcelFile, spread_sheet_data()),
        ("xls_tes.xls", LegacyExcelFile, spread_sheet_data()),
        ("ods_tes.ods", LegacyExcelFile, spread_sheet_data()),
    ]


def spread_sheet_data():
    return [
        (ExcelContext(0, 0, 1), "dates"),
        (ExcelContext(0, 1, 1), "ipv4adresses"),
        (ExcelContext(0, 2, 1), "emails"),
        (ExcelContext(0, 3, 1), "doc- id"),
        (ExcelContext(0, 4, 1), "ipv6adresses"),
        (ExcelContext(0, 5, 1), "Mac-adresses"),
        (ExcelContext(0, 6, 1), "phone numbers"),
        (ExcelContext(0, 7, 1), "technologies and protocols"),
        (ExcelContext(0, 8, 1), "units"),
        (ExcelContext(0, 9, 1), "URLs"),
        (ExcelContext(0, 10, 1), "Wifi_protocols"),
        (ExcelContext(1, 0, 1), "2041-01-20B"),
        (ExcelContext(1, 1, 1), "31.564.808.882"),
        (ExcelContext(1, 2, 1), "^?i4&%t_}4-*ep!'+my.@q5-y0.0k.nu"),
        (ExcelContext(1, 3, 1), "nFOI-Z—2692--SE"),
        (ExcelContext(1, 4, 1), "648::bacM:7ee"),
        (ExcelContext(1, 5, 1), "p34-29-74-58-35-4b"),
        (ExcelContext(1, 6, 1), "+15871-492 83 24"),
        (ExcelContext(1, 7, 1), "6UART"),
        (ExcelContext(1, 8, 1), "802.12405 Ebitps"),
        (
            ExcelContext(1, 9, 1),
            "http://www.n6jp02j.dk/wok6sq/73i9tubh/jydt3es",
        ),
        (ExcelContext(1, 10, 1), "&802.11be"),
        (ExcelContext(0, 0, 2), "25/7 1974$"),
        (ExcelContext(0, 9, 2), "htt ps://5yarf.io/5f86/nep8rq95"),
        (ExcelContext(0, 10, 2), "7802.11ak"),
        (ExcelContext(150, 0, 2), "1976-11-22 00:00:00"),
        (ExcelContext(150, 10, 2), "802.11r"),
    ]


def pdf_test_data():
    return [
        (
            "pdf_tes.pdf",
            PdfFile,
            [
                (
                    "Page: 1",
                    "HEADERFOI-X--9999--SE\n123.21.0.22\nHej164.0.2.2\nIP\nMail\nID\nMac\nURL\n162.2.18.0\nuser@gmail.com\nFOI Memo 1234\n01:21:45:67:89:AB https://\ndummyurl.se/in/a/\ntable\nmailuser@usermail\nFooterText",
                ),
                ("Link at Page: 1", "mailto:mailuser@usermail"),
            ],
        ),
        (
            "test_image.pdf",
            PdfFile,
            [
                ("Page: 1, Image: 1", "0.0.0.0\nhttp://localhost\n2 kbit/s"),
                ("Page: 1, Image: 2", "123.123.123.123\nWi-Fi\n500 kg"),
            ],
        ),
        (
            "hyphenation.pdf",
            PdfFile,
            [
                (
                    "Page: 1",
                    "Lite lång text med något som kanske matchar eller kanske inte vad vet jag egentligen 192.168.200.200\negentligen egentligen egentligen egentligen egentligen egentligen egentligen 192.168.200.200\negentligen egentligen egentligen egentligen egentligen egentligen egentligen 192.168.200.200\n",
                ),
                (
                    "Page: 1, Image: 1",
                    "Lite lång text med något som kanske matchar eller kanske inte vad vet jag egentligen 192.168.200.200\negentligen egentligen egentligen egentligen egentligen egentligen egentligen 192.168.200.200\negentligen egentligen egentligen egentligen egentligen egentligen egentligen 192.168.200.200\n",
                ),
            ],
        ),
    ]


def image_test_data():
    return [
        (
            "test_image.eps",
            ImageFile,
            [(None, "0.0.0.0\nhttp://localhost\n2 kbit/s")],
        ),
        (
            "test_image.gif",
            ImageFile,
            [(None, "0.0.0.0\nhttp://localhost\n2 kbit/s")],
        ),
        (
            "test_image.jpg",
            ImageFile,
            [(None, "0.0.0.0\nhttp://localhost\n2 kbit/s")],
        ),
        (
            "test_image.png",
            ImageFile,
            [(None, "0.0.0.0\n2 kbit/s\nhttp://localhost")],
        ),
        (
            "test_image.svg",
            ImageFile,
            [(None, "0.0.0.0\nhttp://localhost\n2 kbit/s")],
        ),
        (
            "test_image.tif",
            ImageFile,
            [(None, "0.0.0.0\nhttp://localhost\n2 kbit/s")],
        ),
    ]


@pytest.mark.parametrize(
    "file_name, expected_type, expected_content",
    text_test_data()
    + word_test_data()
    + excel_test_data()
    + pdf_test_data()
    + image_test_data(),
)
def test_file_handler(file_name, expected_type, expected_content):
    file_path = os.path.join("tests/test_files", file_name)
    file_handler = FileHandler(True, False)
    files = file_handler.handle_input([file_path])
    content_handler = ContentHandler(False, 1)
    output = use_hyphen_plugin(content_handler.handle_input(files))
    assert len(files) == 1
    file = files[0]
    assert type(file) == expected_type
    print(f"File: {file_name}, cont: {file.content_with_context()}")

    content = [(content.context, content.content) for content in output[0][1]]

    assert content == expected_content
