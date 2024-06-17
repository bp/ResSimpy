"""Class representing a single Wellbore in a Nexus Network."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.Wellbore import Wellbore


@dataclass(kw_only=True)
class NexusWellbore(Wellbore):
    """Class representing a single Wellbore in a Nexus Network.

    Attributes:
        date (str): string representation of the last defined date
        unit_system (UnitSystem): unit system enum
        name (str): Name of the well. (WELL)
        flowsect (int): Number of the flow section. (FLOWSECT)
        diameter (float): Diameter of the well. (DIAM)
        inner_diameter (float): Inner diameter of the well. (INNERDIAM)
        roughness (float): Roughness of the well. (ROUGHNESS)
        bore_type (str): Type of well. (TYPE)
        hyd_method (str): hydraulic method. (METHOD)
        temperature (float): Temperature of the well. (TEMP)
        elevation_profile (str): Elevation profile of the well. (ELEVPR)
        temperature_profile (str): Temperature profile of the well. (TEMPPR)
        heat_transfer_coeff (float): Heat transfer coefficient of the well. (HTC)
        pvt_method (int): Method number used for PVT. (IPVT)
        water_method (int): Method number used for water. (IWAT).
    """

    flowsect: Optional[int] = None
    bore_type: Optional[str] = None
    hyd_method: Optional[str] = None
    temperature: Optional[float] = None
    elevation_profile: Optional[str] = None
    temperature_profile: Optional[str] = None
    heat_transfer_coeff: Optional[float] = None
    pvt_method: Optional[int] = None
    water_method: Optional[int] = None

    def __init__(self, properties_dict: dict[str, None | int | str | float], date: Optional[str] = None,
                 date_format: Optional[DateFormat] = None, start_date: Optional[str] = None,
                 unit_system: Optional[UnitSystem] = None) -> None:
        """Initialises the NexusWellbore class.

        Args:
            properties_dict (dict): dict of the properties to set on the object.
            date (Optional[str]): The date of the object.
            date_format (Optional[DateFormat]): The date format that the object uses.
            start_date (Optional[str]): The start date of the model. Required if the object uses a decimal TIME.
            unit_system (Optional[UnitSystem]): The unit system of the object e.g. ENGLISH, METRIC.
        """
        # call the init of the DataObjectMixin
        name = properties_dict.get('name', None)
        name = name if isinstance(name, str) else None
        super().__init__(_date_format=date_format, _start_date=start_date, _unit_system=unit_system, name=name)

        # Set the date related properties, then set the date, automatically setting the ISODate
        protected_attributes = ['date_format', 'start_date', 'unit_system']

        for attribute in protected_attributes:
            if attribute in properties_dict:
                self.__setattr__(f"_{attribute}", properties_dict[attribute])

        # Loop through the properties dict if one is provided and set those attributes
        remaining_properties = [x for x in properties_dict.keys() if x not in protected_attributes]
        for key in remaining_properties:
            self.__setattr__(key, properties_dict[key])

        if date is None:
            if 'date' not in properties_dict or not isinstance(properties_dict['date'], str):
                raise ValueError(f"No valid Date found for object with properties: {properties_dict}")
            self.date = properties_dict['date']
        else:
            self.date = date

    @staticmethod
    def get_keyword_mapping() -> dict[str, tuple[str, type]]:
        """Gets the mapping of nexus keywords to attribute definitions."""
        nexus_mapping = {
            'WELL': ('name', str),
            'FLOWSECT': ('flowsect', int),
            'DIAM': ('diameter', float),
            'INNERDIAM': ('inner_diameter', float),
            'ROUGHNESS': ('roughness', float),
            'TYPE': ('bore_type', str),
            'METHOD': ('hyd_method', str),
            'TEMP': ('temperature', float),
            'ELEVPR': ('elevation_profile', str),
            'TEMPPR': ('temperature_profile', str),
            'HTC': ('heat_transfer_coeff', float),
            'IPVT': ('pvt_method', int),
            'IWAT': ('water_method', int)
        }

        return nexus_mapping

    def __repr__(self) -> str:
        return super().__repr__()
