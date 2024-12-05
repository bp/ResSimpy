from abc import ABC
from dataclasses import dataclass

from ResSimpy.DataModelBaseClasses.GridArrayDefinition import GridArrayDefinition


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

    _netgrs: GridArrayDefinition
    _porosity: GridArrayDefinition
    _sw: GridArrayDefinition
    _sg: GridArrayDefinition
    _pressure: GridArrayDefinition
    _temperature: GridArrayDefinition
    _kx: GridArrayDefinition
    _ky: GridArrayDefinition
    _kz: GridArrayDefinition

    _iequil: GridArrayDefinition
    _ipvt: GridArrayDefinition
    _iwater: GridArrayDefinition
    _irelpm: GridArrayDefinition
    _irock: GridArrayDefinition
    _itran: GridArrayDefinition
    _iregion: dict[str, GridArrayDefinition]

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

        self._netgrs = GridArrayDefinition()
        self._porosity = GridArrayDefinition()
        self._sw = GridArrayDefinition()
        self._sg = GridArrayDefinition()
        self._pressure = GridArrayDefinition()
        self._temperature = GridArrayDefinition()
        self._kx = GridArrayDefinition()
        self._ky = GridArrayDefinition()
        self._kz = GridArrayDefinition()

        self._iequil: GridArrayDefinition = GridArrayDefinition()
        self._ipvt: GridArrayDefinition = GridArrayDefinition()
        self._iwater: GridArrayDefinition = GridArrayDefinition()
        self._irelpm: GridArrayDefinition = GridArrayDefinition()
        self._irock: GridArrayDefinition = GridArrayDefinition()
        self._itran: GridArrayDefinition = GridArrayDefinition()
        self._iregion: dict[str, GridArrayDefinition] = {}

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
        """Returns the x-direction refinement values."""
        return self._nx

    @property
    def ny(self) -> list[int]:
        """Returns the y-direction refinement values."""
        return self._ny

    @property
    def nz(self) -> list[int]:
        """Returns the z-direction refinement values."""
        return self._nz

    @property
    def netgrs(self) -> GridArrayDefinition:
        """Returns the net-to-gross grid array definition."""
        return self._netgrs

    @property
    def porosity(self) -> GridArrayDefinition:
        """Returns the porosity grid array definition."""
        return self._porosity

    @property
    def sw(self) -> GridArrayDefinition:
        """Returns the water saturation grid array definition."""
        return self._sw

    @property
    def sg(self) -> GridArrayDefinition:
        """Returns the gas saturation grid array definition."""
        return self._sg

    @property
    def pressure(self) -> GridArrayDefinition:
        """Returns the pressure grid array definition."""
        return self._pressure

    @property
    def temperature(self) -> GridArrayDefinition:
        """Returns the temperature grid array definition."""
        return self._temperature

    @property
    def kx(self) -> GridArrayDefinition:
        """Returns the kx grid array definition."""
        return self._kx

    @property
    def ky(self) -> GridArrayDefinition:
        """Returns the ky grid array definition."""
        return self._ky

    @property
    def kz(self) -> GridArrayDefinition:
        """Returns the kz grid array definition."""
        return self._kz

    @property
    def iequil(self) -> GridArrayDefinition:
        """Returns the iequil grid array definition."""
        return self._iequil

    @property
    def ipvt(self) -> GridArrayDefinition:
        """Returns the ipvt grid array definition."""
        return self._ipvt

    @property
    def iwater(self) -> GridArrayDefinition:
        """Returns the iwater grid array definition."""
        return self._iwater

    @property
    def irelpm(self) -> GridArrayDefinition:
        """Returns the irelpm grid array definition."""
        return self._irelpm

    @property
    def irock(self) -> GridArrayDefinition:
        """Returns the irock grid array definition."""
        return self._irock

    @property
    def itran(self) -> GridArrayDefinition:
        """Returns the itran grid array definition."""
        return self._itran

    @property
    def iregion(self) -> dict[str, GridArrayDefinition]:
        """Returns the iregion grid array definition."""
        return self._iregion

    @property
    def grid_array_defs(self) -> dict[str, GridArrayDefinition]:
        """Returns the grid array definitions in a dictionary keyed by the ResSimpy keyword associated with the
        grid array definition.
        """
        grid_array_defs = {'netgrs': self._netgrs,
                           'porosity': self._porosity,
                           'sw': self._sw,
                           'sg': self._sg,
                           'pressure': self._pressure,
                           'temperature': self._temperature,
                           'kx': self._kx,
                           'ky': self._ky,
                           'kz': self._kz,
                           'iequil': self._iequil,
                           'ipvt': self._ipvt,
                           'iwater': self._iwater,
                           'irelpm': self._irelpm,
                           'irock': self._irock,
                           'itran': self._itran}
        # filter to only include grid array definitions with a modifier
        grid_array_defs = {key: value for key, value in grid_array_defs.items() if value.modifier is not None or
                           value.value is not None or value.mods is not None}
        return grid_array_defs
