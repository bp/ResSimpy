from dataclasses import dataclass
from abc import ABC

from ResSimpy.DataObjectMixin import DataObjectMixin
from ResSimpy.Enums.FrequencyEnum import FrequencyEnum
from ResSimpy.Enums.OutputType import OutputType
from ResSimpy.Units.AttributeMappings.BaseUnitMapping import BaseUnitMapping


@dataclass(kw_only=True)
class OutputRequest(DataObjectMixin, ABC):
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

    @staticmethod
    def get_keyword_mapping() -> dict[str, tuple[str, type]]:
        """No keywords for this class, returns an empty dict."""
        return {}

    @property
    def units(self) -> BaseUnitMapping:
        return BaseUnitMapping(unit_system=None)


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
    output_contents: list[str]
    output_type: OutputType
