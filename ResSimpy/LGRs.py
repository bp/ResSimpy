from abc import ABC
from dataclasses import dataclass, field
from typing import Sequence

from ResSimpy.DataModelBaseClasses.LGR import LGR


@dataclass
class LGRs(ABC):
    """Abstract base class for Local Grid Refinements (LGR)."""
    _lgrs: Sequence[LGR] = field(default_factory=list)

    def __init__(self, lgrs: None | Sequence[LGR] = None) -> None:
        """Initializes the LGRs class."""
        self._lgrs: Sequence[LGR] = [] if lgrs is None else lgrs

    @property
    def lgrs(self) -> Sequence[LGR]:
        """Returns the list of LGRs."""
        return self._lgrs

    def get_all(self) -> Sequence[LGR]:
        """Returns all LGRs."""
        return self.lgrs
