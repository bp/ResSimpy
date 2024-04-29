from dataclasses import dataclass
from abc import ABC

from ResSimpy.Enums.FrequencyEnum import FrequencyEnum
from ResSimpy.Enums.OutputType import OutputType


@dataclass(kw_only=True)
class OutputRequest(ABC):
    """Class to hold data input for an Output Request.

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


@dataclass(kw_only=True)
class OutputContents(ABC):
    """Class to hold data input for an Output Contents.

    Attributes:
        date (str): Date of the output contents.
        output (str): Output contents.
        output_type (OutputType): Type of output contents.
    """

    date: str
    output: str
    output_type: OutputType
