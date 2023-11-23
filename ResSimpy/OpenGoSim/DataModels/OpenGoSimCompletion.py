from dataclasses import dataclass

from ResSimpy.Completion import Completion
from ResSimpy.Units.AttributeMappings.BaseUnitMapping import BaseUnitMapping


@dataclass(kw_only=True)
class OpenGoSimCompletion(Completion):

    @staticmethod
    def get_keyword_mapping() -> dict[str, tuple[str, type]]:
        """Gets the mapping of keywords to attribute definitions."""
        raise NotImplementedError("Not implemented for OGS yet")

    @property
    def units(self) -> BaseUnitMapping:
        """Returns the attribute to unit map for the data object."""
        raise NotImplementedError("Not implemented for OGS yet")
