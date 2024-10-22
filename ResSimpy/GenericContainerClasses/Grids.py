from abc import ABC
from dataclasses import dataclass
from typing import Sequence

from ResSimpy.DataModelBaseClasses.Grid import Grid


@dataclass(kw_only=True)
class Grids(ABC):
    def get_grids(self) -> Sequence[Grid]:
        """Returns a list of grids."""
        raise NotImplementedError("Implement this in the derived class")

    def load_grids(self) -> Sequence[Grid]:
        """Loads a list of grid properties."""
        raise NotImplementedError("Implement this in the derived class")
