"""The base class for all Well Completions."""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Sequence

from ResSimpy.DataObjectMixin import DataObjectMixin
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.ISODateTime import ISODateTime
from ResSimpy.Nexus.NexusEnums import DateFormatEnum
from ResSimpy.Units.AttributeMappings.CompletionUnitMapping import CompletionUnits


@dataclass(kw_only=True, repr=False)
class Completion(DataObjectMixin, ABC):
    """A class representing well completions.

    IMPORTANT: if modifying this class, make sure to update the relevant tests in test_load_wells, as well as updating
    the constructor calls in the derived classes.

    Args:
    ----
        date (str): The starting date of the completion. Applies until changed.
        i (Optional[int]): The structured grid cell location in the x direction. 'IW' in Nexus
        j (Optional[int]): The structured grid cell location in the y direction. 'JW' in Nexus
        k (Optional[int]): The structured grid cell location in the z direction. 'L' in Nexus
        skin (Optional[float]): The skin value for the completion. 'SKIN' in Nexus
        depth (Optional[float]): The depth of the completion. 'DEPTH' in Nexus
        well_radius (Optional[float]): The well radius. 'RADW' in Nexus
        x (Optional[float]): The x location of the well in distance units/coordinates. 'X' in Nexus
        y (Optional[float]): The y location of the well in distance units/coordinates. 'Y' in Nexus
        angle_a (Optional[float]): the angle relative to the local I axis. 'ANGLA' in Nexus.
        angle_v (Optional[float]): the angle relative to the true vertical axis (global Z axis). 'ANGLV' in Nexus
        grid (Optional[str]): the grid name to which the completion data applies. 'GRID' in Nexus
        depth_to_top (Optional[float]): subsea depth to the top of a completion interval. 'DTOP' in Nexus
        depth_to_bot (Optional[float]): subsea depth to the bottom of the completion interval. 'DBOT' in Nexus
        perm_thickness_ovr (Optional[float]): permeability thickness override value to use for the completion interval.\
            'KH' in Nexus.
        dfactor (Optional[float]): non-darcy factor to use for rate dependent skin calculations. 'D' in Nexus
        rel_perm_method (Optional[int]): rel perm method to use for the completion. 'IRELPM' in Nexus
        status (Optional[str]): the status of the layer, can be 'ON' or 'OFF'
        peaceman_well_block_radius (Optional[float]): The pressure equivalent radius of the grid block
    """

    __date: str
    __i: Optional[int] = None
    __j: Optional[int] = None
    __k: Optional[int] = None
    __skin: Optional[float] = None
    __depth: Optional[float] = None
    __well_radius: Optional[float] = None
    __x: Optional[float] = None
    __y: Optional[float] = None
    __angle_a: Optional[float] = None
    __angle_v: Optional[float] = None
    __grid: Optional[str] = None
    __depth_to_top: Optional[float] = None
    __depth_to_bottom: Optional[float] = None
    __perm_thickness_ovr: Optional[float] = None
    __dfactor: Optional[float] = None
    __rel_perm_method: Optional[int] = None
    __status: Optional[str] = None
    __iso_date: Optional[ISODateTime] = None
    _date_format: Optional[DateFormatEnum.DateFormat] = None
    __start_date: Optional[str] = None
    __unit_system: Optional[UnitSystem] = None
    __peaceman_well_block_radius: Optional[float] = None

    def __init__(self, date: str, i: Optional[int] = None, j: Optional[int] = None, k: Optional[int] = None,
                 skin: Optional[float] = None, depth: Optional[float] = None, well_radius: Optional[float] = None,
                 x: Optional[float] = None, y: Optional[float] = None, angle_a: Optional[float] = None,
                 angle_v: Optional[float] = None, grid: Optional[str] = None, depth_to_top: Optional[float] = None,
                 depth_to_bottom: Optional[float] = None, perm_thickness_ovr: Optional[float] = None,
                 dfactor: Optional[float] = None, rel_perm_method: Optional[int] = None,
                 status: Optional[str] = None, date_format: Optional[DateFormatEnum.DateFormat] = None,
                 peaceman_well_block_radius: Optional[float] = None, start_date: Optional[str] = None,
                 unit_system: Optional[UnitSystem] = None) -> None:
        """Initialises the Completion class.

        Args:
            date: (str): The starting date of the completion.
            i: (Optional[int]): The structured grid cell location in the x direction.
            j: (Optional[int]): The structured grid cell location in the y direction.
            k: Optional[int]: The structured grid cell location in the z direction.
            skin: Optional[float]: The skin value for the completion.
            depth: Optional[float]: The depth of the completion.
            well_radius: Optional[float]: The well radius.
            x: Optional[float]: The x location of the well in distance units/coordinates.
            y: Optional[float]: The y location of the well in distance units/coordinates.
            angle_a: Optional[float]: the angle relative to the local I axis.
            angle_v: Optional[float]: the angle relative to the true vertical axis (global Z axis).
            grid: Optional[str]: the grid name to which the completion data applies.
            depth_to_top: Optional[float]: depth to the top of a completion interval.
            depth_to_bottom: Optional[float]: depth to the bottom of the completion interval.
            perm_thickness_ovr: Optional[float]: permeability thickness override value to use for the
            completion interval.
            dfactor: Optional[float]: non-darcy factor to use for rate dependent skin calculations.
            rel_perm_method: Optional[int]: rel perm method to use for the completion.
            status: Optional[str]: the status of the layer, can be 'ON' or 'OFF'
            date_format: Optional[DateFormatEnum.DateFormat]: The date format to use for the date as an enum.
            peaceman_well_block_radius: Optional[float]: The pressure equivalent radius of the grid block
            start_date: Optional[str]: The start date of the simulation.
            unit_system: Optional[UnitSystem]: The unit system to use for the completion.
        """
        super().__init__({})
        self._date_format = date_format
        self.__well_radius = well_radius
        self.__date = date
        self.__i = i
        self.__j = j
        self.__k = k
        self.__skin = skin
        self.__depth = depth
        self.__x = x
        self.__y = y
        self.__angle_a = angle_a
        self.__angle_v = angle_v
        self.__grid = grid
        self.__depth_to_top = depth_to_top
        self.__depth_to_bottom = depth_to_bottom
        self.__perm_thickness_ovr = perm_thickness_ovr
        self.__dfactor = dfactor
        self.__rel_perm_method = rel_perm_method
        self.__status = status
        self.__start_date = start_date
        self.__iso_date = self.set_iso_date()
        self.__unit_system = unit_system
        self.__peaceman_well_block_radius = peaceman_well_block_radius

    @property
    def well_radius(self):
        return self.__well_radius

    @property
    def date(self):
        return self.__date

    @property
    def iso_date(self):
        return self.__iso_date

    @property
    def i(self):
        return self.__i

    @property
    def j(self):
        return self.__j

    @property
    def k(self):
        return self.__k

    @property
    def skin(self):
        return self.__skin

    @property
    def depth(self):
        return self.__depth

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

    @property
    def angle_a(self):
        return self.__angle_a

    @property
    def angle_v(self):
        return self.__angle_v

    @property
    def grid(self):
        return self.__grid

    @property
    def depth_to_top(self):
        return self.__depth_to_top

    @property
    def depth_to_bottom(self):
        return self.__depth_to_bottom

    @property
    def perm_thickness_ovr(self):
        return self.__perm_thickness_ovr

    @property
    def dfactor(self):
        return self.__dfactor

    @property
    def rel_perm_method(self):
        return self.__rel_perm_method

    @property
    def status(self):
        return self.__status

    @property
    def peaceman_well_block_radius(self) -> Optional[float]:
        """The Peaceman Well Block Radius for the completion."""
        return self.__peaceman_well_block_radius

    @property
    def date_format(self):
        return self._date_format

    @property
    def start_date(self):
        return self.__start_date

    def set_iso_date(self) -> ISODateTime:
        return ISODateTime.convert_to_iso(self.date, self.date_format, self.start_date)

    @property
    def unit_system(self):
        return self.__unit_system

    @property
    def units(self) -> CompletionUnits:
        return CompletionUnits(self.unit_system)

    @property
    def completion_is_shutin(self) -> bool:
        """Determines if the supplied completion is a shut-in or not."""
        return not self.completion_is_perforation

    @property
    def perforations(self) -> Sequence[Completion]:
        """Returns a list of all of the perforations for the well."""
        raise NotImplementedError("This method has not been implemented for this simulator yet")

    @property
    def first_perforation(self) -> Optional[Completion]:
        """Returns the first perforation for the well."""
        raise NotImplementedError("This method has not been implemented for this simulator yet")

    @property
    def shutins(self) -> Sequence[Completion]:
        """Returns a list of all of the perforations for the well."""
        raise NotImplementedError("This method has not been implemented for this simulator yet")

    @property
    def last_shutin(self) -> Optional[Completion]:
        """Returns the first perforation for the well."""
        raise NotImplementedError("This method has not been implemented for this simulator yet")

    @property
    @abstractmethod
    def completion_is_perforation(self) -> bool:
        """Determines if the supplied completion is a perforation or not."""
        raise NotImplementedError("Implement this in the derived class")
