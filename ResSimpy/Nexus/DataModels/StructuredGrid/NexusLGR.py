from dataclasses import dataclass

from ResSimpy.LGR import LGR


@dataclass
class NexusLGR(LGR):
    """Class for handling a Local Grid Refinement (LGR) in the NexusGrid."""

    def __init__(self, parent_grid: str, name: str, i1: int, i2: int, j1: int, j2: int, k1: int, k2: int,
                 nx: list[int], ny: list[int], nz: list[int]) -> None:
        """Initializes the NexusLGR class."""
        super().__init__(parent_grid, name, i1, i2, j1, j2, k1, k2, nx, ny, nz)
