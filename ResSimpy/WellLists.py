from dataclasses import dataclass
from abc import ABC
from typing import Literal, Sequence


@dataclass(kw_only=True)
class WellList:
    """Class for representing a single WellList or group for the model."""
    name: str
    wells: list[str]
    date: str


@dataclass(kw_only=True)
class WellLists(ABC):
    """Class for representing a set of WellList objects for the model."""
    __well_lists: Sequence[WellList]

    def __init__(self, welllists: Sequence[WellList]) -> None:
        """Initialises the WellLists class.

        Args:
            welllists (Sequence[WellList]): List of WellList objects.
        """
        self.__well_lists = welllists

    @property
    def _network_element_name(self) -> Literal['welllists']:
        return 'welllists'

    @property
    def welllists(self) -> Sequence[WellList]:
        """Returns all WellList instances."""
        return self.__well_lists

    @property
    def unique_names(self) -> list[str]:
        """Returns all WellList names."""
        return list({x.name for x in self.welllists})
