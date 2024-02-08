"""The abstract base class for all simulators."""
from __future__ import annotations
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass

from ResSimpy.Aquifer import Aquifer
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Equilibration import Equilibration
from ResSimpy.File import File
from ResSimpy.Gaslift import Gaslift
from ResSimpy.Grid import Grid
from ResSimpy.Hydraulics import Hydraulics
from ResSimpy.Network import Network
from ResSimpy.PVT import PVT
from ResSimpy.RelPerm import RelPerm
from ResSimpy.Rock import Rock
from ResSimpy.Separator import Separator
from ResSimpy.Valve import Valve
from ResSimpy.Water import Water
from ResSimpy.Wells import Wells


@dataclass(kw_only=True, init=False)
class Simulator(ABC):
    _start_date: str
    _origin: str
    _wells: Wells
    _pvt: PVT
    _separator: Separator
    _water: Water
    _equil: Equilibration
    _rock: Rock
    _relperm: RelPerm
    _valve: Valve
    _aquifer: Aquifer
    _hydraulics: Hydraulics
    _gaslift: Gaslift
    _network: Network
    _grid: None | Grid
    _model_files: File
    _default_units: UnitSystem

    def __repr__(self) -> str:
        """Pretty printing Simulator data."""
        printable_str = f'Origin: {self.origin}\n'
        printable_str += f'Full path: {self.model_files.location}\n'
        printable_str += f'Start date: {self.start_date}\n'
        printable_str += f'Date format: {self.get_date_format()}\n'
        printable_str += f'Default units: {str(self.default_units)}\n'
        return printable_str

    """Class Properties"""

    @property
    def start_date(self) -> str:
        return self._start_date

    @start_date.setter
    def start_date(self, value) -> None:
        self._start_date = value

    @property
    def wells(self) -> Wells:
        return self._wells

    @property
    def pvt(self) -> PVT:
        return self._pvt

    @property
    def separator(self) -> Separator:
        return self._separator

    @property
    def water(self) -> Water:
        return self._water

    @property
    def equil(self) -> Equilibration:
        return self._equil

    @property
    def rock(self) -> Rock:
        return self._rock

    @property
    def relperm(self) -> RelPerm:
        return self._relperm

    @property
    def valve(self) -> Valve:
        return self._valve

    @property
    def aquifer(self) -> Aquifer:
        return self._aquifer

    @property
    def hydraulics(self) -> Hydraulics:
        return self._hydraulics

    @property
    def gaslift(self) -> Gaslift:
        return self._gaslift

    @property
    def network(self) -> Network:
        return self._network

    @property
    def default_units(self) -> UnitSystem:
        return self._default_units

    @property
    def grid(self) -> None | Grid:
        """Pass the grid information to the front end."""
        return self._grid

    @property
    def origin(self) -> str:
        return self._origin

    @origin.setter
    def origin(self, value: None | str) -> None:
        if value is None:
            raise ValueError(f'Origin path to model is required. Instead got {value}.')
        self._origin: str = value.strip()

    @property
    def model_location(self) -> str:
        """Returns the location of the model."""
        return os.path.dirname(self._origin)

    @property
    def model_files(self) -> File:
        return self._model_files

    """ Class Methods """

    @staticmethod
    @abstractmethod
    def get_fluid_type(surface_file_name: str) -> str:
        raise NotImplementedError("This method has not been implemented for this simulator yet")

    @abstractmethod
    def set_output_path(self, path: str) -> None:
        raise NotImplementedError("Implement this method on the derived class")

    @abstractmethod
    def get_date_format(self) -> str:
        """Returns date format as a string."""
        raise NotImplementedError("Implement this method on the derived class")

    @abstractmethod
    def write_out_new_model(self, new_location: str, new_model_name: str) -> None:
        """Writes out a new version of the model to the location supplied.

        Args:
        new_location (str): Path to write the contents of the model to.
        """
        raise NotImplementedError("Implement this method on the derived class")
