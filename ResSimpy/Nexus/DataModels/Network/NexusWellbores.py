from dataclasses import field, dataclass
from typing import Optional

import pandas as pd

from ResSimpy.Nexus.DataModels.Network.NexusWellbore import NexusWellbore
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.NexusEnums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.NexusNetwork import NexusNetwork
from ResSimpy.Utils.obj_to_dataframe import obj_to_dataframe
import ResSimpy.Nexus.nexus_file_operations as nfo


@dataclass
class NexusWellbores:
    __wellbores: list[NexusWellbore] = field(default_factory=list)

    def __init__(self, parent_network: NexusNetwork):
        self.__parent_network: NexusNetwork = parent_network
        self.__wellbores: list[NexusWellbore] = []

    def get_wellbores(self) -> list[NexusWellbore]:
        """ Returns a list of wellbores loaded from the simulator"""
        self.__parent_network.get_load_status()
        return self.__wellbores

    def get_wellbore(self, name: str) -> Optional[NexusWellbore]:
        """ Returns a single well connection with the provided name loaded from the simulator

        Args:
            name (str): name of the requested well connection

        Returns:
            NexusWellbore: which has the same name as requested
        """
        to_return = filter(lambda x: False if x.name is None else x.name.upper() == name.upper(),
                           self.__wellbores)
        return next(to_return, None)

    def get_wellbores_df(self) -> pd.DataFrame:
        return obj_to_dataframe(self.__wellbores)

    def get_wellbores_overview(self) -> str:
        raise NotImplementedError('To be implemented')

    def load_wellbores(self, surface_file: NexusFile, start_date: str, default_units: UnitSystem) -> None:
        new_wellbores = nfo.collect_all_tables_to_objects(surface_file, {'WELLBORE': NexusWellbore, },
                                                          start_date=start_date,
                                                          default_units=default_units)
        self.add_wellbores(new_wellbores.get('WELLBORE'))

    def add_wellbores(self, additional_list: Optional[list[NexusWellbore]]) -> None:
        """ extends the nodes object by a list of wellbores provided to it.

        Args:
            additional_list (list[NexusWellbore]): list of nexus wellbores to add to the nodes list.
        """
        if additional_list is None:
            return
        self.__wellbores.extend(additional_list)
