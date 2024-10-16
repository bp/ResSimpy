"""The abstract base class for all simulators."""
from __future__ import annotations
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass

from ResSimpy.DataModelBaseClasses.Aquifer import Aquifer
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.DataModelBaseClasses.Equilibration import Equilibration
from ResSimpy.FileOperations.File import File
from ResSimpy.DataModelBaseClasses.Gaslift import Gaslift
from ResSimpy.DataModelBaseClasses.Grid import Grid
from ResSimpy.GenericContainerClasses.Hydraulics import Hydraulics
from ResSimpy.DataModelBaseClasses.Network import Network
from ResSimpy.DataModelBaseClasses.PVT import PVT
from ResSimpy.DataModelBaseClasses.RelPerm import RelPerm
from ResSimpy.DataModelBaseClasses.Reporting import Reporting
from ResSimpy.DataModelBaseClasses.Rock import Rock
from ResSimpy.DataModelBaseClasses.Separator import Separator
from ResSimpy.DataModelBaseClasses.Valve import Valve
from ResSimpy.DataModelBaseClasses.Water import Water
from ResSimpy.GenericContainerClasses.Wells import Wells


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
    _reporting: Reporting

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
        """Returns the start date of the model as a string."""
        return self._start_date

    @start_date.setter
    def start_date(self, value: str) -> None:
        self._start_date = value

    @property
    def wells(self) -> Wells:
        """Returns an instance of wells."""
        return self._wells

    @property
    def pvt(self) -> PVT:
        """Returns inputs of pvt (production validation testing)."""
        return self._pvt

    @property
    def separator(self) -> Separator:
        """Returns an instance of separator property."""
        return self._separator

    @property
    def water(self) -> Water:
        """Returns an instance of water property."""
        return self._water

    @property
    def equil(self) -> Equilibration:
        """Returns an instance of equilibration."""
        return self._equil

    @property
    def rock(self) -> Rock:
        """Returns an instance of rock property."""
        return self._rock

    @property
    def relperm(self) -> RelPerm:
        """Returns an instance of relative permeability."""
        return self._relperm

    @property
    def valve(self) -> Valve:
        """Returns an instance of valve property."""
        return self._valve

    @property
    def aquifer(self) -> Aquifer:
        """Returns an instance of aquifer."""
        return self._aquifer

    @property
    def hydraulics(self) -> Hydraulics:
        """Returns an instance of hydraulics."""
        return self._hydraulics

    @property
    def gaslift(self) -> Gaslift:
        """Returns an instance of gas lift property."""
        return self._gaslift

    @property
    def network(self) -> Network:
        """Returns an instance of network."""
        return self._network

    @property
    def default_units(self) -> UnitSystem:
        """Returns the default units to use if no units are found."""
        return self._default_units

    @staticmethod
    @abstractmethod
    def sim_default_unit_system() -> UnitSystem:
        """Returns the default unit system used by the Simulator."""
        raise NotImplementedError("This method has not been implemented for this simulator yet")

    @property
    def grid(self) -> None | Grid:
        """Pass the grid information to the front end."""
        return self._grid

    @property
    def origin(self) -> str:
        """Returns an instance of origin as a string."""
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
        """Returns model file of this instance."""

        return self._model_files

    """ Class Methods """

    @staticmethod
    @abstractmethod
    def get_fluid_type(surface_file_content: list[str]) -> str:
        """Returns the fluid type.

        Args:
            surface_file_content(list[str]): Reads the file content of surface with each line as a new entry in the list
        """
        raise NotImplementedError("This method has not been implemented for this simulator yet")

    @abstractmethod
    def set_output_path(self, path: str) -> None:
        """Initialise the output to the declared path (output location).

        Args:
            path(str): Declared location of the path.
        """
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
        new_model_name (str): The name for the model that will be created.
        """
        raise NotImplementedError("Implement this method on the derived class")
