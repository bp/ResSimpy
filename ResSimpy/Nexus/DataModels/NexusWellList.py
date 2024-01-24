"""Holds a class for representing a single WellList or group for the Nexus model."""
from dataclasses import dataclass

from ResSimpy.Units.AttributeMappings.BaseUnitMapping import BaseUnitMapping
from ResSimpy.WellLists import WellList


@dataclass(kw_only=True, init=False)
class NexusWellList(WellList):
    """Class for representing a single WellList or group for the Nexus model."""

    def __init__(self, name: str, wells: list[str], date: str) -> None:
        super().__init__(name=name, wells=wells, date=date)

    @staticmethod
    def get_keyword_mapping() -> dict[str, tuple[str, type]]:
        return {}

    @property
    def units(self) -> BaseUnitMapping:
        """Returns the attribute to unit map for the data object."""
        return BaseUnitMapping(None)
