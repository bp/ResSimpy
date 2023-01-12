from dataclasses import dataclass

from ResSimpy.Nexus.DataModels import NexusCompletion
from ResSimpy.Well import Well


@dataclass
class NexusWell(Well):

    def __init__(self, well_name, completions):
        super().__init__(well_name, completions)
