"""Class for handling targets in the Nexus Network. This class is used to store and manipulate the targets in a
NexusNetwork. It is stored as an instance in the NexusNetwork class as "targets".
"""
from __future__ import annotations
from dataclasses import dataclass, field
from uuid import UUID
from typing import Sequence, Optional, TYPE_CHECKING

import pandas as pd

from ResSimpy.File import File
from ResSimpy.Nexus.DataModels.Network.NexusProc import NexusProc
from ResSimpy.Nexus.nexus_add_new_object_to_file import AddObjectOperations
from ResSimpy.Nexus.nexus_collect_tables import collect_all_tables_to_objects
from ResSimpy.Nexus.DataModels.Network.NexusTarget import NexusTarget
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.nexus_modify_object_in_file import ModifyObjectOperations
from ResSimpy.Nexus.nexus_remove_object_from_file import RemoveObjectOperations
from ResSimpy.Targets import Targets
from ResSimpy.Utils.obj_to_dataframe import obj_to_dataframe

if TYPE_CHECKING:
    from ResSimpy.Nexus.NexusNetwork import NexusNetwork


@dataclass(kw_only=True)
class NexusProcs():
    """Class for handling procedures in the Nexus Network. This class is used to store and collect information about
    certain procedures written in the Nexus surface file.
    """
    #need field function to make a new unique empty list
    __procs: list[NexusProc] = field(default_factory=list)

    def __init__(self, parent_network: NexusNetwork) -> None:
        self.__parent_network: NexusNetwork = parent_network
        self.__procs = [] #list[NexusProc] = field(default_factory=list)

    def get_all(self) -> Sequence[NexusProc]:
        """Returns a list of procs loaded from the simulator."""
        self.__parent_network.get_load_status()
        return self.__procs

    def _add_to_memory(self, procs_to_add: list[NexusProc]) -> None:
        """Adds the list of Nexus procedure objects to memory"""
        self.__procs.extend(procs_to_add)
        print(len(self.__procs))
