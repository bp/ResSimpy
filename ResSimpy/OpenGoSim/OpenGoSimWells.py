from dataclasses import dataclass

from ResSimpy.Wells import Wells


@dataclass(kw_only=True)
class OpenGoSimWells(Wells):
    """A class for collecting all OpenGoSimWell objects in an OpenGoSimSimulator. Handles adding and removing
    completions as well as rescheduling wells. This is usually accessed through the model.wells property.
    """
    pass
