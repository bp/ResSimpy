"""Class for handling the mapping between unit systems and the units used for that unit system."""
from abc import ABC
from dataclasses import dataclass

from ResSimpy.Enums.UnitsEnum import UnitSystem


@dataclass
class UnitDimension(ABC):
    """Class for handling the mapping between unit systems and the units used for that unit system."""
    english = None
    metric = None
    lab = None
    metkgcm2 = None
    metbar = None
    metric_atm = None

    def unit_system_enum_to_variable(self, unit_system: UnitSystem) -> str:
        """Returns the unit variable for the given unit system."""
        match unit_system:
            case UnitSystem.ENGLISH:
                return self.english
            case UnitSystem.LAB:
                return self.lab
            case UnitSystem.METRIC:
                return self.metric
            case UnitSystem.METKGCM2:
                return self.metkgcm2
            case UnitSystem.METBAR:
                return self.metbar
            case UnitSystem.METRIC_ATM:
                return self.metric_atm
            case _:
                raise ValueError(f'Unit system {unit_system} not recognised.')


class Area(UnitDimension):
    english = 'ft2'
    metric = 'm2'
    lab = 'cm2'
    metkgcm2 = 'm2'
    metbar = 'm2'
    metric_atm = 'm2'
