from dataclasses import dataclass
from typing import Optional

from ResSimpy.Completion import Completion
from ResSimpy.Enums.PenetrationDirectionEnum import PenetrationDirectionEnum
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.Units.AttributeMappings.CompletionUnitMapping import CompletionUnits


@dataclass(kw_only=True)
class OpenGoSimCompletion(Completion):

    __penetration_direction: Optional[PenetrationDirectionEnum]

    def __init__(self, date: str, i: Optional[int] = None, j: Optional[int] = None, k: Optional[int] = None,
                 penetration_direction: Optional[PenetrationDirectionEnum] = None) -> None:
        self.__penetration_direction = penetration_direction
        super().__init__(i=i, j=j, k=k, date=date, date_format=DateFormat.DD_MMM_YYYY)

    @staticmethod
    def get_keyword_mapping() -> dict[str, tuple[str, type]]:
        """Gets the mapping of keywords to attribute definitions."""
        raise NotImplementedError("Not implemented for OGS yet")

    @property
    def units(self) -> CompletionUnits:
        """Returns the attribute to unit map for the data object."""
        raise NotImplementedError("Not implemented for OGS yet")

    @property
    def completion_is_perforation(self) -> bool:
        """Determines if the supplied completion is a perforation or not."""
        raise NotImplementedError("Not implemented yet.")
