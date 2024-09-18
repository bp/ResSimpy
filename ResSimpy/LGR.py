from abc import ABC
from dataclasses import dataclass


@dataclass
class LGR(ABC):
    """Abstract base class for Local Grid Refinements (LGR)."""
    _parent_grid: str
    _name: str
    # range of grid blocks
    _i1: int
    _i2: int
    _j1: int
    _j2: int
    _k1: int
    _k2: int
    _nx: list[int]
    _ny: list[int]
    _nz: list[int]

    def __init__(self, parent_grid: str, name: str, i1: int, i2: int, j1: int, j2: int, k1: int, k2: int,  # noqa: D417
                 nx: list[int], ny: list[int], nz: list[int]) -> None:
        """Initializes the LGR class.

        Args:
            parent_grid (str): Name of the parent grid.
            name (str): Name of the LGR.
            i1, i2, j1, j2, k1, k2 (int): Range of grid blocks.
            nx, ny, nz (list[int]): number of x/y/z direction fine gridblocks for each corresponding coarse gridblock.
        """
        self._parent_grid = parent_grid
        self._name = name

        self._i1 = i1
        self._i2 = i2
        self._j1 = j1
        self._j2 = j2
        self._k1 = k1
        self._k2 = k2

        self._nx = nx
        self._ny = ny
        self._nz = nz

    @property
    def range(self) -> tuple[int, int, int, int, int, int]:
        """Returns the range of grid blocks in the parent grid."""
        return (self._i1, self._i2, self._j1, self._j2, self._k1, self._k2)

    @property
    def name(self) -> str:
        """Returns the name of the LGR."""
        return self._name

    @property
    def parent_grid(self) -> str:
        """Returns the name of the parent grid."""
        return self._parent_grid

    @property
    def nx(self) -> list[int]:
        """Returns the nx values."""
        return self._nx

    @property
    def ny(self) -> list[int]:
        """Returns the ny values."""
        return self._ny

    @property
    def nz(self) -> list[int]:
        """Returns the nz values."""
        return self._nz
