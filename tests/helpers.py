import re
from typing import Sequence

import pluggy
import yaml
from marisa_trie import Trie
from parsimonious import Grammar

from parseidon.files.file import File
from parseidon.handlers.content import Content
from parseidon.handlers.matcher_handlers.filter_matcher_handler import (
    FilterMatcherHandler,
)
from parseidon.handlers.matcher_handlers.peg_parse_matcher_handler import (
    PegParseMatcherHandler,
)
from parseidon.handlers.matcher_handlers.regex_matcher_handler import (
    RegexMatcherHandler,
)
from parseidon.helpers.resource_loader import open_file
from parseidon.hookspecs import ContentHandlerSpecs
from parseidon_headings_plugin.src.parseidon_headings_plugin.remove_headings import (
    RemoveHeadingPlugin,
)
from parseidon_hyphen_plugin.src.parseidon_hyphen_plugin.dehyphenate import (
    DehyphenatePlugin,
)

testfiles_path = "./tests/test_files/"
val_path = "./tests/tests_expected_output/"
regex_file = "regex_files/main_regex.yaml"
peg_file = "peg_files/peg_grammars.txt"
trie_file = "trie/swedish.marisa"
skip_list_file = "skip_lists/skip_list1.txt"
pegs_ind_path = "peg_files/individual_pegs/"


def skip_list() -> set[str]:
    with open_file(skip_list_file, "r") as f:
        skips = f.read().splitlines()
        return set(skips)


def filter_matcher(tf=trie_file):
    return FilterMatcherHandler(tf, True, [])


def regex_matcher(
    pattern_type: str | None = None, skip_list: set = set()
) -> RegexMatcherHandler:
    patterns = {}

    with open_file(regex_file, "r") as file:
        raw_patterns = yaml.safe_load(file)

    for reg_type, regex in raw_patterns.items():
        curr_regex = "".join(regex) if isinstance(regex, list) else regex
        try:
            if pattern_type == None or reg_type == pattern_type:
                patterns[reg_type] = re.compile(curr_regex)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {curr_regex} Error: {e}")

    return RegexMatcherHandler(patterns, skip_list)


def peg_matcher(grammar_file: str = peg_file, skip_list: set = set()):
    with open_file(grammar_file, "r") as f:
        grammar_text = f.read()
    return PegParseMatcherHandler(Grammar(grammar_text), skip_list)


def use_hyphen_plugin(output):
    pm = pluggy.PluginManager(project_name="parseidon")
    pm.add_hookspecs(ContentHandlerSpecs)
    pm.register(DehyphenatePlugin())
    output = pm.hook.post_process_content(output=output, trie_file=None)
    return output[0]


def remove_ip_headings(output):
    pm = pluggy.PluginManager(project_name="parseidon")
    pm.add_hookspecs(ContentHandlerSpecs)
    pm.register(RemoveHeadingPlugin())
    output = pm.hook.post_process_content(output=output, trie_file=None)
    return output[0]


class DummyFile(File):

    def __init__(self, name, filetype, path, raw_content):
        super().__init__(name, filetype, path, True)
        self._content = raw_content

    def _get_content(self):
        return self._content

    def content_with_context(self) -> Sequence[Content]:
        return [Content("P1", self._content, self), Content("P2", self._content, self)]

    def get_position_for_context(self, context, start_pos) -> str:
        return "In test file"

    def get_neighbor_context_for(self, context, start_pos, end_pos) -> str:
        return self._content[start_pos:end_pos]
