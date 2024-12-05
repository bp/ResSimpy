from dataclasses import dataclass

from ResSimpy.OpenGoSim.DataModels.OpenGoSimWell import OpenGoSimWell
from ResSimpy.GenericContainerClasses.Wells import Wells


@dataclass(kw_only=True, init=False)
class OpenGoSimWells(Wells):
    """A class for collecting all OpenGoSimWell objects in an OpenGoSimSimulator.

    Handles adding and removing completions as well as rescheduling wells. This is usually accessed through the
    model.wells property.
    """
    _wells: list[OpenGoSimWell]
