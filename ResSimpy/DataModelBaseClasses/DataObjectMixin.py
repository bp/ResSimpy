"""Base class representing a data object in ResSimpy."""
from uuid import uuid4, UUID
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional

from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Time.ISODateTime import ISODateTime
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.Units.AttributeMappings.BaseUnitMapping import BaseUnitMapping
from ResSimpy.Utils import to_dict_generic
from ResSimpy.Utils.generic_repr import generic_repr, generic_str
from ResSimpy.Utils.obj_to_table_string import to_table_line


@dataclass(kw_only=True)
class DataObjectMixin(ABC):
    """Base class representing a data object in ResSimpy."""
    __id: UUID = field(default_factory=lambda: uuid4(), compare=False)
    __iso_date: ISODateTime = field(init=False, repr=True)
    _date_format: Optional[DateFormat] = None
    __date: Optional[str] = None
    _start_date: Optional[str] = None
    _unit_system: Optional[UnitSystem] = None
    __name: Optional[str] = None

    def __init__(self, date: Optional[str] = None, date_format: Optional[DateFormat] = None,
                 start_date: Optional[str] = None, unit_system: Optional[UnitSystem] = None,
                 name: Optional[str] = None) -> None:
        """Initialises the DataObjectMixin Class. First '_' parameter is a dummy parameter for type compatibility.

        Args:
            name (Optional[str]): The name of the object.
            date (Optional[str]): The date of the object.
            date_format (Optional[DateFormat]): The date format of the object.
            start_date (Optional[str]): The start date of the model (required if the date is in numerical format).
            unit_system (Optional[UnitSystem]): The unit system of the object.
        """
        self.__id = uuid4()
        self._date_format = date_format
        self._start_date = start_date
        self._unit_system = unit_system
        self.date = date
        self.__name = name

    def __repr__(self) -> str:
        return generic_repr(self)

    def __str__(self) -> str:
        return generic_str(self)

    @property
    def iso_date(self) -> ISODateTime:
        """The date of the object in ISO format."""
        if self.__iso_date is None:
            self.set_iso_date()
        return self.__iso_date

    @property
    def date(self) -> Optional[str]:
        """The date of the object as written in the source file."""
        return self.__date

    @date.setter
    def date(self, value: str) -> None:
        self.__date = value
        self.set_iso_date()

    @property
    def start_date(self) -> Optional[str]:
        """The start date of the model (required for Nexus objects using a decimal date format)."""
        return self._start_date

    @property
    def date_format(self) -> Optional[DateFormat]:
        """The date format of the date on the object."""
        return self._date_format

    @property
    def unit_system(self) -> Optional[UnitSystem]:
        """The unit system being used in the object."""
        return self._unit_system

    @property
    def name(self) -> Optional[str]:
        """The name of the object in the simulator."""
        return self.__name

    def set_iso_date(self) -> None:
        """Updates the ISO Date property."""
        if self.date is None:
            raise ValueError("Cannot set ISO Date without a date.")

        self.__iso_date = ISODateTime.convert_to_iso(self.date, self.date_format, self.start_date)

    def to_dict(self, keys_in_keyword_style: bool = False, add_date: bool = True, add_units: bool = True,
                add_iso_date: bool = False, include_nones: bool = True,
                units_as_string: bool = True) -> dict[str, None | str | int | float]:
        """Returns a dictionary of the attributes of the object.

        Args:
            keys_in_keyword_style (bool): if True returns the key values as simulator keywords, otherwise returns the \
                attribute name as stored by ressimpy.
            add_date (bool): if True adds the date to the dictionary
            add_iso_date (bool): adds an iso date attribute if it exists.
            add_units (bool): if True adds the units to the dictionary
            include_nones (bool): if True includes None values from the object in the dictionary.
            units_as_string (bool): If True, converts the object's units to a string value rather than an enum.

        Returns:
            a dictionary keyed by attributes and values as the value of the attribute
        """
        result_dict = to_dict_generic.to_dict(self, keys_in_keyword_style, add_date=add_date, add_units=add_units,
                                              add_iso_date=add_iso_date,
                                              include_nones=include_nones, units_as_string=units_as_string)
        return result_dict

    def to_table_line(self, headers: list[str]) -> str:
        """Takes a generic Nexus object and returns the attribute values as a string in the order of headers provided.

        Requires an implemented to_dict method and get_keyword_mapping() method.

        Args:
            headers (list[str]): list of header values in keyword format

        Returns:
            string of the values in the order of the headers provided.

        """
        return to_table_line(self, headers)

    @property
    def id(self) -> UUID:
        """Unique identifier for each object."""
        return self.__id

    @staticmethod
    @abstractmethod
    def get_keyword_mapping() -> dict[str, tuple[str, type]]:
        """Gets the mapping of keywords to attribute definitions."""
        raise NotImplementedError("Implement this in the derived class")

    @property
    @abstractmethod
    def units(self) -> BaseUnitMapping:
        """Returns the attribute to unit map for the data object."""
        raise NotImplementedError("Implement this in the derived class")

    def get_unit_for_attribute(self, attribute_name: str, uppercase: bool = False) -> str:
        """Returns the unit variable for the given unit system.

        Args:
            attribute_name (str): name of the attribute to get the unit for
            unit_system (UnitSystem): unit system to get the unit for
            uppercase (bool): if True returns the unit in uppercase
        """
        unit_dimension = self.units.attribute_map.get(attribute_name, None)
        if unit_dimension is None:
            raise AttributeError(f'Attribute {attribute_name} not recognised and does not have a unit definition')

        if self.unit_system is None:
            raise AttributeError("Cannot find unit without a unit system.")

        unit = unit_dimension.unit_system_enum_to_variable(unit_system=self.unit_system)
        if uppercase:
            unit = unit.upper()
        return unit
