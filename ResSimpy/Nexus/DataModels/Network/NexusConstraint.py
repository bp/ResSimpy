from dataclasses import dataclass
from typing import Optional

from ResSimpy.Constraint import Constraint
from ResSimpy.Nexus.NexusEnums.UnitsEnum import UnitSystem
from ResSimpy.Utils import to_dict_generic
from ResSimpy.Utils.generic_repr import generic_repr


@dataclass
class NexusConstraint(Constraint):
    max_reverse_surface_oil_rate: Optional[float] = None
    max_reverse_surface_gas_rate: Optional[float] = None
    max_reverse_surface_water_rate: Optional[float] = None
    max_reverse_surface_liquid_rate: Optional[float] = None
    max_reverse_reservoir_oil_rate: Optional[float] = None
    max_reverse_reservoir_gas_rate: Optional[float] = None
    max_reverse_reservoir_water_rate: Optional[float] = None
    max_reverse_reservoir_liquid_rate: Optional[float] = None

    def __init__(self, properties_dict: dict[str, None | int | str | float | UnitSystem]):
        super().__init__()
        for key, prop in properties_dict.items():
            self.__setattr__(key, prop)

    @staticmethod
    def get_nexus_mapping() -> dict[str, tuple[str, type]]:
        """gets the mapping of nexus keywords to attribute definitions"""
        nexus_mapping = {
            'NAME': ('name', str),
            'QLIQSMAX': ('max_surface_liquid_rate', float),
            'QWSMAX': ('max_surface_water_rate', float),
            'QOSMAX': ('max_surface_oil_rate', float),
            'QGSMAX': ('max_surface_gas_rate', float),
            'QLIQSMAX-': ('max_reverse_surface_liquid_rate', float),
            'QWSMAX-': ('max_reverse_surface_water_rate', float),
            'QOSMAX-': ('max_reverse_surface_oil_rate', float),
            'QGSMAX-': ('max_reverse_surface_gas_rate', float),
        }
        return nexus_mapping

    def to_dict(self, keys_in_nexus_style: bool = False) -> dict[str, None | str | int | float]:
        """
            Returns a dictionary of the attributes of the Constraint
        Args:
            keys_in_nexus_style (bool): if True returns the key values in Nexus keywords, otherwise returns the \
                attribute name as stored by ressimpy

        Returns:
            a dictionary keyed by attributes and values as the value of the attribute
        """
        result_dict = to_dict_generic.to_dict(self, keys_in_nexus_style, add_date=True, add_units=True)
        return result_dict

    def update(self, new_data: dict[str, None | int | str | float | UnitSystem]):
        """Updates attributes in the object based on the dictionary provided"""
        for k, v in new_data.items():
            if v is not None:
                setattr(self, k, v)

    def __repr__(self):
        return generic_repr(self)
