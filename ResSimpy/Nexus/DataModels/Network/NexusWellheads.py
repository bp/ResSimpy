from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING
import pandas as pd

from ResSimpy.Nexus.DataModels.Network.NexusWellhead import NexusWellhead
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.NexusEnums.UnitsEnum import UnitSystem
import ResSimpy.Nexus.nexus_file_operations as nfo
from ResSimpy.Utils.obj_to_dataframe import obj_to_dataframe

if TYPE_CHECKING:
    from ResSimpy.Nexus.NexusNetwork import NexusNetwork


@dataclass
class NexusWellheads:
    __wellheads: list[NexusWellhead] = field(default_factory=list)

    def __init__(self, parent_network: NexusNetwork):
        self.__parent_network: NexusNetwork = parent_network
        self.__wellheads: list[NexusWellhead] = []

    def get_wellheads(self) -> list[NexusWellhead]:
        """ Returns a list of wellheads loaded from the simulator"""
        self.__parent_network.get_load_status()
        return self.__wellheads

    def get_wellhead(self, name: str) -> Optional[NexusWellhead]:
        """ Returns a single well connection with the provided name loaded from the simulator

        Args:
            name (str): name of the requested well connection

        Returns:
            NexusWellConnection: which has the same name as requested
        """
        to_return = filter(lambda x: False if x.name is None else x.name.upper() == name.upper(),
                           self.__wellheads)
        return next(to_return, None)

    def get_wellheads_df(self) -> pd.DataFrame:
        return obj_to_dataframe(self.__wellheads)

    def get_wellheads_overview(self) -> str:
        raise NotImplementedError('To be implemented')

    def load_wellheads(self, surface_file: NexusFile, start_date: str, default_units: UnitSystem) -> None:
        new_wellheads = nfo.collect_all_tables_to_objects(surface_file, {'WELLHEAD': NexusWellhead, },
                                                          start_date=start_date,
                                                          default_units=default_units)
        self.add_wellheads(new_wellheads.get('WELLHEAD'))

    def add_wellheads(self, additional_list: Optional[list[NexusWellhead]]) -> None:
        """ extends the nodes object by a list of wellheads provided to it.

        Args:
            additional_list (list[NexusWellhead]): list of nexus wellheads to add to the nodes list.
        """
        if additional_list is None:
            return
        self.__wellheads.extend(additional_list)

    def __repr__(self):
        filtered_attrs = {k: v for k, v in vars(self).items() if v is not None}
        attrs = ', '.join(f"{k}={v!r}" for k, v in filtered_attrs.items())
        return f"{self.__class__.__name__}({attrs})"
