from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING
from uuid import UUID

import pandas as pd

from ResSimpy.File import File
from ResSimpy.Nexus.nexus_collect_tables import collect_all_tables_to_objects
from ResSimpy.Nexus.DataModels.Network.NexusWellhead import NexusWellhead
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Utils.obj_to_dataframe import obj_to_dataframe
from ResSimpy.Wellheads import Wellheads

if TYPE_CHECKING:
    from ResSimpy.Nexus.NexusNetwork import NexusNetwork


@dataclass
class NexusWellheads(Wellheads):
    __wellheads: list[NexusWellhead] = field(default_factory=list)

    def __init__(self, parent_network: NexusNetwork) -> None:
        self.__parent_network: NexusNetwork = parent_network
        self.__wellheads: list[NexusWellhead] = []

    def get_all(self) -> list[NexusWellhead]:
        """Returns a list of wellheads loaded from the simulator."""
        self.__parent_network.get_load_status()
        return self.__wellheads

    def get_by_name(self, name: str) -> Optional[NexusWellhead]:
        """Returns a single wellhead with the provided name loaded from the simulator.

        Args:
            name (str): name of the requested well connection
        Returns:
            NexusWellhead: which has the same name as requested
        """
        to_return = filter(lambda x: False if x.name is None else x.name.upper() == name.upper(),
                           self.__wellheads)
        return next(to_return, None)

    def get_df(self) -> pd.DataFrame:
        return obj_to_dataframe(self.__wellheads)

    def get_overview(self) -> str:
        raise NotImplementedError('To be implemented')

    def load(self, surface_file: File, start_date: str, default_units: UnitSystem) -> None:
        new_wellheads = collect_all_tables_to_objects(surface_file, {'WELLHEAD': NexusWellhead},
                                                      start_date=start_date,
                                                      default_units=default_units)
        wellheads_list = new_wellheads.get('WELLHEAD')
        if isinstance(wellheads_list, dict):
            raise ValueError('Incompatible data format for additional wells. Expected type "list" instead got "dict"')
        self._add_to_memory(wellheads_list)

    def _add_to_memory(self, additional_list: Optional[list[NexusWellhead]]) -> None:
        """Extends the wellhead object by a list of wellheads provided to it.

        Args:
            additional_list (list[NexusWellhead]): list of nexus wellheads to add to the wellhead list.
        """
        if additional_list is None:
            return
        self.__wellheads.extend(additional_list)

    def add(self, obj_to_add: dict[str, None | str | float | int]) -> None:
        raise NotImplementedError

    def remove(self, obj_to_remove: UUID | dict[str, None | str | float | int]) -> None:
        raise NotImplementedError

    def modify(self, obj_to_modify: dict[str, None | str | float | int],
               new_properties: dict[str, None | str | float | int]) -> None:
        raise NotImplementedError

    @property
    def table_header(self) -> str:
        """Start of the wellhead definition table."""
        return 'WELLHEAD'

    @property
    def table_footer(self) -> str:
        """End of the wellhead definition table."""
        return 'END' + self.table_header
