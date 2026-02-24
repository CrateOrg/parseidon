from parseidon.handlers.conversion_handler import ConversionHandler


def test_conversion_handler():
    handler = ConversionHandler[int, str](lambda number: f"{number}")
    assert "123456" == handler.handle_input(123456)
