from dataclasses import dataclass

from ResSimpy.DataModelBaseClasses.GridArrayDefinition import GridArrayDefinition
from ResSimpy.DataModelBaseClasses.LGR import LGR


@dataclass
class NexusLGR(LGR):
    """Class for handling a Local Grid Refinement (LGR) in the NexusGrid."""
    _dx: GridArrayDefinition
    _dy: GridArrayDefinition
    _dz: GridArrayDefinition
    _depth: GridArrayDefinition
    _mdepth: GridArrayDefinition
    _dznet: GridArrayDefinition
    _compr: GridArrayDefinition
    _icoars: GridArrayDefinition
    _ialphaf: GridArrayDefinition
    _ipolymer: GridArrayDefinition
    _iadsorption: GridArrayDefinition
    _itracer: GridArrayDefinition
    _igrid: GridArrayDefinition
    _isector: GridArrayDefinition
    _swl: GridArrayDefinition
    _swr: GridArrayDefinition
    _swu: GridArrayDefinition
    _sgl: GridArrayDefinition
    _sgr: GridArrayDefinition
    _sgu: GridArrayDefinition
    _swro: GridArrayDefinition
    _swro_ls: GridArrayDefinition
    _sgro: GridArrayDefinition
    _sgrw: GridArrayDefinition
    _krw_swro: GridArrayDefinition
    _krws_ls: GridArrayDefinition
    _krw_swu: GridArrayDefinition
    _krg_sgro: GridArrayDefinition
    _krg_sgu: GridArrayDefinition
    _krg_sgrw: GridArrayDefinition
    _kro_swl: GridArrayDefinition
    _kro_swr: GridArrayDefinition
    _kro_sgl: GridArrayDefinition
    _kro_sgr: GridArrayDefinition
    _krw_sgl: GridArrayDefinition
    _krw_sgr: GridArrayDefinition
    _sgtr: GridArrayDefinition
    _sotr: GridArrayDefinition
    _swlpc: GridArrayDefinition
    _sglpc: GridArrayDefinition
    _pcw_swl: GridArrayDefinition
    _pcg_sgu: GridArrayDefinition
    _chloride: GridArrayDefinition
    _calcium: GridArrayDefinition
    _salinity: GridArrayDefinition
    _api: GridArrayDefinition
    _tmx: GridArrayDefinition
    _tmy: GridArrayDefinition
    _tmz: GridArrayDefinition
    _multbv: GridArrayDefinition
    _pv: GridArrayDefinition
    _pvmult: GridArrayDefinition
    _livecell: GridArrayDefinition
    _worka1: GridArrayDefinition
    _worka2: GridArrayDefinition
    _worka3: GridArrayDefinition
    _worka4: GridArrayDefinition
    _worka5: GridArrayDefinition
    _worka6: GridArrayDefinition
    _worka7: GridArrayDefinition
    _worka8: GridArrayDefinition
    _worka9: GridArrayDefinition
    _kxeff: GridArrayDefinition
    _kyeff: GridArrayDefinition
    _kzeff: GridArrayDefinition

    def __init__(self, parent_grid: str, name: str, i1: int, i2: int, j1: int, j2: int, k1: int, k2: int,
                 nx: list[int], ny: list[int], nz: list[int]) -> None:
        """Initializes the NexusLGR class."""
        super().__init__(parent_grid, name, i1, i2, j1, j2, k1, k2, nx, ny, nz)
        self._pvmult: GridArrayDefinition = GridArrayDefinition()
        self._livecell: GridArrayDefinition = GridArrayDefinition()
        self._worka1: GridArrayDefinition = GridArrayDefinition()
        self._worka2: GridArrayDefinition = GridArrayDefinition()
        self._worka3: GridArrayDefinition = GridArrayDefinition()
        self._worka4: GridArrayDefinition = GridArrayDefinition()
        self._worka5: GridArrayDefinition = GridArrayDefinition()
        self._worka6: GridArrayDefinition = GridArrayDefinition()
        self._worka7: GridArrayDefinition = GridArrayDefinition()
        self._worka8: GridArrayDefinition = GridArrayDefinition()
        self._worka9: GridArrayDefinition = GridArrayDefinition()
        self._dx: GridArrayDefinition = GridArrayDefinition()
        self._dy: GridArrayDefinition = GridArrayDefinition()
        self._dz: GridArrayDefinition = GridArrayDefinition()
        self._depth: GridArrayDefinition = GridArrayDefinition()
        self._mdepth: GridArrayDefinition = GridArrayDefinition()
        self._dznet: GridArrayDefinition = GridArrayDefinition()
        self._compr: GridArrayDefinition = GridArrayDefinition()
        self._icoars: GridArrayDefinition = GridArrayDefinition()
        self._ialphaf: GridArrayDefinition = GridArrayDefinition()
        self._ipolymer: GridArrayDefinition = GridArrayDefinition()
        self._iadsorption: GridArrayDefinition = GridArrayDefinition()
        self._itracer: GridArrayDefinition = GridArrayDefinition()
        self._igrid: GridArrayDefinition = GridArrayDefinition()
        self._isector: GridArrayDefinition = GridArrayDefinition()
        self._swl: GridArrayDefinition = GridArrayDefinition()
        self._swr: GridArrayDefinition = GridArrayDefinition()
        self._swu: GridArrayDefinition = GridArrayDefinition()
        self._sgl: GridArrayDefinition = GridArrayDefinition()
        self._sgr: GridArrayDefinition = GridArrayDefinition()
        self._sgu: GridArrayDefinition = GridArrayDefinition()
        self._swro: GridArrayDefinition = GridArrayDefinition()
        self._swro_ls: GridArrayDefinition = GridArrayDefinition()
        self._sgro: GridArrayDefinition = GridArrayDefinition()
        self._sgrw: GridArrayDefinition = GridArrayDefinition()
        self._krw_swro: GridArrayDefinition = GridArrayDefinition()
        self._krws_ls: GridArrayDefinition = GridArrayDefinition()
        self._krw_swu: GridArrayDefinition = GridArrayDefinition()
        self._krg_sgro: GridArrayDefinition = GridArrayDefinition()
        self._krg_sgu: GridArrayDefinition = GridArrayDefinition()
        self._krg_sgrw: GridArrayDefinition = GridArrayDefinition()
        self._kro_swl: GridArrayDefinition = GridArrayDefinition()
        self._kro_swr: GridArrayDefinition = GridArrayDefinition()
        self._kro_sgl: GridArrayDefinition = GridArrayDefinition()
        self._kro_sgr: GridArrayDefinition = GridArrayDefinition()
        self._krw_sgl: GridArrayDefinition = GridArrayDefinition()
        self._krw_sgr: GridArrayDefinition = GridArrayDefinition()
        self._sgtr: GridArrayDefinition = GridArrayDefinition()
        self._sotr: GridArrayDefinition = GridArrayDefinition()
        self._swlpc: GridArrayDefinition = GridArrayDefinition()
        self._sglpc: GridArrayDefinition = GridArrayDefinition()
        self._pcw_swl: GridArrayDefinition = GridArrayDefinition()
        self._pcg_sgu: GridArrayDefinition = GridArrayDefinition()
        self._chloride: GridArrayDefinition = GridArrayDefinition()
        self._calcium: GridArrayDefinition = GridArrayDefinition()
        self._salinity: GridArrayDefinition = GridArrayDefinition()
        self._api: GridArrayDefinition = GridArrayDefinition()
        self._tmx: GridArrayDefinition = GridArrayDefinition()
        self._tmy: GridArrayDefinition = GridArrayDefinition()
        self._tmz: GridArrayDefinition = GridArrayDefinition()
        self._multbv: GridArrayDefinition = GridArrayDefinition()
        self._pv: GridArrayDefinition = GridArrayDefinition()
        self._kxeff: GridArrayDefinition = GridArrayDefinition()
        self._kyeff: GridArrayDefinition = GridArrayDefinition()
        self._kzeff: GridArrayDefinition = GridArrayDefinition()

    @property
    def netgrs(self) -> GridArrayDefinition:
        """Returns the netgrs values."""
        return self._netgrs

    @property
    def porosity(self) -> GridArrayDefinition:
        """Returns the porosity values."""
        return self._porosity

    @property
    def sw(self) -> GridArrayDefinition:
        """Returns the sw values."""
        return self._sw

    @property
    def sg(self) -> GridArrayDefinition:
        """Returns the sg values."""
        return self._sg

    @property
    def pressure(self) -> GridArrayDefinition:
        """Returns the pressure values."""
        return self._pressure

    @property
    def temperature(self) -> GridArrayDefinition:
        """Returns the temperature values."""
        return self._temperature

    @property
    def kx(self) -> GridArrayDefinition:
        """Returns the kx values."""
        return self._kx

    @property
    def ky(self) -> GridArrayDefinition:
        """Returns the ky values."""
        return self._ky

    @property
    def kz(self) -> GridArrayDefinition:
        """Returns the kz values."""
        return self._kz

    @property
    def dx(self) -> GridArrayDefinition:
        """Returns the dx values."""
        return self._dx

    @property
    def dy(self) -> GridArrayDefinition:
        """Returns the dy values."""
        return self._dy

    @property
    def dz(self) -> GridArrayDefinition:
        """Returns the dz values."""
        return self._dz

    @property
    def depth(self) -> GridArrayDefinition:
        """Returns the depth values."""
        return self._depth

    @property
    def mdepth(self) -> GridArrayDefinition:
        """Returns the mdepth values."""
        return self._mdepth

    @property
    def dznet(self) -> GridArrayDefinition:
        """Returns the dznet values."""
        return self._dznet

    @property
    def compr(self) -> GridArrayDefinition:
        """Returns the compr values."""
        return self._compr

    @property
    def icoars(self) -> GridArrayDefinition:
        """Returns the icoars values."""
        return self._icoars

    @property
    def ialphaf(self) -> GridArrayDefinition:
        """Returns the ialphaf values."""
        return self._ialphaf

    @property
    def ipolymer(self) -> GridArrayDefinition:
        """Returns the ipolymer values."""
        return self._ipolymer

    @property
    def iadsorption(self) -> GridArrayDefinition:
        """Returns the iadsorption values."""
        return self._iadsorption

    @property
    def itracer(self) -> GridArrayDefinition:
        """Returns the itracer values."""
        return self._itracer

    @property
    def igrid(self) -> GridArrayDefinition:
        """Returns the igrid values."""
        return self._igrid

    @property
    def isector(self) -> GridArrayDefinition:
        """Returns the isector values."""
        return self._isector

    @property
    def swl(self) -> GridArrayDefinition:
        """Returns the swl values."""
        return self._swl

    @property
    def swr(self) -> GridArrayDefinition:
        """Returns the swr values."""
        return self._swr

    @property
    def swu(self) -> GridArrayDefinition:
        """Returns the swu values."""
        return self._swu

    @property
    def sgl(self) -> GridArrayDefinition:
        """Returns the sgl values."""
        return self._sgl

    @property
    def sgr(self) -> GridArrayDefinition:
        """Returns the sgr values."""
        return self._sgr

    @property
    def sgu(self) -> GridArrayDefinition:
        """Returns the sgu values."""
        return self._sgu

    @property
    def swro(self) -> GridArrayDefinition:
        """Returns the swro values."""
        return self._swro

    @property
    def swro_ls(self) -> GridArrayDefinition:
        """Returns the swro_ls values."""
        return self._swro_ls

    @property
    def sgro(self) -> GridArrayDefinition:
        """Returns the sgro values."""
        return self._sgro

    @property
    def sgrw(self) -> GridArrayDefinition:
        """Returns the sgrw values."""
        return self._sgrw

    @property
    def krw_swro(self) -> GridArrayDefinition:
        """Returns the krw_swro values."""
        return self._krw_swro

    @property
    def krws_ls(self) -> GridArrayDefinition:
        """Returns the krws_ls values."""
        return self._krws_ls

    @property
    def krw_swu(self) -> GridArrayDefinition:
        """Returns the krw_swu values."""
        return self._krw_swu

    @property
    def krg_sgro(self) -> GridArrayDefinition:
        """Returns the krg_sgro values."""
        return self._krg_sgro

    @property
    def krg_sgu(self) -> GridArrayDefinition:
        """Returns the krg_sgu values."""
        return self._krg_sgu

    @property
    def krg_sgrw(self) -> GridArrayDefinition:
        """Returns the krg_sgrw values."""
        return self._krg_sgrw

    @property
    def kro_swl(self) -> GridArrayDefinition:
        """Returns the kro_swl values."""
        return self._kro_swl

    @property
    def kro_swr(self) -> GridArrayDefinition:
        """Returns the kro_swr values."""
        return self._kro_swr

    @property
    def kro_sgl(self) -> GridArrayDefinition:
        """Returns the kro_sgl values."""
        return self._kro_sgl

    @property
    def kro_sgr(self) -> GridArrayDefinition:
        """Returns the kro_sgr values."""
        return self._kro_sgr

    @property
    def krw_sgl(self) -> GridArrayDefinition:
        """Returns the krw_sgl values."""
        return self._krw_sgl

    @property
    def krw_sgr(self) -> GridArrayDefinition:
        """Returns the krw_sgr values."""
        return self._krw_sgr

    @property
    def sgtr(self) -> GridArrayDefinition:
        """Returns the sgtr values."""
        return self._sgtr

    @property
    def sotr(self) -> GridArrayDefinition:
        """Returns the sotr values."""
        return self._sotr

    @property
    def swlpc(self) -> GridArrayDefinition:
        """Returns the swlpc values."""
        return self._swlpc

    @property
    def sglpc(self) -> GridArrayDefinition:
        """Returns the sglpc values."""
        return self._sglpc

    @property
    def pcw_swl(self) -> GridArrayDefinition:
        """Returns the pcw_swl values."""
        return self._pcw_swl

    @property
    def pcg_sgu(self) -> GridArrayDefinition:
        """Returns the pcg_sgu values."""
        return self._pcg_sgu

    @property
    def chloride(self) -> GridArrayDefinition:
        """Returns the chloride values."""
        return self._chloride

    @property
    def calcium(self) -> GridArrayDefinition:
        """Returns the calcium values."""
        return self._calcium

    @property
    def salinity(self) -> GridArrayDefinition:
        """Returns the salinity values."""
        return self._salinity

    @property
    def api(self) -> GridArrayDefinition:
        """Returns the api values."""
        return self._api

    @property
    def tmx(self) -> GridArrayDefinition:
        """Returns the tmx values."""
        return self._tmx

    @property
    def tmy(self) -> GridArrayDefinition:
        """Returns the tmy values."""
        return self._tmy

    @property
    def tmz(self) -> GridArrayDefinition:
        """Returns the tmz values."""
        return self._tmz

    @property
    def multbv(self) -> GridArrayDefinition:
        """Returns the multbv values."""
        return self._multbv

    @property
    def pv(self) -> GridArrayDefinition:
        """Returns the pv values."""
        return self._pv

    @property
    def iequil(self) -> GridArrayDefinition:
        """Returns the iequil values."""
        return self._iequil

    @property
    def ipvt(self) -> GridArrayDefinition:
        """Returns the ipvt values."""
        return self._ipvt

    @property
    def iwater(self) -> GridArrayDefinition:
        """Returns the iwater values."""
        return self._iwater

    @property
    def irelpm(self) -> GridArrayDefinition:
        """Returns the irelpm values."""
        return self._irelpm

    @property
    def irock(self) -> GridArrayDefinition:
        """Returns the irock values."""
        return self._irock

    @property
    def itran(self) -> GridArrayDefinition:
        """Returns the itran values."""
        return self._itran

    @property
    def iregion(self) -> dict[str, GridArrayDefinition]:
        """Returns the iregion values."""
        return self._iregion

    @property
    def pvmult(self) -> GridArrayDefinition:
        """Returns the pvmult values."""
        return self._pvmult

    @property
    def livecell(self) -> GridArrayDefinition:
        """Returns the livecell values."""
        return self._livecell

    @property
    def worka1(self) -> GridArrayDefinition:
        """Returns the worka1 values."""
        return self._worka1

    @property
    def worka2(self) -> GridArrayDefinition:
        """Returns the worka2 values."""
        return self._worka2

    @property
    def worka3(self) -> GridArrayDefinition:
        """Returns the worka3 values."""
        return self._worka3

    @property
    def worka4(self) -> GridArrayDefinition:
        """Returns the worka4 values."""
        return self._worka4

    @property
    def worka5(self) -> GridArrayDefinition:
        """Returns the worka5 values."""
        return self._worka5

    @property
    def worka6(self) -> GridArrayDefinition:
        """Returns the worka6 values."""
        return self._worka6

    @property
    def worka7(self) -> GridArrayDefinition:
        """Returns the worka7 values."""
        return self._worka7

    @property
    def worka8(self) -> GridArrayDefinition:
        """Returns the worka8 values."""
        return self._worka8

    @property
    def worka9(self) -> GridArrayDefinition:
        """Returns the worka9 values."""
        return self._worka9

    @property
    def kxeff(self) -> GridArrayDefinition:
        """Returns the kxeff values."""
        return self._kxeff

    @property
    def kyeff(self) -> GridArrayDefinition:
        """Returns the kyeff values."""
        return self._kyeff

    @property
    def kzeff(self) -> GridArrayDefinition:
        """Returns the kzeff values."""
        return self._kzeff
