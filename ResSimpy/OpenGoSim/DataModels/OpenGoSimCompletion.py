from dataclasses import dataclass
from typing import Optional

from ResSimpy.DataModelBaseClasses.Completion import Completion
from ResSimpy.Enums.PenetrationDirectionEnum import PenetrationDirectionEnum
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.Units.AttributeMappings.CompletionUnitMapping import CompletionUnits


@dataclass(kw_only=True)
class OpenGoSimCompletion(Completion):

    __penetration_direction: Optional[PenetrationDirectionEnum]
    __is_open: bool
    __refinement_name: Optional[str]

    def __init__(self, date: str, i: Optional[int] = None, j: Optional[int] = None, k: Optional[int] = None,
                 penetration_direction: Optional[PenetrationDirectionEnum] = None, is_open: Optional[bool] = None,
                 refinement_name: Optional[str] = None) -> None:
        """Initialises the OpenGoSimCompletion class.

        Args:
            date (str): The date of the completion.
            i (Optional[int]): The i index of the completion.
            j (Optional[int]): The j index of the completion.
            k (Optional[int]): The k index of the completion.
            penetration_direction (Optional[PenetrationDirectionEnum]): The direction of the penetration for the
            completion.
            is_open (Optional[bool]): Whether the completion is open or closed. If True the completion is open.
            refinement_name (Optional[str]): The grid refinement name that the completion is applied to.
        """
        self.__penetration_direction = penetration_direction
        self.__is_open = is_open if is_open is not None else True
        self.__refinement_name = refinement_name
        super().__init__(i=i, j=j, k=k, date=date, date_format=DateFormat.DD_MMM_YYYY)

    def __repr__(self) -> str:
        return f"i: {self.i} j: {self.j} k: {self.k}"

    def is_open_set(self, value: bool) -> None:
        """Set the open state of a completion."""
        self.__is_open = value

    @property
    def refinement_name(self) -> Optional[str]:
        """The refinement name that the completion is applied to."""
        return self.__refinement_name

    @property
    def penetration_direction(self) -> Optional[PenetrationDirectionEnum]:
        """The direction of the penetration for the completion."""
        return self.__penetration_direction

    @property
    def is_open(self) -> bool:
        """Whether the completion is perforated or not."""
        return self.__is_open

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
        return self.__is_open
