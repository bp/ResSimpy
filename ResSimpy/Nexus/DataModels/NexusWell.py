from dataclasses import dataclass

from ResSimpy.Nexus.DataModels.NexusCompletion import NexusCompletion
from ResSimpy.Nexus.NexusEnums.UnitsEnum import UnitSystem
from ResSimpy.Well import Well


@dataclass
class NexusWell(Well):

    def __init__(self, well_name: str, completions: list[NexusCompletion], units: UnitSystem):
        super().__init__(well_name=well_name, completions=completions, units=units)
