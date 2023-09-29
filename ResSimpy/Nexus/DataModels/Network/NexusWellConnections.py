"""Class for handling well connections in the Nexus Network. This class is used to store and manipulate the well
connections in a NexusNetwork. It is stored as an instance in the NexusNetwork class as "well_connections".
In Nexus this is the WELLS table.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING
from uuid import UUID

import pandas as pd

from ResSimpy.File import File
from ResSimpy.Nexus.nexus_add_new_object_to_file import AddObjectOperations
from ResSimpy.Nexus.nexus_modify_object_in_file import ModifyObjectOperations
from ResSimpy.Nexus.nexus_remove_object_from_file import RemoveObjectOperations
from ResSimpy.Utils.obj_to_dataframe import obj_to_dataframe
from ResSimpy.Nexus.DataModels.Network.NexusWellConnection import NexusWellConnection
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.nexus_collect_tables import collect_all_tables_to_objects
from ResSimpy.WellConnections import WellConnections

if TYPE_CHECKING:
    from ResSimpy.Nexus.NexusNetwork import NexusNetwork


@dataclass
class NexusWellConnections(WellConnections):
    """Class for handling well connections in the Nexus Network. This class is used to store and manipulate the well
    connections in a NexusNetwork. It is stored as an instance in the NexusNetwork class as "well_connections".
    In Nexus this is the WELLS table.
    """
    __well_connections: list[NexusWellConnection] = field(default_factory=list)

    def __init__(self, parent_network: NexusNetwork) -> None:
        self.__parent_network: NexusNetwork = parent_network
        self.__well_connections: list[NexusWellConnection] = []
        self.__add_object_operations = AddObjectOperations(NexusWellConnection, self.table_header, self.table_footer,
                                                           self.__parent_network.model)
        self.__remove_object_operations = RemoveObjectOperations(self.__parent_network, self.table_header,
                                                                 self.table_footer)
        self.__modify_object_operations = ModifyObjectOperations(self)

    def get_all(self) -> list[NexusWellConnection]:
        """Returns a list of well connections loaded from the simulator."""
        self.__parent_network.get_load_status()
        return self.__well_connections

    def get_by_name(self, name: str) -> Optional[NexusWellConnection]:
        """Returns a single well connection with the provided name loaded from the simulator.

        Args:
            name (str): name of the requested well connection

        Returns:
            NexusWellConnection: which has the same name as requested
        """
        self.__parent_network.get_load_status()
        to_return = filter(lambda x: False if x.name is None else x.name.upper() == name.upper(),
                           self.__well_connections)
        return next(to_return, None)

    def get_df(self) -> pd.DataFrame:
        """Creates a dataframe representing all processed well connections data in a surface file
        Returns:
            DataFrame: of the properties of the well connections through time with each row representing a single well \
            connection.
        """
        self.__parent_network.get_load_status()
        return obj_to_dataframe(self.__well_connections)

    def get_overview(self) -> str:
        raise NotImplementedError('To be implemented')

    def _add_to_memory(self, additional_list: Optional[list[NexusWellConnection]]) -> None:
        """Extends the nodes object by a list of connections provided to it.

        Args:
            additional_list (Sequence[NexusWellConnection]): list of nexus connections to add to the nodes list.
        """
        if additional_list is None:
            return
        self.__well_connections.extend(additional_list)

    def load(self, surface_file: File, start_date: str, default_units: UnitSystem) -> None:
        new_well_connections = collect_all_tables_to_objects(surface_file, {'WELLS': NexusWellConnection},
                                                             start_date=start_date,
                                                             default_units=default_units)
        cons_list = new_well_connections.get('WELLS')
        if isinstance(cons_list, dict):
            raise ValueError('Incompatible data format for additional wells. Expected type "list" instead got "dict"')
        self._add_to_memory(cons_list)

    def remove(self, obj_to_remove: dict[str, None | str | float | int] | UUID) -> None:
        """Remove a wellbore from the network based on the properties matching a dictionary or id.

        Args:
            obj_to_remove (UUID | dict[str, None | str | float | int]): UUID of the wellbore to remove or a dictionary \
            with sufficient matching parameters to uniquely identify a wellbore

        """
        self.__remove_object_operations.remove_object_from_network_main(
            obj_to_remove, self._network_element_name, self.__well_connections)

    def add(self, obj_to_remove: dict[str, None | str | float | int]) -> None:
        """Adds a well connection to a network, taking a dictionary with properties for the new well connection.

        Args:
            obj_to_remove (dict[str, None | str | float | int]): dictionary taking all the properties for the new
            well connection.
            Requires date and a name.
        """
        new_object = self.__add_object_operations.add_network_obj(obj_to_remove, NexusWellConnection,
                                                                  self.__parent_network)
        self._add_to_memory([new_object])

    def modify(self, obj_to_modify: dict[str, None | str | float | int],
               new_properties: dict[str, None | str | float | int]) -> None:
        """Modifies an existing well connection based on a matching dictionary of properties.
        (partial matches allowed if precisely 1 matching node is found).
        Updates the properties with properties in the new_properties dictionary.

        Args:
            obj_to_modify (dict[str, None | str | float | int]): dictionary containing attributes to match in the
            existing well connections.
            new_properties (dict[str, None | str | float | int]): properties to switch to in the new well connection
        """
        self.__parent_network.get_load_status()
        self.__modify_object_operations.modify_network_object(obj_to_modify, new_properties,
                                                              self.__parent_network)

    @property
    def table_header(self) -> str:
        return 'WELLS'

    @property
    def table_footer(self) -> str:
        return 'END' + self.table_header
