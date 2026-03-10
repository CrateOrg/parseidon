from parseidon.handlers.file_handler import FileHandler
from parseidon.handlers.content_handler import ContentHandler
from tests.helpers import use_hyphen_plugin
from parseidon.plugin_manager import PluginManager


def test_hyphenation_content():
    PluginManager.init_plugin_manager(False)
    files = FileHandler(True, False).handle_input(["tests/test_files/hyphenation.pdf"])
    handler = ContentHandler(True, 1)
    output = handler.handle_input(files)
    contents = use_hyphen_plugin(output)[0][1]
    count = 0
    for content in contents:
        text_content = content.content
        print(text_content)
        c = text_content.count("192.168.200.200")
        count += c
    assert count == 6
