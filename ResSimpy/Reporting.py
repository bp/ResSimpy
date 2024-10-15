from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import Sequence, TYPE_CHECKING

from ResSimpy.DataModelBaseClasses.output_request import OutputRequest, OutputContents
if TYPE_CHECKING:
    from ResSimpy.DataModelBaseClasses.Simulator import Simulator


@dataclass(kw_only=True)
class Reporting(ABC):
    """Base class for reporting in ResSimpy."""

    __ss_output_requests: Sequence[OutputRequest]
    __ss_output_contents: Sequence[OutputContents]
    __array_output_requests: Sequence[OutputRequest]
    __array_output_contents: Sequence[OutputContents]

    def __init__(self, model: Simulator) -> None:
        """Initialises the Reporting class with a parent model."""
        self.__model = model
        self.__ss_output_requests = []
        self.__ss_output_contents = []
        self.__array_output_requests = []
        self.__array_output_contents = []

    @property
    def ss_output_requests(self) -> Sequence[OutputRequest]:
        """Gets the spreadsheet and tabulated output requests."""
        return self.__ss_output_requests

    @property
    def ss_output_contents(self) -> Sequence[OutputContents]:
        """Gets the contents requested for spreadsheet and tabulated results."""
        return self.__ss_output_contents

    @property
    def array_output_requests(self) -> Sequence[OutputRequest]:
        """Gets the array output requests."""
        return self.__array_output_requests

    @property
    def array_output_contents(self) -> Sequence[OutputContents]:
        """Gets the contents requested to be output for the arrays."""
        return self.__array_output_contents
