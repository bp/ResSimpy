"""Data objects for handling output requests and contents in Nexus."""

from __future__ import annotations

from dataclasses import dataclass

from ResSimpy.Enums.FrequencyEnum import FrequencyEnum
from ResSimpy.Enums.OutputType import OutputType
from ResSimpy.output_request import OutputRequest, OutputContents


@dataclass(kw_only=True)
class NexusOutputRequest(OutputRequest):
    """Class for handling output requests in Nexus.

    Attributes:
        date (str): Date of the output request.
        output (str): Output request.
        output_type (OutputType): Type of output request.
        output_frequency (FrequencyEnum): Frequency of the output request.
        output_frequency_number (None | float): Number of the frequency of the output request.
    """
    date: str
    output: str
    output_type: OutputType
    output_frequency: FrequencyEnum
    output_frequency_number: None | float

    def to_table_line(self, headers: list[str]) -> str:
        """String representation of the single line within an Output request table."""
        _ = headers
        result = f'{self.output} {self.output_frequency.name}'
        if self.output_frequency_number is not None:
            result += ' ' + str(self.output_frequency_number)
        result += '\n'
        return result


@dataclass(kw_only=True)
class NexusOutputContents(OutputContents):
    """Class for handling the output that Nexus produces."""
    date: str
    output_contents: list[str]
    output_type: OutputType
    output: str
