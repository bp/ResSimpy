from abc import ABC
from dataclasses import dataclass
from typing import Literal, Sequence

from ResSimpy.WellList import WellList


@dataclass(kw_only=True)
class WellLists(ABC):
    """Class for representing a set of WellList objects for the model."""
    _well_lists: Sequence[WellList]

    def __init__(self) -> None:
        """Initialises the WellLists class."""
        self._well_lists = []

    @property
    def _network_element_name(self) -> Literal['welllists']:
        return 'welllists'

    @property
    def welllists(self) -> Sequence[WellList]:
        """Returns all WellList instances."""
        return self._well_lists

    @property
    def unique_names(self) -> list[str]:
        """Returns all WellList names."""
        return list({x.name for x in self.welllists if x.name is not None})

    def get_all_by_name(self, well_list_name: str) -> Sequence[WellList]:
        """Returns a single WellList instance by name.

        Args:
            well_list_name (str): The name of the WellList.

        Returns:
            WellList: The WellList instance.
        """
        return [x for x in self._well_lists if x.name == well_list_name]
