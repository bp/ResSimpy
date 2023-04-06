from dataclasses import dataclass
from typing import Optional

from ResSimpy.Constraint import Constraint


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

    def __init__(self, properties_dict: dict[str, None | int | str | float]):
        super().__init__()
        for key, prop in properties_dict.items():
            self.__setattr__(key, prop)
