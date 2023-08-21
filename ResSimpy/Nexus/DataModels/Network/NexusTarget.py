from __future__ import annotations
from dataclasses import dataclass
from ResSimpy.Target import Target
from ResSimpy.Utils import to_dict_generic
from ResSimpy.Utils.generic_repr import generic_repr
from ResSimpy.Utils.obj_to_table_string import to_table_line

@dataclass(kw_only=True)
class NexusTarget(Target):

    def __init__(self, properties_dict: dict[str, None | int | str | float]) -> None:
        super().__init__()
        for key, prop in properties_dict.items():
            self.__setattr__(key, prop)

    def __repr__(self) -> str:
        return generic_repr(self)

    @staticmethod
    def get_nexus_mapping() -> dict[str, tuple[str, type]]:
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

    def to_dict(self, keys_in_nexus_style: bool = False, include_nones: bool = True) -> \
            dict[str, None | str | int | float]:
        """Returns a dictionary of the attributes of the Node.

        Args:
            keys_in_nexus_style (bool): if True returns the key values in Nexus keywords, otherwise returns the \
                attribute name as stored by ressimpy.
            include_nones (bool): If False filters the nones out of the dictionary. Defaults to True

        Returns:
            a dictionary keyed by attributes and values as the value of the attribute
        """
        result_dict = to_dict_generic.to_dict(self, keys_in_nexus_style, add_date=True, add_units=True,
                                              include_nones=include_nones)
        return result_dict

    def to_table_line(self, headers: list[str]) -> str:
        """Returns the string representation of a row in a table for a given set of headers."""
        return to_table_line(self, headers)

    def update(self, input_dictionary:  dict[str, None | float | int | str]) -> None:
        """Updates a target based on a dictionary of attributes."""
        for k, v in input_dictionary.items():
            if v is None:
                continue
            if hasattr(self, '_NexusTarget__' + k):
                setattr(self, '_NexusTarget__' + k, v)
            elif hasattr(super(), '_Target__' + k):
                setattr(self, '_Target__' + k, v)