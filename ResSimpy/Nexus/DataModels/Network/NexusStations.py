"""Holds the NexusStations class which is used to store and manipulate the stations in a NexusNetwork.

It is stored as an instance in the NexusNetwork class as "stations".
"""

from __future__ import annotations
from dataclasses import dataclass, field
from uuid import UUID
from typing import Literal, Sequence, Optional, TYPE_CHECKING

import pandas as pd

from ResSimpy.FileOperations.File import File
from ResSimpy.Nexus.nexus_add_new_object_to_file import AddObjectOperations
from ResSimpy.Nexus.nexus_collect_tables import collect_all_tables_to_objects
from ResSimpy.Nexus.DataModels.Network.NexusStation import NexusStation
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.nexus_modify_object_in_file import ModifyObjectOperations
from ResSimpy.Nexus.nexus_remove_object_from_file import RemoveObjectOperations
from ResSimpy.DataModelBaseClasses.OperationsMixin import NetworkOperationsMixIn
from ResSimpy.Utils.obj_to_dataframe import obj_to_dataframe

if TYPE_CHECKING:
    from ResSimpy.Nexus.NexusNetwork import NexusNetwork


@dataclass(kw_only=True)
class NexusStations(NetworkOperationsMixIn):
    """Class to store and manipulate the stations in a NexusStation.

    It is stored as an instance in the NexNexusStation usNetwork class as "stations".
    A list of stations in the network are stored in memory these can be accessed through
    the get_all method.
    """

    _stations: list[NexusStation] = field(default_factory=list)

    def __init__(self, parent_network: NexusNetwork) -> None:
        """Initialises the NexusStations class.

        Args:
            parent_network (NexusNetwork): The network that the stations are a part of.
        """
        self.__parent_network: NexusNetwork = parent_network
        self._stations: list[NexusStation] = []
        self.__add_object_operations = AddObjectOperations(
            NexusStation,
            self.table_header,
            self.table_footer,
            self.__parent_network.model,
        )
        self.__remove_object_operations = RemoveObjectOperations(
            self.__parent_network, self.table_header, self.table_footer
        )
        self.__modify_object_operations = ModifyObjectOperations(self)

    @property
    def table_header(self) -> str:
        """Start of the Station definition table."""
        return "STATION"

    @property
    def table_footer(self) -> str:
        """End of the Station definition table."""
        return "ENDSTATION"

    def get_all(self) -> Sequence[NexusStation]:
        """Returns a list of stations loaded from the simulator."""
        self.__parent_network.get_load_status()
        return self._stations

    def get_by_name(self, station_name: str) -> Optional[NexusStation]:
        """Returns a single station with the provided name loaded from the simulator.

        Args:
        ----
            station_name (str): name of the requested station

        Returns:
        -------
            NexusStation: which has the same name as the requested station_name

        """
        stations_to_return = filter(
            lambda x: (
                False if x.name is None else x.name.upper() == station_name.upper()
            ),
            self._stations,
        )
        return next(stations_to_return, None)

    def get_df(self) -> pd.DataFrame:
        """Creates a dataframe representing all processed station data in a surface file.

        Returns:
            DataFrame: of the properties of the stations through time with each row representing a station.
        """
        self.__parent_network.get_load_status()
        df_store = obj_to_dataframe(self._stations)
        return df_store

    def get_overview(self) -> str:
        """Returns overview of the stations."""
        raise NotImplementedError("To be implemented")

    def load(
        self, surface_file: File, start_date: str, default_units: UnitSystem
    ) -> None:
        """Calls load stations and appends the list of discovered stations into the NexusStations object.

        Args:
            surface_file (File): NexusFile representation of the surface file.
            start_date (str): Starting date of the run
            default_units (UnitSystem): Units used in case not specified by surface file.

        Raises:
            TypeError: if the unit system found in the property check is not a valid enum UnitSystem.

        """
        new_stations, _ = collect_all_tables_to_objects(
            surface_file,
            {"STATIONS": NexusStation},
            start_date=start_date,
            default_units=default_units,
            date_format=self.__parent_network.model.date_format,
        )
        stations_list = new_stations.get("STATIONS")
        self._add_to_memory(stations_list)

    def _add_to_memory(self, additional_list: Optional[list[NexusStation]]) -> None:
        """Extends the stations object by a list of stations provided to it.

        Args:
        ----
            additional_list (Sequence[NexusStation]): list of nexus stations to add to the stations list.

        Returns:
        -------
            None
        """
        if additional_list is None:
            return
        self._stations.extend(additional_list)

    def remove(
        self, station_to_remove: dict[str, None | str | float | int] | UUID
    ) -> None:
        """Remove a station from the network based on the properties matching a dictionary or id.

        Args:
            station_to_remove (UUID | dict[str, None | str | float | int]): UUID of the station to remove
            or a dictionary with sufficient matching parameters to uniquely identify a station

        """
        self.__remove_object_operations.remove_object_from_network_main(
            station_to_remove, self._network_element_name, self._stations
        )

    def add(self, station_to_add: dict[str, None | str | float | int]) -> None:
        """Adds a station to a network, taking a dictionary with properties for the new station.

        Args:
            station_to_add (dict[str, None | str | float | int]): dictionary taking all the properties for new station.
            Requires date and a station name.
        """
        new_object = self.__add_object_operations.add_network_obj(
            station_to_add, NexusStation, self.__parent_network
        )
        self._add_to_memory([new_object])

    def modify(
        self,
        station_to_modify: dict[str, None | str | float | int],
        new_properties: dict[str, None | str | float | int],
    ) -> None:
        """Modifies an existing station based on a matching dictionary of properties.

        Partial matches allowed if precisely 1 matching station is found. Updates the properties with properties in the
        new_properties dictionary.

        Args:
            station_to_modify (dict[str, None | str | float | int]): dictionary containing attributes to match in the
            existing station set.
            new_properties (dict[str, None | str | float | int]): properties to switch to in the new station
        """
        self.__parent_network.get_load_status()

        self.__modify_object_operations.modify_network_object(
            station_to_modify, new_properties, self.__parent_network
        )

    @property
    def _network_element_name(self) -> Literal["stations"]:
        return "stations"
