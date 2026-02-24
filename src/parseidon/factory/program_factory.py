from parseidon.mode.filter_mode import FilterMode
from parseidon.mode.find_mode import FindMode
from parseidon.mode.pegparse_mode import PegParseMode
from parseidon.mode.regex_mode import RegexMode


def program_factory(args):
    match args.command:
        case RegexMode.command:
            return RegexMode.from_args(args)
        case PegParseMode.command:
            return PegParseMode.from_args(args)
        case FilterMode.command:
            return FilterMode.from_args(args)
        case FindMode.command:
            return FindMode.from_args(args)
        case _:
            raise RuntimeError("Unknown command")

