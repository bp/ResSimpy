from abc import ABC
from dataclasses import dataclass
from typing import Optional

from ResSimpy.DataModelBaseClasses.DataObjectMixin import DataObjectMixin
from ResSimpy.Enums.FrequencyEnum import FrequencyEnum
from ResSimpy.Enums.OutputType import OutputType
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
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

    output: str
    output_type: OutputType
    output_frequency: FrequencyEnum
    output_frequency_number: None | float

    def __init__(self, date: str, output: str, output_type: OutputType, output_frequency: FrequencyEnum,
                 output_frequency_number: Optional[float] = None, date_format: Optional[DateFormat] = None,
                 start_date: Optional[str] = None) -> None:
        """Initialises the OutputRequest class.

        Args:
            date (str): Date of the output request.
            output (str): Output request.
            output_type (OutputType): Type of output request.
            output_frequency (FrequencyEnum): Frequency of the output request.
            output_frequency_number (None | float): Number of the frequency of the output request.
            date_format (Optional[DateFormat]): The date format of the object.
            start_date (Optional[str]): The start date of the model (required if the date is in numerical format).
        """

        super().__init__(date=date, date_format=date_format, start_date=start_date)

        self.output = output
        self.output_type = output_type
        self.output_frequency = output_frequency
        self.output_frequency_number = output_frequency_number

    @staticmethod
    def get_keyword_mapping() -> dict[str, tuple[str, type]]:
        """No keywords for this class, returns an empty dict."""
        return {}

    @property
    def units(self) -> BaseUnitMapping:
        """Writes unit type for the given unit system.

        Returns:
            An instance of the BaseUnitMapping class.
        """
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
