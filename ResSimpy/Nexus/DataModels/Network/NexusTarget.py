from __future__ import annotations
from dataclasses import dataclass
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Target import Target
from ResSimpy.Utils.generic_repr import generic_repr


@dataclass(kw_only=True)
class NexusTarget(Target):

    def __init__(self, properties_dict: dict[str, None | int | str | float]) -> None:
        super().__init__()
        for key, prop in properties_dict.items():
            self.__setattr__(key, prop)

    def __repr__(self) -> str:
        return generic_repr(self)

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
            'QGUIDE': ('guide_rate', float),
            'MAXDPDT': ('max_change_pressure', float),
            'RANKDT': ('rank_dt', float),
            'CTRLTYPE': ('control_type', str),
            'CALCTYPE': ('calculation_type', str)
            }
        return keywords

    def update(self, new_data: dict[str, None | int | str | float | UnitSystem], nones_overwrite: bool = False):
        """Updates attributes in the object based on the dictionary provided."""
        for k, v in new_data.items():
            if v is not None or nones_overwrite:
                setattr(self, k, v)
