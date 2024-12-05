"""Data objects for handling output requests and contents in Nexus."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from ResSimpy.Enums.FrequencyEnum import FrequencyEnum
from ResSimpy.Enums.OutputType import OutputType
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.DataModelBaseClasses.output_request import OutputRequest, OutputContents


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

    def __init__(self, date: str, output: str, output_type: OutputType, output_frequency: FrequencyEnum,
                 output_frequency_number: Optional[float] = None, date_format: Optional[DateFormat] = None,
                 start_date: Optional[str] = None) -> None:
        """Initialises the NexusOutputRequest class.

        Args:
            date (str): Date of the output request.
            output (str): Output request.
            output_type (OutputType): Type of output request.
            output_frequency (FrequencyEnum): Frequency of the output request.
            output_frequency_number (None | float): Number of the frequency of the output request.
            date_format (Optional[DateFormat]): The date format of the object.
            start_date (Optional[str]): The start date of the model (required if the date is in numerical format).
        """

        super().__init__(output=output, output_type=output_type, output_frequency=output_frequency,
                         output_frequency_number=output_frequency_number, date=date, date_format=date_format,
                         start_date=start_date)

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
