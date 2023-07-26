from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING
from uuid import UUID

import pandas as pd

from ResSimpy.File import File
from ResSimpy.Utils.obj_to_dataframe import obj_to_dataframe
from ResSimpy.Nexus.DataModels.Network.NexusWellConnection import NexusWellConnection
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.nexus_collect_tables import collect_all_tables_to_objects
from ResSimpy.WellConnection import WellConnection
from ResSimpy.WellConnections import WellConnections

if TYPE_CHECKING:
    from ResSimpy.Nexus.NexusNetwork import NexusNetwork


@dataclass
class NexusWellConnections(WellConnections):
    __well_connections: list[NexusWellConnection] = field(default_factory=list)

    def __init__(self, parent_network: NexusNetwork) -> None:
        self.__parent_network: NexusNetwork = parent_network
        self.__well_connections: list[NexusWellConnection] = []

    def get_all(self) -> list[NexusWellConnection]:
        """Returns a list of well connections loaded from the simulator."""
        self.__parent_network.get_load_status()
        return self.__well_connections

    def get_by_name(self, name: str) -> Optional[NexusWellConnection]:
        """Returns a single well connection with the provided name loaded from the simulator.

        Args:
        ----
            name (str): name of the requested well connection

        Returns:
        -------
            NexusWellConnection: which has the same name as requested
        """
        to_return = filter(lambda x: False if x.name is None else x.name.upper() == name.upper(),
                           self.__well_connections)
        return next(to_return, None)

    def get_df(self) -> pd.DataFrame:
        """Creates a dataframe representing all processed well connections data in a surface file
        Returns:
            DataFrame: of the properties of the well connections through time with each row representing a single well \
            connection.
        """
        return obj_to_dataframe(self.__well_connections)

    def get_overview(self) -> str:
        raise NotImplementedError('To be implemented')

    def _add_to_memory(self, additional_list: Optional[list[WellConnection]]) -> None:
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

    def add(self, obj_to_add: dict[str, None | str | float | int]):
        pass

    def remove(self, obj_to_remove: UUID | dict[str, None | str | float | int]):
        pass

    def modify(self, obj_to_modify: dict[str, None | str | float | int],
               new_properties: dict[str, None | str | float | int]) -> None:
        pass

    @property
    def table_header(self) -> str:
        return 'WELLS'

    @property
    def table_footer(self) -> str:
        return 'END' + self.table_header
