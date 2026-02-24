from typing import Callable, Sequence, TypeVar

from parseidon.handlers.handler import Handler
from parseidon.handlers.match import Match
from parseidon.handlers.matcher_handlers.matcher_handler import MatcherHandlerOutput

ConversionHandlerInput = TypeVar("ConversionHandlerInput")
ConversionHandlerOutput = TypeVar("ConversionHandlerOutput")


class ConversionHandler(Handler[ConversionHandlerInput, ConversionHandlerOutput]):
    """
    Class for converting handler output to match another handlers
    required input format

    Attributes:
        converter (Callable): Function to convert input to desired format
    """

    def __init__(
        self, converter: Callable[[ConversionHandlerInput], ConversionHandlerOutput]
    ) -> None:
        """
        Initializes ConversionHandler object

        Parameters:
            converter (Callable): Function to convert input to desired format
        """
        super().__init__()
        self.converter = converter

    def handle_input(self, input: ConversionHandlerInput) -> ConversionHandlerOutput:
        """
        Converts input to desired format

        Parameters:
            input (ConversionHandlerInput): Input data to be converted

        Returns:
            ConversionHandlerOutput: Input data converted to correct format
        """
        return self.converter(input)


class MatcherHandlerToOutputHandlerConverter(
    ConversionHandler[MatcherHandlerOutput, Sequence[Match]]
):
    """
    Class for converting MatcherHandler output to match OutputHandler
    input format
    """

    def __init__(self) -> None:
        """
        Initializes MatcherHandlerToOutputHandlerConverter object

        Parameters:-
        """
        super().__init__(
            lambda doc_list: [match for _, matches in doc_list for match in matches]
        )
