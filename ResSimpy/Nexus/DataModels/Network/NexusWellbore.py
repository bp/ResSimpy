"""Class representing a single Wellbore in a Nexus Network."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

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

    def __init__(self, properties_dict: dict[str, None | int | str | float]) -> None:
        """Initialises the NexusWellbore class.

        Args:
            properties_dict (dict): dict of the properties to set on the object.
        """
        # call the init of the DataObjectMixin
        super(Wellbore, self).__init__({})
        for key, prop in properties_dict.items():
            self.__setattr__(key, prop)

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
