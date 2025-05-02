"""Class for handling drills in the Nexus Network.

This class is used to store and manipulate the drills in a NexusNetwork. It is stored as an instance in the
NexusNetwork class as "drills". In Nexus this is the DRILL table.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING
from uuid import UUID

import pandas as pd

from ResSimpy.FileOperations.File import File
from ResSimpy.GenericContainerClasses.Drills import Drills
from ResSimpy.Nexus.DataModels.Network.NexusDrill import NexusDrill
from ResSimpy.Nexus.nexus_add_new_object_to_file import AddObjectOperations
from ResSimpy.Nexus.nexus_collect_tables import collect_all_tables_to_objects
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.nexus_modify_object_in_file import ModifyObjectOperations
from ResSimpy.Nexus.nexus_remove_object_from_file import RemoveObjectOperations
from ResSimpy.Utils.obj_to_dataframe import obj_to_dataframe

if TYPE_CHECKING:
    from ResSimpy.Nexus.NexusNetwork import NexusNetwork


@dataclass
class NexusDrills(Drills):
    _drills: list[NexusDrill] = field(default_factory=list)

    def __init__(self, parent_network: NexusNetwork) -> None:
        """Initialises the NexusDrills class.

        Args:
            parent_network (NexusNetwork): The network that the drills are a part of.
        """
        self.__parent_network: NexusNetwork = parent_network
        self._drills: list[NexusDrill] = []
        self.__add_object_operations = AddObjectOperations(NexusDrill, self.table_header, self.table_footer,
                                                           self.__parent_network.model)
        self.__remove_object_operations = RemoveObjectOperations(self.__parent_network, self.table_header,
                                                                 self.table_footer)
        self.__modify_object_operations = ModifyObjectOperations(self)

    def get_all(self) -> list[NexusDrill]:
        """Returns a list of drills loaded from the simulator."""
        self.__parent_network.get_load_status()
        return self._drills

    def get_by_name(self, name: str) -> Optional[NexusDrill]:
        """Returns a single drill with the provided name loaded from the simulator.

        Args:
            name (str): name of the requested well connection
        Returns:
            NexusDrill: which has the same name as requested
        """
        to_return = filter(lambda x: False if x.name is None else x.name.upper() == name.upper(),
                           self._drills)
        return next(to_return, None)

    def get_df(self) -> pd.DataFrame:
        """Returns drill data as a dataframe."""
        return obj_to_dataframe(self._drills)

    def load(self, surface_file: File, start_date: str, default_units: UnitSystem) -> None:
        """Loads drill data from surface file.

        Args:
            surface_file(file): Nexus file representation of the surface file.
            start_date(str): start date of the run.
            default_units(UnitSystem): default units used if no units are found.
        """
        new_drills, _ = collect_all_tables_to_objects(surface_file, {'DRILL': NexusDrill},
                                                      start_date=start_date,
                                                      default_units=default_units,
                                                      date_format=self.__parent_network.model.date_format)
        drills_list = new_drills.get('DRILL')
        self._add_to_memory(drills_list)

    def _add_to_memory(self, additional_list: Optional[list[NexusDrill]]) -> None:
        """Extends the drill object by a list of drills provided to it.

        Args:
            additional_list (list[NexusDrill]): list of nexus drills to add to the drill list.
        """
        if additional_list is None:
            return
        self._drills.extend(additional_list)

    def remove(self, obj_to_remove: dict[str, None | str | float | int] | UUID) -> None:
        """Remove a drill from the network based on the properties matching a dictionary or id.

        Args:
            obj_to_remove (UUID | dict[str, None | str | float | int]): UUID of the drill to remove or a dictionary \
            with sufficient matching parameters to uniquely identify a drill

        """
        self.__remove_object_operations.remove_object_from_network_main(
            obj_to_remove, self._network_element_name, self._drills)

    def add(self, obj_to_add: dict[str, None | str | float | int]) -> None:
        """Adds a drill to a network, taking a dictionary with properties for the new drill.

        Args:
            obj_to_add (dict[str, None | str | float | int]): dictionary taking all the properties for the new
            drill.
            Requires date and a name.
        """
        new_object = self.__add_object_operations.add_network_obj(obj_to_add, NexusDrill, self.__parent_network)
        self._add_to_memory([new_object])

    def modify(self, obj_to_modify: dict[str, None | str | float | int],
               new_properties: dict[str, None | str | float | int]) -> None:
        """Modifies an existing drill based on a matching dictionary of properties.

        Partial matches allowed if precisely 1 matching node is found.
        Updates the properties with properties in the new_properties dictionary.

        Args:
            obj_to_modify (dict[str, None | str | float | int]): dictionary containing attributes to match in the
            existing drills.
            new_properties (dict[str, None | str | float | int]): properties to switch to in the new drill
        """
        self.__parent_network.get_load_status()
        self.__modify_object_operations.modify_network_object(obj_to_modify, new_properties,
                                                              self.__parent_network)

    @property
    def table_header(self) -> str:
        """Start of the drill definition table."""
        return 'DRILL'

    @property
    def table_footer(self) -> str:
        """End of the drill definition table."""
        return 'END' + self.table_header

    def get_overview(self) -> str:
        """Returns overview of the drill."""
        raise NotImplementedError('To be implemented')
