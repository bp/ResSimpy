from dataclasses import dataclass
from typing import Optional

from ResSimpy.Nexus.NexusEnums.UnitsEnum import UnitSystem
import ResSimpy.Utils.to_dict_generic as to_dict_generic


@dataclass(kw_only=True)
class NexusWellhead:

    def __init__(self, properties_dict: dict[str, None | int | str | float]):
        for key, prop in properties_dict.items():
            self.__setattr__(key, prop)

    @staticmethod
    def get_nexus_mapping() -> dict[str, tuple[str, type]]:
        """gets the mapping of nexus keywords to attribute definitions"""
        nexus_mapping = {
        }
        return nexus_mapping

    def to_dict(self, keys_in_nexus_style: bool = False) -> dict[str, None | str | int | float]:
        """ Returns a dictionary of the attributes of the well connection
        Args:
            keys_in_nexus_style (bool): if True returns the key values in Nexus keywords, otherwise returns the \
                attribute name as stored by ressimpy

        Returns:
            a dictionary keyed by attributes and values as the value of the attribute
        """
        result_dict = to_dict_generic.to_dict(self, keys_in_nexus_style, add_date=True, add_units=True)
        return result_dict
