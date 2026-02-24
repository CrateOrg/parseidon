from abc import ABC, abstractmethod
from typing import Generic, TypeVar

HandlerInput = TypeVar("HandlerInput")
HandlerOutput = TypeVar("HandlerOutput")


class Handler(ABC, Generic[HandlerInput, HandlerOutput]):
    @abstractmethod
    def handle_input(self, input: HandlerInput) -> HandlerOutput: ...

