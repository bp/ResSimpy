from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional, Any, Literal

from ResSimpy.Network import Network
from ResSimpy.Nexus.nexus_collect_tables import collect_all_tables_to_objects
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
class NexusNetwork(Network):
    __model: NexusSimulator
    nodes: NexusNodes
    connections: NexusNodeConnections
    well_connections: NexusWellConnections
    wellheads: NexusWellheads
    wellbores: NexusWellbores
    constraints: NexusConstraints
    __has_been_loaded: bool = False

    def __init__(self, model: NexusSimulator) -> None:
        self.__has_been_loaded: bool = False
        self.__model: NexusSimulator = model
        self.nodes: NexusNodes = NexusNodes(self)
        self.connections: NexusNodeConnections = NexusNodeConnections(self)
        self.well_connections: NexusWellConnections = NexusWellConnections(self)
        self.wellheads: NexusWellheads = NexusWellheads(self)
        self.wellbores: NexusWellbores = NexusWellbores(self)
        self.constraints: NexusConstraints = NexusConstraints(self, model)

    def get_load_status(self) -> bool:
        """Checks load status and loads the network if it hasn't already been loaded."""
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
            return self.__model.model_files.surface_files
        if self.__model.model_files.surface_files is None:
            return None
        return self.__model.model_files.surface_files.get(method_number)

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
        if self.__model.model_files.surface_files is None:
            raise FileNotFoundError('Could not find any surface files associated with the fcs file provided.')

        for surface in self.__model.model_files.surface_files.values():
            nexus_obj_dict = collect_all_tables_to_objects(
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
                default_units=self.__model.default_units,
                )
            self.nodes._add_nodes_to_memory(type_check_lists(nexus_obj_dict.get('NODES')))
            self.connections.add_connections(type_check_lists(nexus_obj_dict.get('NODECON')))
            self.well_connections.add_connections(type_check_lists(nexus_obj_dict.get('WELLS')))
            self.wellheads.add_wellheads(type_check_lists(nexus_obj_dict.get('WELLHEAD')))
            self.wellbores.add_wellbores(type_check_lists(nexus_obj_dict.get('WELLBORE')))
            self.constraints.add_constraints_to_memory(type_check_dicts(nexus_obj_dict.get('CONSTRAINTS')))

        self.__has_been_loaded = True

    def get_unique_names_in_network(self) -> list[str]:
        """Extracts all names from a network including all the nodes, wells and connections.

        Returns:
            list[str]: list of all the unique names from the network including nodes, wells and connections

        """
        constraint_names_to_add = []
        constraint_names_to_add.extend([x.name for x in self.nodes.get_nodes() if x.name is not None])
        constraint_names_to_add.extend([x.name for x in self.well_connections.get_well_connections()
                                        if x.name is not None])
        constraint_names_to_add.extend([x.name for x in self.connections.get_connections() if x.name is not None])
        constraint_names_to_add.extend([x.name for x in self.wellbores.get_wellbores() if x.name is not None])
        constraint_names_to_add.extend([x.name for x in self.wellheads.get_wellheads() if x.name is not None])
        constraint_names_to_add = list(set(constraint_names_to_add))

        return constraint_names_to_add

    def find_node_with_dict(self, name: str, search_dict: dict[str, None | float | str | int],
                            network_element_type: Literal['nodes', 'connections', 'well_connections', 'wellheads',
                                                          'wellbores', 'constraints']) -> Any:
        """Finds a uniquely matching constraint from a given set of properties in a dictionary of attributes.

        Args:
            name (str): name of the node/connection to find
            search_dict (dict[str, float | str | int]): dictionary of attributes to match on. \
            Allows for partial matches if it finds a unique object.
            network_element_type (Literal[str]): one of nodes, connections, well_connections, wellheads, wellbores,
                constraints

        Returns:
            NexusConstraint of an existing constraint in the model that uniquely matches the provided \
            constraint_dict constraint
        """
        network_element_to_search: Any
        self.get_load_status()
        if network_element_type == 'constraints':
            network_element_to_search = self.constraints.get_constraints().get(name, None)
        else:
            network_element_to_search = getattr(self, network_element_type, None)
            if network_element_to_search is not None:
                network_element_to_search = [x for x in network_element_to_search if x.name == name]

        if network_element_to_search is None or len(network_element_to_search) == 0:
            raise ValueError(f'No {network_element_type} found with {name=}')

        matching_elements = []
        for elements in network_element_to_search:
            for prop, value in search_dict.items():
                if getattr(elements, prop) == value:
                    continue
                else:
                    break
            else:
                matching_elements.append(elements)

        if len(matching_elements) == 1:
            return matching_elements[0]
        else:
            raise ValueError(f'No unique matching {network_element_type} with the properties provided.'
                             f'Instead found: {len(matching_elements)} matching {network_element_type}.')
