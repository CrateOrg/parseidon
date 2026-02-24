import csv
import datetime
import json
import os
import sys
from abc import ABC, abstractmethod
from enum import Enum
from typing import Sequence

import pymupdf

from parseidon.handlers.handler import Handler
from parseidon.handlers.match import Match


class OutputFormat(Enum):
    """
    Class enumerating output file formats
    """

    CSV = 1
    JSON = 2
    PDF = 3

    @staticmethod
    def from_format_arg(format_arg: str):
        if format_arg == "csv":
            return OutputFormat.CSV
        elif format_arg == "json":
            return OutputFormat.JSON
        else:
            raise ValueError()  # Can not set PDF from cli

    def __str__(self) -> str:
        return self.name.lower()

    def file_ending(self) -> str:
        match self:
            case OutputFormat.CSV:
                return "csv"
            case OutputFormat.JSON:
                return "json"
            case OutputFormat.PDF:
                return "pdf"
            case _:
                raise RuntimeError(f"Unknown output format {self.value}!")


class OutputMode(Enum):
    """
    Class enumerating output modes
    """

    FILE = 1
    STDOUT = 2
    path: str | None

    @classmethod
    def from_output_arg(cls, output_arg):
        if output_arg == "-":
            return OutputMode.STDOUT
        else:
            format = OutputMode.FILE
            format.path = output_arg
            return format


OutputHandlerInput = Sequence[Match | pymupdf.Document]
OutputHandlerOutput = type(None)


class OutputStrategy(ABC):
    """
    Parent class for converting matches to
    different output formats
    """

    def __init__(self, output_path) -> None:
        self.output_path = output_path
        super().__init__()

    @abstractmethod
    def handle(self, input): ...


class MatchToJSON(OutputStrategy):
    """
    Class for writing matches to JSON
    """

    def handle(self, input: Sequence[Match]) -> None:
        """
        Transform match objects to JSON format and dump
        it to output file/stdout.

        Parameters:
            input (sequence): List of matches
        """
        data = [
            {
                "Object type": match.object_type,
                "Object found": match.found_object,
                "Filepath": match.file_path,
                "Position": match.position,
                "Context": match.context,
                "Count": match.count,
            }
            for match in input
        ]
        if self.output_path == sys.stdout:
            json.dump(data, self.output_path, indent=2)
        else:
            with open(self.output_path, "w", newline="") as jsonfile:
                json.dump(data, jsonfile, indent=2)


class MatchToCSV(OutputStrategy):
    """
    Class for writing matches to csv
    """

    def handle(self, input: Sequence[Match]):
        """
        Transform match objects to csv format and dump
        it to output file/stdout.

        Parameters:
            input (sequence): List of matches
        """
        fieldnames = [
            "Object type",
            "Object found",
            "Filepath",
            "Position",
            "Context",
            "Count",
        ]
        if self.output_path == sys.stdout:
            writer = csv.DictWriter(
                self.output_path, fieldnames=fieldnames, delimiter="|"
            )
            writer.writeheader()
            writer.writerows(
                [
                    {
                        "Object type": match.object_type,
                        "Object found": match.found_object,
                        "Filepath": match.file_path,
                        "Position": match.position,
                        "Context": match.context,
                        "Count": match.count,
                    }
                    for match in input
                ]
            )
        else:
            with open(self.output_path, "w", newline="") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter="|")
                writer.writeheader()
                writer.writerows(
                    [
                        {
                            "Object type": match.object_type,
                            "Object found": match.found_object,
                            "Filepath": match.file_path,
                            "Position": match.position,
                            "Context": match.context,
                            "Count": match.count,
                        }
                        for match in input
                    ]
                )


class DocumentToPDF(OutputStrategy):
    """
    Class for combining documents to one output pdf
    """

    def handle(self, input: Sequence[pymupdf.Document]) -> None:
        """
        Transform input pdf-documents to one output file.
        Save it or output to stdout

        Parameters:
            input (sequence): List of pdf-documents
        """
        combined_document = input[0]
        for doc in input[1:]:
            combined_document.insert_pdf(doc)

        if self.output_path == sys.stdout:
            sys.stdout.buffer.write(combined_document.tobytes())
        else:
            combined_document.save(self.output_path)


class OutputHandler(Handler[OutputHandlerInput, OutputHandlerOutput]):
    """
    Class for handling output

    Attributes:
        output_mode (OutputMode): Output to file or stdout
        format (OutputFormat): How should the output data be formatted
    """

    def __init__(self, output_mode: OutputMode, format: OutputFormat) -> None:
        """
        Initializes OutputHandler object

        Parameters:
            output_mode (OutputMode): Output to file or stdout
            format (OutputFormat): How should the output data be formatted
        """
        super().__init__()
        self.output_mode = output_mode
        self.format = format

    def handle_input(self, input: OutputHandlerInput) -> None:
        """
        Select output mode and format, output data accordingly

        Parameters:
            input (OutputHandlerInput): List of pdfs/matches to output
        """

        strategy = self.__select_strategy(self.output_mode, self.format, input)
        strategy.handle(input)  # type: ignore

    def __select_strategy(
        self, output_mode: OutputMode, format: OutputFormat, input: OutputHandlerInput
    ) -> OutputStrategy:
        """
        Select output strategy based on mode and format.

        Parameters:
            output_mode (OutputMode): Output to file or stdout
            format (OutputFormat): How should the output data be formatted
            input (OutputHandlerInput): List of pdfs/matches to output

        Returns:
            OutputStrategy: Object that can output data in correct
                            format and to the correct location
        """
        if output_mode == OutputMode.STDOUT:
            output_path = sys.stdout
        elif output_mode == OutputMode.FILE:
            output_path = self.__format_out_name(output_mode, format.file_ending())

        all_matches = all(isinstance(match, Match) for match in input)
        all_document = not all_matches and all(
            isinstance(image, pymupdf.Document) for image in input
        )

        if all_matches and format == OutputFormat.CSV:
            return MatchToCSV(output_path)
        elif all_matches and format == OutputFormat.JSON:
            return MatchToJSON(output_path)
        elif all_document and format == OutputFormat.PDF:
            return DocumentToPDF(output_path)
        else:
            raise RuntimeError("Can not output data! Invalid input format")

    def __format_out_name(self, output_mode: OutputMode, file_ending: str) -> str:
        """
        Select output strategy based on mode and format.

        Parameters:
            output_mode (OutputMode): Output to file or stdout
            file_ending (str): File extension (fileformat)

        Returns:
            str: Output path
        """
        now = datetime.datetime.now()
        time = now.strftime("%Y-%m-%d_%H:%M:%S")
        path = output_mode.path
        if not path:
            raise RuntimeError("Output path was not set!")
        if not os.path.basename(path):
            path = os.path.join(path, f"{time}.{file_ending}")
        return path
