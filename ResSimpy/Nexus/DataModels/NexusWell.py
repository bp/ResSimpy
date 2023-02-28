from dataclasses import dataclass

from ResSimpy.Nexus.DataModels.NexusCompletion import NexusCompletion
from ResSimpy.Nexus.NexusEnums.UnitsEnum import Units
from ResSimpy.Well import Well


@dataclass
class NexusWell(Well):

    def __init__(self, well_name: str, completions: list[NexusCompletion], units: Units):
        super().__init__(well_name=well_name, completions=completions, units=units)
