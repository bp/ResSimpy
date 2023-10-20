"""Class for handling targets in the Nexus Network. This class is used to store and manipulate the targets in a
NexusNetwork. It is stored as an instance in the NexusNetwork class as "targets".
"""
from __future__ import annotations
from dataclasses import dataclass, field
from uuid import UUID
from typing import Sequence, Optional, TYPE_CHECKING

import pandas as pd

from ResSimpy.File import File
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
class NexusTargets(Targets):
    """Class for handling targets in the Nexus Network. This class is used to store and manipulate the targets in a
    NexusNetwork. It is stored as an instance in the NexusNetwork class as "targets".
    """
    __targets: list[NexusTarget] = field(default_factory=list)

    def __init__(self, parent_network: NexusNetwork) -> None:
        self.__parent_network: NexusNetwork = parent_network
        self.__targets: list[NexusTarget] = []
        self.__add_object_operations = AddObjectOperations(None, self.table_header,
                                                           self.table_footer, self.__parent_network.model)
        self.__remove_object_operations = RemoveObjectOperations(self.__parent_network, self.table_header,
                                                                 self.table_footer)
        self.__modify_object_operations = ModifyObjectOperations(self)

    @property
    def table_header(self) -> str:
        """Start of the target definition table."""
        return 'TARGET'

    @property
    def table_footer(self) -> str:
        """End of the target definition table."""
        return 'ENDTARGET'

    def get_all(self) -> Sequence[NexusTarget]:
        """Returns a list of targets loaded from the simulator."""
        self.__parent_network.get_load_status()
        return self.__targets

    def get_by_name(self, target_name: str) -> Optional[NexusTarget]:
        """Returns a single target with the provided name loaded from the simulator.

        Args:
        ----
            target_name (str): name of the requested node

        Returns:
        -------
            NexusTarget: which has the same name as the requested target_name

        """
        targets_to_return = filter(lambda x: False if x.name is None else x.name.upper() == target_name.upper(),
                                   self.__targets)
        return next(targets_to_return, None)

    def get_df(self) -> pd.DataFrame:
        """Creates a dataframe representing all processed target data in a surface file
        Returns:
            DataFrame: of the properties of the targets through time with each row representing a target.
        """
        df_store = obj_to_dataframe(self.__targets)
        return df_store

    def get_overview(self) -> str:
        raise NotImplementedError('To be implemented')

    def load(self, surface_file: File, start_date: str, default_units: UnitSystem) -> None:
        """Calls load target and appends the list of discovered nodes into the NexusTargets object.

        Args:
            surface_file (File): NexusFile representation of the surface file.
            start_date (str): Starting date of the run
            default_units (UnitSystem): Units used in case not specified by surface file.

        Raises:
            TypeError: if the unit system found in the property check is not a valid enum UnitSystem.

        """
        new_targets = collect_all_tables_to_objects(surface_file, {'TARGET': NexusTarget},
                                                    start_date=start_date,
                                                    default_units=default_units)
        cons_list = new_targets.get('TARGET')
        if isinstance(cons_list, dict):
            raise ValueError('Incompatible data format for additional wells. Expected type "list" instead got "dict"')
        self._add_to_memory(cons_list)

    def _add_to_memory(self, additional_list: Optional[list[NexusTarget]]) -> None:
        """Extends the targets object by a list of targets provided to it.

        Args:
        ----
            additional_list (Sequence[NexusTarget]): list of nexus targets to add to the targets list.

        Returns:
        -------
            None
        """
        if additional_list is None:
            return
        self.__targets.extend(additional_list)

    def remove(self, target_to_remove: dict[str, None | str | float | int] | UUID) -> None:
        """Remove a node from the network based on the properties matching a dictionary or id.

        Args:
            target_to_remove (UUID | dict[str, None | str | float | int]): UUID of the node to remove or a dictionary \
            with sufficient matching parameters to uniquely identify a node

        """
        self.__remove_object_operations.remove_object_from_network_main(
            target_to_remove, self._network_element_name, self.__targets)

    def add(self, target_to_add: dict[str, None | str | float | int]) -> None:
        """Adds a target to a network, taking a dictionary with properties for the new node.

        Args:
            target_to_add (dict[str, None | str | float | int]):
            dictionary taking all the properties for the new target.
            Requires date and a target name.
        """
        new_object = self.__add_object_operations.add_network_obj(target_to_add, NexusTarget,  self.__parent_network)
        self._add_to_memory([new_object])

    def modify(self, target_to_modify: dict[str, None | str | float | int],
               new_properties: dict[str, None | str | float | int]) -> None:
        """Modifies an existing node based on a matching dictionary of properties (partial matches allowed if precisely
         1 matching node is found). Updates the properties with properties in the new_properties dictionary.

        Args:
            target_to_modify (dict[str, None | str | float | int]): dictionary containing attributes to match in the
            existing node set.
            new_properties (dict[str, None | str | float | int]): properties to switch to in the new node
        """
        self.__parent_network.get_load_status()

        self.__modify_object_operations.modify_network_object(target_to_modify, new_properties,
                                                              self.__parent_network)
