"""Abstract base class for network objects."""
from __future__ import annotations

import warnings
from abc import ABC
from dataclasses import dataclass
from typing import Optional

from ResSimpy.DataModelBaseClasses.DataObjectMixin import DataObjectMixin
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat


@dataclass(kw_only=True)
class NetworkObject(DataObjectMixin, ABC):
    """Abstract base class for the object that form part of the surface network."""

    def __init__(self, properties_dict: Optional[dict[str, None | int | str | float]] = None,
                 date: Optional[str] = None, date_format: Optional[DateFormat] = None, start_date: Optional[str] = None,
                 unit_system: Optional[UnitSystem] = None, name: Optional[str] = None) -> None:
        """Initialises the NetworkObject class."""

        if properties_dict is None:
            properties_dict = {}

        if name is not None:
            obj_name = name
        else:
            dict_obj_name = properties_dict.get('name', None)
            if isinstance(dict_obj_name, str):
                obj_name = dict_obj_name
            else:
                obj_name = None

        if date is None:
            if 'date' not in properties_dict or not isinstance(properties_dict['date'], str):
                raise ValueError(f"No valid Date found for object with properties: {properties_dict}")
            date = properties_dict['date']

        if start_date is None:
            if 'start_date' in properties_dict:
                obj_start_date = properties_dict['start_date']
                start_date = obj_start_date if isinstance(obj_start_date, str) else None

        if date_format is None:
            if 'date_format' in properties_dict and isinstance(properties_dict['date_format'], DateFormat):
                date_format = properties_dict['date_format']
            else:
                raise ValueError("No date format supplied for object.")

        if unit_system is None:
            if 'unit_system' in properties_dict and isinstance(properties_dict['unit_system'], UnitSystem):
                unit_system = properties_dict['unit_system']
            else:
                # TODO: Update our unit tests with unit systems and upgrade the below to an error
                if 'Nexus' in self.__class__.__name__:
                    unit_system = UnitSystem.ENGLISH
                warnings.warn(f"No unit system supplied for object: {self.name}, assuming Simulator default of "
                              f"{unit_system}.")

        super().__init__(date_format=date_format, start_date=start_date, unit_system=unit_system, name=obj_name,
                         date=date)

        # Set attributes in the provided dict, excluding the ones already set.
        protected_attributes = ['date_format', 'start_date', 'unit_system', 'name']
        remaining_properties = [x for x in properties_dict.keys() if x not in protected_attributes]
        for key in remaining_properties:
            self.__setattr__(key, properties_dict[key])
