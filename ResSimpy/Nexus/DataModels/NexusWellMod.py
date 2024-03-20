"""Data structure for holding wellmod data for the NexusWell class."""
from dataclasses import dataclass

from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Utils.generic_repr import generic_repr, generic_str
from ResSimpy.Utils.to_dict_generic import to_dict


@dataclass(kw_only=True)
class NexusWellMod:
    """Data structure for holding wellmod data for the NexusWell class."""

    well_name: str
    date: str
    unit_system: UnitSystem | None = None
    partial_perf: float | list[float] | None = None
    permeability_thickness: float | list[float] | None = None
    skin: float | list[float] | None = None
    well_radius: float | list[float] | None = None
    polymer_well_radius: float | list[float] | None = None
    polymer_block_radius: float | list[float] | None = None
    well_indices: float | list[float] | None = None
    rel_perm_method: int | None | list[int] = None
    delta_perm_thickness_ovr: float | list[float] | None = None
    delta_swr: float | list[float] | None = None
    delta_sgr: float | list[float] | None = None
    delta_krw: float | list[float] | None = None
    delta_krg: float | list[float] | None = None
    perm_thickness_mult: float | list[float] | None = None

    def __init__(self, wellmod_dict: dict[str, None | str | float | int | list[float]]) -> None:
        """Initialises the NexusWellMod class.

        Args:
            wellmod_dict (dict[str, None | str | float | int | list[float]]): Dictionary of wellmod properties.
        """
        for key, prop in wellmod_dict.items():
            self.__setattr__(key, prop)

    def __repr__(self) -> str:
        return generic_repr(self)

    def __str__(self) -> str:
        return generic_str(self)

    def to_dict(self, keys_in_nexus_style: bool = False, add_date: bool = True, add_units: bool = True,
                include_nones: bool = True) -> dict[str, str | float | int | None]:
        """Returns a dictionary representation of the wellmod."""
        return to_dict(nexus_object=self, keys_in_nexus_style=keys_in_nexus_style, add_date=add_date,
                       add_units=add_units, include_nones=include_nones)

    @staticmethod
    def get_keyword_mapping() -> dict[str, tuple[str, type]]:
        """Returns a dictionary mapping the keywords to the names of the attributes."""
        keyword_mapping = {
            'KH': ('permeability_thickness', float),
            'SKIN': ('skin', float),
            'RADW': ('well_radius', float),
            'RADWP': ('polymer_well_radius', float),
            'RADBP': ('polymer_block_radius', float),
            'WI': ('well_indices', float),
            'PPERF': ('partial_perf', float),
            'IRELPM': ('rel_perm_method', int),
            'DKH': ('delta_perm_thickness_ovr', float),
            'DSWR': ('delta_swr', float),
            'DSGR': ('delta_sgr', float),
            'DKRW': ('delta_krw', float),
            'DKRG': ('delta_krg', float),
            'KHMULT': ('perm_thickness_mult', float),
        }
        return keyword_mapping
