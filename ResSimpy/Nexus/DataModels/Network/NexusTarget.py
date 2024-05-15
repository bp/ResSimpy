"""Class that represents a single nexus target in the NexusSimulator."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.Target import Target


@dataclass(kw_only=True, repr=False)
class NexusTarget(Target):
    """Class that represents a single nexus target in the NexusSimulator."""
    def __init__(self, properties_dict: dict[str, None | int | str | float], date: Optional[str] = None,
                 date_format: Optional[DateFormat] = None, start_date: Optional[str] = None,
                 unit_system: Optional[UnitSystem] = None) -> None:
        """Initialises the NexusTarget class.

        Args:
            properties_dict (dict): A dictionary of properties to set on the object.
        """
        protected_attributes = ['date', 'date_format', 'start_date', 'unit_system']
        super().__init__()

        self._date_format = date_format
        self._start_date = start_date
        self._date = date
        self._unit_system = unit_system

        # Loop through the properties dict if one is provided and set those attributes
        for key, prop in properties_dict.items():
            if key in protected_attributes:
                key = '_' + key
            self.__setattr__(key, prop)

    @staticmethod
    def get_keyword_mapping() -> dict[str, tuple[str, type]]:
        """Gets the mapping of nexus keywords to attribute definitions."""
        keywords = {
            'NAME': ('name', str),
            'CTRL': ('control_quantity', str),
            'CTRLCOND': ('control_conditions', str),
            'CTRLCONS': ('control_connections', str),
            'CTRLMETHOD': ('control_method', str),
            'CALCMETHOD': ('calculation_method', str),
            'CALCCOND': ('calculation_conditions', str),
            'CALCCONS': ('calculation_connections', str),
            'VALUE': ('value', float),
            'ADDVALUE': ('add_value', float),
            'REGION': ('region', str),
            'PRIORITY': ('priority', int),
            'QMIN': ('minimum_rate', float),
            'QMIN_NOSHUT': ('minimum_rate_no_shut', float),
            'QGUIDE': ('guide_rate', str),
            'MAXDPDT': ('max_change_pressure', float),
            'RANKDT': ('rank_dt', float),
            'CTRLTYPE': ('control_type', str),
            'CALCTYPE': ('calculation_type', str)
            }
        return keywords

    def update(self, new_data: dict[str, None | int | str | float | UnitSystem], nones_overwrite: bool = False) -> None:
        """Updates attributes in the object based on the dictionary provided."""
        for k, v in new_data.items():
            if v is not None or nones_overwrite:
                setattr(self, k, v)
