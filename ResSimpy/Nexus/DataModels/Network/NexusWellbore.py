from dataclasses import dataclass
from typing import Optional

import ResSimpy.Utils.to_dict_generic as to_dict_generic
from ResSimpy.Utils.generic_repr import generic_repr
from ResSimpy.Wellbore import Wellbore


@dataclass(kw_only=True)
class NexusWellbore(Wellbore):
    """Attributes
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
        for key, prop in properties_dict.items():
            self.__setattr__(key, prop)

    @staticmethod
    def get_nexus_mapping() -> dict[str, tuple[str, type]]:
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

    def to_dict(self, keys_in_nexus_style: bool = False) -> dict[str, None | str | int | float]:
        """Returns a dictionary of the attributes of the wellbore.

        Args:
            keys_in_nexus_style (bool): if True returns the key values in Nexus keywords, otherwise returns the \
                attribute name as stored by ressimpy.

        Returns:
            a dictionary keyed by attributes and values as the value of the attribute
        """
        result_dict = to_dict_generic.to_dict(self, keys_in_nexus_style, add_date=True, add_units=True)
        return result_dict

    def __repr__(self) -> str:
        return generic_repr(self)
