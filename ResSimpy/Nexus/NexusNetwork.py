from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional, Any

import ResSimpy.Nexus.nexus_collect_tables
from ResSimpy.Nexus.DataModels.Network.NexusConstraint import NexusConstraint
from ResSimpy.Nexus.DataModels.Network.NexusConstraints import NexusConstraints
from ResSimpy.Nexus.DataModels.Network.NexusNode import NexusNode
from ResSimpy.Nexus.DataModels.Network.NexusNodeConnection import NexusNodeConnection
from ResSimpy.Nexus.DataModels.Network.NexusNodeConnections import NexusNodeConnections
from ResSimpy.Nexus.DataModels.Network.NexusNodes import NexusNodes
from ResSimpy.Nexus.DataModels.Network.NexusWellConnection import NexusWellConnection
from ResSimpy.Nexus.DataModels.Network.NexusWellConnections import NexusWellConnections
from ResSimpy.Nexus.DataModels.Network.NexusWellbore import NexusWellbore
from ResSimpy.Nexus.DataModels.Network.NexusWellbores import NexusWellbores
from ResSimpy.Nexus.DataModels.Network.NexusWellhead import NexusWellhead
from ResSimpy.Nexus.DataModels.Network.NexusWellheads import NexusWellheads
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile

if TYPE_CHECKING:
    from ResSimpy.Nexus.NexusSimulator import NexusSimulator


@dataclass(kw_only=True)
class NexusNetwork:
    __model: NexusSimulator
    Nodes: NexusNodes
    Connections: NexusNodeConnections
    WellConnections: NexusWellConnections
    Wellheads: NexusWellheads
    Wellbores: NexusWellbores
    Constraints: NexusConstraints
    __has_been_loaded: bool = False

    def __init__(self, model: NexusSimulator) -> None:
        self.__has_been_loaded: bool = False
        self.__model: NexusSimulator = model
        self.Nodes: NexusNodes = NexusNodes(self)
        self.Connections: NexusNodeConnections = NexusNodeConnections(self)
        self.WellConnections: NexusWellConnections = NexusWellConnections(self)
        self.Wellheads: NexusWellheads = NexusWellheads(self)
        self.Wellbores: NexusWellbores = NexusWellbores(self)
        self.Constraints: NexusConstraints = NexusConstraints(self)

    def get_load_status(self) -> bool:
        if not self.__has_been_loaded:
            self.load()
        return self.__has_been_loaded

    def get_surface_file(self, method_number: Optional[int] = None) -> Optional[dict[int, NexusFile] | NexusFile]:
        """Gets a specific surface file object or a dictionary of surface files keyed by method number.

        Args:
        ----
            method_number (int): Method number for selection of a specific surface file.
                If None then returns a dictionary of method, surface file object

        Returns:
        -------
            Optional[dict[int, NexusFile] | NexusFile]: returns a specific surface file object or a dictionary of \
                surface files keyed by method number
        """
        if method_number is None:
            return self.__model.fcs_file.surface_files
        if self.__model.fcs_file.surface_files is None:
            return None
        return self.__model.fcs_file.surface_files.get(method_number)

    def load(self) -> None:
        """Loads all the objects from the surface files in the Simulator class.
        Table headers with None next to their name are currently skipped awaiting development.
        """

        def type_check_lists(input: Optional[list[Any] | dict[str, list[NexusConstraint]]]) -> Optional[list[Any]]:
            """Guards against dictionaries coming from the dictionary."""
            if isinstance(input, dict):
                raise TypeError(f"Expected a list, instead received a dict: {input}")
            return input

        def type_check_dicts(input: Optional[list[Any] | dict[str, list[NexusConstraint]]]) -> \
                Optional[dict[str, list[NexusConstraint]]]:
            """Guards against dictionaries coming from the dictionary."""
            if isinstance(input, list):
                raise TypeError(f"Expected a dict, instead received a list: {input}")
            return input

        # TODO implement all objects with Nones next to them in the dictionary below
        if self.__model.fcs_file.surface_files is None:
            raise FileNotFoundError('Could not find any surface files associated with the fcs file provided.')
        for surface in self.__model.fcs_file.surface_files.values():
            nexus_obj_dict = ResSimpy.Nexus.nexus_collect_tables.collect_all_tables_to_objects(
                surface, {'NODECON': NexusNodeConnection,
                          'NODES': NexusNode,
                          'WELLS': NexusWellConnection,
                          'WELLHEAD': NexusWellhead,
                          'WELLBORE': NexusWellbore,
                          'CONSTRAINTS': NexusConstraint,
                          'CONSTRAINT': NexusConstraint,
                          'QMULT': NexusConstraint,
                          'CONDEFAULTS': None,
                          'TARGET': None,
                          },
                start_date=self.__model.start_date,
                default_units=self.__model.default_units)
            self.Nodes.add_nodes(type_check_lists(nexus_obj_dict.get('NODES')))
            self.Connections.add_connections(type_check_lists(nexus_obj_dict.get('NODECON')))
            self.WellConnections.add_connections(type_check_lists(nexus_obj_dict.get('WELLS')))
            self.Wellheads.add_wellheads(type_check_lists(nexus_obj_dict.get('WELLHEAD')))
            self.Wellbores.add_wellbores(type_check_lists(nexus_obj_dict.get('WELLBORE')))
            self.Constraints.add_constraints(type_check_dicts(nexus_obj_dict.get('CONSTRAINTS')))

        self.__has_been_loaded = True
