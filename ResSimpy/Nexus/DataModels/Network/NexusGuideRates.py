"""Class for handling guide rates in the Nexus Network.

This class is used to store and manipulate the guide rates in a NexusNetwork. It is stored as an instance in the
NexusNetwork class as "guide_rates". In Nexus this is the GUIDERATE table.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING
from uuid import UUID

import pandas as pd

from ResSimpy.FileOperations.File import File
from ResSimpy.GenericContainerClasses.GuideRates import GuideRates
from ResSimpy.Nexus.DataModels.Network.NexusGuideRate import NexusGuideRate
from ResSimpy.Nexus.nexus_add_new_object_to_file import AddObjectOperations
from ResSimpy.Nexus.nexus_collect_tables import collect_all_tables_to_objects
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.nexus_modify_object_in_file import ModifyObjectOperations
from ResSimpy.Nexus.nexus_remove_object_from_file import RemoveObjectOperations
from ResSimpy.Utils.obj_to_dataframe import obj_to_dataframe

if TYPE_CHECKING:
    from ResSimpy.Nexus.NexusNetwork import NexusNetwork


@dataclass
class NexusGuideRates(GuideRates):
    _guid_rates: list[NexusGuideRate] = field(default_factory=list)

    def __init__(self, parent_network: NexusNetwork) -> None:
        """Initialises the NexusDrills class.

        Args:
            parent_network (NexusNetwork): The network that the guide rates are a part of.
        """
        self.__parent_network: NexusNetwork = parent_network
        self._guid_rates: list[NexusGuideRate] = []
        self.__add_object_operations = AddObjectOperations(NexusGuideRate, self.table_header, self.table_footer,
                                                           self.__parent_network.model)
        self.__remove_object_operations = RemoveObjectOperations(self.__parent_network, self.table_header,
                                                                 self.table_footer)
        self.__modify_object_operations = ModifyObjectOperations(self)

    def get_all(self) -> list[NexusGuideRate]:
        """Returns a list of guide rates loaded from the simulator."""
        self.__parent_network.get_load_status()
        return self._guid_rates

    def get_by_name(self, name: str) -> Optional[NexusGuideRate]:
        """Returns a single guide rate for the provided target loaded from the simulator.

        Args:
            name (str): name of the requested target
        Returns:
            NexusGuideRate: which has the same name as requested
        """
        to_return = filter(lambda x: False if x.name is None else x.name.upper() == name.upper(),
                           self._guid_rates)
        return next(to_return, None)

    def get_df(self) -> pd.DataFrame:
        """Returns guide rates data as a dataframe."""
        return obj_to_dataframe(self._guid_rates)

    def load(self, surface_file: File, start_date: str, default_units: UnitSystem) -> None:
        """Loads guide rates from surface file.

        Args:
            surface_file(file): Nexus file representation of the surface file.
            start_date(str): start date of the run.
            default_units(UnitSystem): default units used if no units are found.
        """
        new_guide_rates, _ = collect_all_tables_to_objects(surface_file, {'GUIDERATE': NexusGuideRate},
                                                           start_date=start_date,
                                                           default_units=default_units,
                                                           date_format=self.__parent_network.model.date_format)
        guide_rates_list = new_guide_rates.get('GUIDERATE')
        self._add_to_memory(guide_rates_list)

    def _add_to_memory(self, additional_list: Optional[list[NexusGuideRate]]) -> None:
        """Extends the guide rates object by a list of guide rates provided to it.

        Args:
            additional_list (list[NexusGuideRate]): list of nexus guide rates to add to the existing list.
        """
        if additional_list is None:
            return
        self._guid_rates.extend(additional_list)

    def remove(self, obj_to_remove: dict[str, None | str | float | int] | UUID) -> None:
        """Remove a guide rate from the network based on the properties matching a dictionary or id.

        Args:
            obj_to_remove (UUID | dict[str, None | str | float | int]): UUID of the guide rate to remove or a
            dictionary with sufficient matching parameters to uniquely identify a guide rate

        """
        self.__remove_object_operations.remove_object_from_network_main(
            obj_to_remove, self._network_element_name, self._guid_rates)

    def add(self, obj_to_add: dict[str, None | str | float | int]) -> None:
        """Adds a guide rate to a network, taking a dictionary with properties for the new guide rate.

        Args:
            obj_to_add (dict[str, None | str | float | int]): dictionary taking all the properties for the new
            guide rate.
            Requires date and a name.
        """
        new_object = self.__add_object_operations.add_network_obj(obj_to_add, NexusGuideRate, self.__parent_network)
        self._add_to_memory([new_object])

    def modify(self, obj_to_modify: dict[str, None | str | float | int],
               new_properties: dict[str, None | str | float | int]) -> None:
        """Modifies an existing guide rate based on a matching dictionary of properties.

        Partial matches allowed if precisely 1 matching guide rate is found.
        Updates the properties with properties in the new_properties dictionary.

        Args:
            obj_to_modify (dict[str, None | str | float | int]): dictionary containing attributes to match in the
            existing guide rates.
            new_properties (dict[str, None | str | float | int]): properties to switch to in the new guide rate
        """
        self.__parent_network.get_load_status()
        self.__modify_object_operations.modify_network_object(obj_to_modify, new_properties,
                                                              self.__parent_network)

    @property
    def table_header(self) -> str:
        """Start of the guide rate definition table."""
        return 'GUIDERATE'

    @property
    def table_footer(self) -> str:
        """End of the guide rate definition table."""
        return 'END' + self.table_header

    def get_overview(self) -> str:
        """Returns overview of the guide rates."""
        raise NotImplementedError('To be implemented')
