"""The base class for all Well Completions"""
from abc import ABC
from dataclasses import dataclass
from typing import Optional


@dataclass(kw_only=True)
class Completion(ABC):
    """
    A class representing well completions.
    IMPORTANT: if modifying this class, make sure to update the relevant tests in test_load_wells, as well as updating
    the constructor calls in the derived classes.
    well_radius: The well radius. 'RADW' in Nexus
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

    def __init__(self, date: str, i: Optional[int] = None, j: Optional[int] = None, k: Optional[int] = None,
                 skin: Optional[float] = None, depth: Optional[float] = None, well_radius: Optional[float] = None,
                 x: Optional[float] = None, y: Optional[float] = None, angle_a: Optional[float] = None,
                 angle_v: Optional[float] = None, grid: Optional[str] = None, depth_to_top: Optional[float] = None,
                 depth_to_bottom: Optional[float] = None):
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

    @property
    def well_radius(self):
        return self.__well_radius

    @property
    def date(self):
        return self.__date

    @property
    def i(self):
        return self.__i

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

    def to_dict(self) -> dict[str, None | float | int | str]:
        attribute_dict = {
            'well_radius': self.__well_radius,
            'date': self.__date,
            'i': self.__i,
            'j': self.__j,
            'k': self.__k,
            'skin': self.__skin,
            'depth': self.__depth,
            'x': self.__x,
            'y': self.__y,
            'angle_a': self.__angle_a,
            'angle_v': self.__angle_v,
            'grid': self.__grid,
            'depth_to_top': self.__depth_to_top,
            'depth_to_bottom': self.__depth_to_bottom,
        }
        return attribute_dict
