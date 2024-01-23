"""Holds a class for representing a single WellList or group for the Nexus model."""
from dataclasses import dataclass

from ResSimpy.DataObjectMixin import DataObjectMixin
from ResSimpy.Units.AttributeMappings.BaseUnitMapping import BaseUnitMapping


@dataclass(kw_only=True)
class NexusWellList(DataObjectMixin):
    """Class for representing a single WellList for the Nexus model."""
    name: str
    wells: list[str]
    date: str

    @staticmethod
    def get_keyword_mapping() -> dict[str, tuple[str, type]]:
        return {}

    @property
    def units(self) -> BaseUnitMapping:
        """Returns the attribute to unit map for the data object."""
        return BaseUnitMapping(None)
