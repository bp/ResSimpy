from abc import ABC
from dataclasses import dataclass, field
from typing import Sequence

from ResSimpy.DataModelBaseClasses.LGR import LGR


@dataclass
class LGRs(ABC):
    """Abstract base class for Local Grid Refinements (LGR)."""
    _lgr_list: Sequence[LGR] = field(default_factory=list)

    def __init__(self, lgr_list: None | Sequence[LGR] = None) -> None:
        """Initializes the LGRs class."""
        self._lgr_list: Sequence[LGR] = [] if lgr_list is None else lgr_list

    @property
    def lgr_list(self) -> Sequence[LGR]:
        """Returns the list of LGRs."""
        return self._lgr_list

    def get_all(self) -> Sequence[LGR]:
        """Returns all LGRs."""
        return self._lgr_list
