"""Class for handling the set of Local Grid Refinements (LGR) in the NexusGrid."""
from dataclasses import dataclass, field

from ResSimpy.LGRs import LGRs
from ResSimpy.Nexus.DataModels.StructuredGrid.NexusLGR import NexusLGR


@dataclass
class NexusLGRs(LGRs):
    """Class for handling the set of Local Grid Refinements (LGR) in the NexusGrid."""

    _lgrs: list[NexusLGR] = field(default_factory=list)
    _grid_file_as_list: list[str] = field(default_factory=list)
    __has_been_loaded: bool = False

    def __init__(self, lgrs: None | list[NexusLGR] = None, assume_loaded: bool = False) -> None:
        """Initializes the NexusLGRs class."""
        super().__init__(lgrs=lgrs)
        self.__has_been_loaded = assume_loaded

    def load_lgrs(self) -> None:
        """Loads LGRs from a list of strings."""
        # Implementation to load LGRs from the provided list

        self.__has_been_loaded = True

    @property
    def lgrs(self) -> list[NexusLGR]:
        """Collection of the LGRs in the NexusGrid."""
        if not self.__has_been_loaded:
            self.load_lgrs()
        return self._lgrs
