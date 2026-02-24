import logging
from typing import Any

from parseidon.handlers.handler import Handler

logger = logging.getLogger(__name__)


class Chain:
    """
    Class for managing handlers in a chain

    Attributes: -
    """

    def __init__(self) -> None:
        """
        Initializes a Chain object

        Parameters: -
        """
        self.chain: list[Handler] = []

    def add_handler(self, handler: Handler) -> None:
        """
        Add a handler to the chain

        Parameters:
            handler (Handler): Handler to be added to the chain
        """
        self.chain.append(handler)

    def handle_input(self, input: Any) -> Any:
        """
        For each handler in the chain, let it handle
        input data in its intended way

        Parameters:
            input (Any): Input data to handlers, depends on handler

        Returns:
            Any: Depends on handler
        """
        next_input = input
        for handler in self.chain:
            try:
                next_input = handler.handle_input(next_input)
            except Exception as e:
                logger.exception("An unexpected error occurred!")
                raise e

        return next_input
