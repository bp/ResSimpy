from dataclasses import dataclass
from abc import ABC
from typing import Literal


@dataclass(kw_only=True)
class WellList:
    """Class for representing a single WellList or group for the model."""
    name: str
    wells: list[str]
    date: str


@dataclass(kw_only=True)
class WellLists(ABC):
    """Class for representing a set of WellList objects for the model."""

    @property
    def _network_element_name(self) -> Literal['welllists']:
        return 'welllists'
