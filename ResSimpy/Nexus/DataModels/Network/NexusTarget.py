"""Class that represents a single nexus target in the NexusSimulator."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.DataModelBaseClasses.Target import Target


@dataclass(kw_only=True, repr=False)
class NexusTarget(Target):
    """Class that represents a single nexus target in the NexusSimulator."""
    def __init__(self, properties_dict: None | dict[str, None | int | str | float] = None, date: Optional[str] = None,
                 date_format: Optional[DateFormat] = None, start_date: Optional[str] = None,
                 unit_system: Optional[UnitSystem] = None, name: Optional[str] = None,
                 control_quantity: None | str = None, control_conditions: None | str = None,
                    control_connections: None | str = None, control_method: None | str = None,
                    calculation_method: None | str = None, calculation_conditions: None | str = None,
                    calculation_connections: None | str = None, value: None | float = None,
                    add_value: None | float = None, region: None | str = None, priority: None | int = None,
                    minimum_rate: None | float = None, minimum_rate_no_shut: None | float = None,
                    guide_rate: None | str = None, max_change_pressure: None | float = None,
                    rank_dt: None | float = None, control_type: None | str = None,
                    calculation_type: None | str = None
                 ) -> None:
        """Initialises the NexusTarget class.

        Args:
            properties_dict (dict): dict of the properties to set on the object.
            date (Optional[str]): The date of the object.
            date_format (Optional[DateFormat]): The date format that the object uses.
            start_date (Optional[str]): The start date of the model. Required if the object uses a decimal TIME.
            unit_system (Optional[UnitSystem]): The unit system of the object e.g. ENGLISH, METRIC.
            name (Optional[str]): The name of the target.
        """
        super().__init__(date_format=date_format, start_date=start_date, unit_system=unit_system, name=name, date=date,
                         properties_dict=properties_dict, control_quantity=control_quantity,
                         control_conditions=control_conditions, control_connections=control_connections,
                         control_method=control_method,
                         calculation_method=calculation_method, calculation_conditions=calculation_conditions,
                         calculation_connections=calculation_connections, value=value, add_value=add_value,
                         region=region, priority=priority, minimum_rate=minimum_rate,
                         minimum_rate_no_shut=minimum_rate_no_shut, guide_rate=guide_rate,
                         max_change_pressure=max_change_pressure, rank_dt=rank_dt,
                         control_type=control_type, calculation_type=calculation_type)

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
