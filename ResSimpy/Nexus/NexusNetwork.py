"""Represents the Nexus implementation of a network.

Holds all the network objects and loads them from the simulator. The currently supported elements are nodes,
connections, well connections, wellheads, wellbores, constraints and targets.
"""
from __future__ import annotations

import re
import warnings
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional, Any, Literal

from ResSimpy.Enums.WellTypeEnum import WellType
from ResSimpy.DataModelBaseClasses.Network import Network
from ResSimpy.Nexus.DataModels.Network.NexusAction import NexusAction
from ResSimpy.Nexus.DataModels.Network.NexusActions import NexusActions
from ResSimpy.Nexus.DataModels.Network.NexusActivationChange import NexusActivationChange
from ResSimpy.Nexus.DataModels.Network.NexusActivationChanges import NexusActivationChanges
from ResSimpy.Nexus.DataModels.Network.NexusConList import NexusConList
from ResSimpy.Nexus.DataModels.Network.NexusConLists import NexusConLists
from ResSimpy.Nexus.DataModels.Network.NexusProc import NexusProc
from ResSimpy.Nexus.DataModels.Network.NexusProcs import NexusProcs
from ResSimpy.Nexus.DataModels.NexusWellList import NexusWellList
from ResSimpy.Nexus.NexusEnums.ActivationChangeEnum import ActivationChangeEnum
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
from ResSimpy.Nexus.DataModels.Network.NexusTarget import NexusTarget
from ResSimpy.Nexus.DataModels.Network.NexusTargets import NexusTargets
from ResSimpy.Nexus.DataModels.Network.NexusWellLists import NexusWellLists

import ResSimpy.FileOperations.file_operations as fo

if TYPE_CHECKING:
    from ResSimpy.Nexus.NexusSimulator import NexusSimulator


@dataclass(kw_only=True)
class NexusNetwork(Network):
    """Represents the Nexus implementation of a network.

    Holds all the network objects and loads them from the simulator. The currently supported elements are nodes,
    connections, well connections, wellheads, wellbores, constraints and targets.
    """
    __model: NexusSimulator
    nodes: NexusNodes
    connections: NexusNodeConnections
    well_connections: NexusWellConnections
    wellheads: NexusWellheads
    wellbores: NexusWellbores
    constraints: NexusConstraints
    procs: NexusProcs
    actions: NexusActions
    targets: NexusTargets
    welllists: NexusWellLists
    activation_changes: NexusActivationChanges
    _has_been_loaded: bool = False

    def __init__(self, model: NexusSimulator, assume_loaded: bool = False) -> None:
        """Initialises the NexusNetwork class.

        Args:
            model (NexusSimulator): NexusSimulator object to be used to loading of the network object.
            assume_loaded (bool): Should be set to True if this object should be created rather than read in from a
                                  file.
        """
        super().__init__(assume_loaded=assume_loaded)
        self.__model: NexusSimulator = model
        self.nodes: NexusNodes = NexusNodes(self)
        self.connections: NexusNodeConnections = NexusNodeConnections(self)
        self.well_connections: NexusWellConnections = NexusWellConnections(self)
        self.wellheads: NexusWellheads = NexusWellheads(self)
        self.wellbores: NexusWellbores = NexusWellbores(self)
        self.constraints: NexusConstraints = NexusConstraints(self, model)
        self.targets: NexusTargets = NexusTargets(self)
        self.welllists: NexusWellLists = NexusWellLists(self)
        self.procs: NexusProcs = NexusProcs(self)
        self.actions: NexusActions = NexusActions(self)
        self.conlists: NexusConLists = NexusConLists(self)
        self.activation_changes: NexusActivationChanges = NexusActivationChanges(self)

    @property
    def model(self) -> NexusSimulator:
        """Returns Nexus simulator model."""
        return self.__model

    def get_network_file(self, method_number: int = 1) -> NexusFile:
        """Gets a specific network file object from the method number.

        Args:
        ----
            method_number (int): Method number for selection of a specific surface file.
                If None then returns a dictionary of method, surface file object

        Returns:
        -------
            NexusFile: returns a specific surface file object of surface files keyed by method number
        """
        if self.__model.model_files.surface_files is None:
            raise ValueError('No files found for the surface network')
        network_file = self.__model.model_files.surface_files.get(method_number, None)
        if network_file is None:
            raise ValueError(f'No file found for {method_number=}, instead found {network_file=}')
        return network_file

    @property
    def __load_procs(self) -> list[NexusProc]:
        """This private function searches the surface file for Nexus procedures, stores data related procedures, and \
        returns a list of Nexus procedure objects. It also collects and stores Nexus Proc function frequencies.
        """

        loaded_procs: list[NexusProc] = []

        files_dict = self.__model.model_files.surface_files
        if files_dict is None:
            raise ValueError('Surface files not found for this model.')

        for file in files_dict.values():

            # for every surface file, grab the lines as a list
            file_contents = file.get_flat_list_str_file
            if file_contents is None:
                raise ValueError(f'No file contents found for surface file {file.location}.')

            # boolean to determine if we are interested in a specific line or not
            grab_line = False

            # the contents of a specific procedure as a list
            proc_contents: list[str] = []

            # initialize the time to the start date of the model, name, and priority
            time = self.__model.start_date
            name_ = None
            priority_ = None
            # initialize an empty proc object, so we can use its staticmethod reset_nexus_proc_function_counts
            proc_obj = NexusProc()
            nexus_proc_function_counts = proc_obj.reset_nexus_proc_function_counts()

            for line in file_contents:

                # check for TIME keyword
                if not grab_line and fo.check_token('TIME', line=line):
                    time = fo.get_expected_token_value(token='TIME', file_list=[line], token_line=line)

                # check for keyword ENDPROCS to signal end of the procedure
                if fo.check_token('ENDPROCS', line=line):
                    # create the proc object
                    proc_obj = NexusProc(contents=proc_contents, date=time, name=name_, priority=priority_)

                    # set the proc function counts
                    proc_obj.contents_breakdown = nexus_proc_function_counts

                    # DO and IF statements are always combined with ENDIF and ENDDO, therefore dividing by 2 will take
                    # care of the over-counting
                    proc_obj.contents_breakdown['IF'] = int(proc_obj.contents_breakdown['IF'] / 2)
                    proc_obj.contents_breakdown['DO'] = int(proc_obj.contents_breakdown['DO'] / 2)

                    # append the fresh object to the list
                    loaded_procs.append(proc_obj)

                    # *IMPORTANT*: reset proc_contents after a procedure has ended!
                    # *IMPORTANT*: reset proc function count dict after a procedure has ended!
                    grab_line = False
                    proc_contents = []
                    nexus_proc_function_counts = proc_obj.reset_nexus_proc_function_counts()

                if grab_line:
                    proc_contents.append(line)
                    # loop over the basic nexus functions and count the occurrences in the proc
                    # split out and ignore the comments with line.split
                    # calling len on re.findall will return the number of times it found it in the line
                    # if re.findall did not find the string it will return an empty list
                    # note that the length of an empty list is zero
                    for function in nexus_proc_function_counts.keys():
                        # special cases arise because some proc functions are one char long (i.e. Q and P)
                        # the search string must be adjusted to avoid over counting when such cases arise
                        if len(function) == 1:
                            nexus_proc_function_counts[function] += (
                                # the regex ensures that cases such as P    ( are captured
                                len(re.findall(function + '\\s*\\(', line.upper().split('!')[0])))
                        else:
                            nexus_proc_function_counts[function] += (
                                len(re.findall(function, line.upper().split('!')[0])))

                if fo.check_token('PROCS', line=line):
                    # next check if it has a NAME and PRIORITY
                    if fo.check_token('NAME', line=line):
                        name_ = fo.get_expected_token_value(token='NAME', file_list=[line], token_line=line)
                    if fo.check_token('PRIORITY', line=line):
                        priority_ = int(fo.get_expected_token_value(token='PRIORITY', file_list=[line],
                                                                    token_line=line))

                    grab_line = True

        return loaded_procs

    def load(self) -> None:
        """Loads all the objects from the surface files in the Simulator class.

        Table headers with None next to their name are currently skipped awaiting development.
        """

        def type_check_lists(value: Optional[list[Any] | dict[str, list[NexusConstraint]]]) -> Optional[list[Any]]:
            """Guards against dictionaries coming from the dictionary."""
            if isinstance(value, dict):
                raise TypeError(f"Expected a list, instead received a dict: {value}")
            return value

        def type_check_dicts(value: Optional[list[Any] | dict[str, list[NexusConstraint]]]) -> \
                Optional[dict[str, list[NexusConstraint]]]:
            """Guards against dictionaries coming from the dictionary."""
            if isinstance(value, list):
                raise TypeError(f"Expected a dict, instead received a list: {value}")
            return value

        # TODO implement all objects with Nones next to them in the dictionary below
        if self.__model.model_files.surface_files is None:
            raise FileNotFoundError('Could not find any surface files associated with the fcs file provided.')

        object_to_table_header_map = {'NODECON': NexusNodeConnection,
                                      'NODES': NexusNode,
                                      'WELLS': NexusWellConnection,
                                      'GASWELLS': NexusWellConnection,
                                      'WELLHEAD': NexusWellhead,
                                      'WELLBORE': NexusWellbore,
                                      'CONSTRAINTS': NexusConstraint,
                                      'CONSTRAINT': NexusConstraint,
                                      'QMULT': NexusConstraint,
                                      'CONDEFAULTS': None,
                                      'TARGET': NexusTarget,
                                      'GUIDERATE': None,
                                      'PROCS': None,
                                      'WELLLIST': NexusWellList,
                                      'CONLIST': NexusConList,
                                      'ACTIONS': NexusAction,
                                      'ACTIVATE_DEACTIVATE': NexusActivationChange
                                      }

        for surface in self.__model.model_files.surface_files.values():
            nexus_obj_dict, constraints = collect_all_tables_to_objects(
                nexus_file=surface,
                table_object_map=object_to_table_header_map,
                start_date=self.__model.start_date,
                default_units=self.__model.default_units,
                date_format=self.__model.date_format
            )
            self.nodes._add_to_memory(type_check_lists(nexus_obj_dict.get('NODES')))
            self.connections._add_to_memory(type_check_lists(nexus_obj_dict.get('NODECON')))
            self.well_connections._add_to_memory(type_check_lists(nexus_obj_dict.get('WELLS')))
            self.well_connections._add_to_memory(type_check_lists(nexus_obj_dict.get('GASWELLS')))
            self.wellheads._add_to_memory(type_check_lists(nexus_obj_dict.get('WELLHEAD')))
            self.wellbores._add_to_memory(type_check_lists(nexus_obj_dict.get('WELLBORE')))
            self.constraints._add_to_memory(type_check_dicts(constraints))
            self.targets._add_to_memory(type_check_lists(nexus_obj_dict.get('TARGET')))
            self.welllists._add_to_memory(type_check_lists(nexus_obj_dict.get('WELLLIST')))
            self.conlists._add_to_memory(type_check_lists(nexus_obj_dict.get('CONLIST')))
            self.activation_changes._add_to_memory(type_check_lists(nexus_obj_dict.get('ACTIVATE_DEACTIVATE')))
            constraint_activation_changes = self.__get_constraint_activation_changes(constraints=constraints)
            self.activation_changes._add_to_memory(type_check_lists(constraint_activation_changes))

            actions_check = type_check_lists(nexus_obj_dict.get('ACTIONS'))
            if actions_check is not None:
                self.actions._add_to_memory(actions_check)

            add_procs_to_mem = self.__load_procs
            self.procs._add_to_memory(add_procs_to_mem)

        self._has_been_loaded = True
        self.__update_well_types()

        if self.model.options is not None:
            # load the options file
            self.model.options.load_nexus_options_if_not_loaded()

            # assign the region numbers for the targets with a region name
            self.targets._look_up_region_numbers_for_targets(self.model.options)

    def __get_constraint_activation_changes(self, constraints: dict[str, list[NexusConstraint]]) \
            -> list[NexusActivationChange]:
        """Get all the activation changes held in constraint objects."""
        activation_changes = []
        for connection_name, connection_constraints in constraints.items():
            for constraint in connection_constraints:
                if constraint.active_node is not None:
                    change = ActivationChangeEnum.ACTIVATE if constraint.active_node is True \
                        else ActivationChangeEnum.DEACTIVATE
                    new_activation_change = NexusActivationChange(change=change, name=connection_name,
                                                                  date=constraint.date,
                                                                  date_format=constraint.date_format,
                                                                  start_date=constraint.start_date,
                                                                  is_constraint_change=True)
                    activation_changes.append(new_activation_change)

        return activation_changes

    def __update_well_types(self) -> None:
        """Updates the types of all of the wells using information found in the wells table."""
        for connection in self.well_connections.get_all():
            if connection.name is None or connection.stream is None:
                # Connection cannot be used to determine well type, so ignore it.
                continue

            well_to_modify = self.__model.wells.get(connection.name)

            if well_to_modify is None:
                warnings.warn(UserWarning(f'Cannot find matching well for {connection.name} declared in surface file.'))
                continue

            match connection.stream.upper():
                case 'PRODUCER':
                    well_type = WellType.PRODUCER
                case 'GAS':
                    well_type = WellType.GAS_INJECTOR
                case 'WATER':
                    well_type = WellType.WATER_INJECTOR
                case 'OIL':
                    well_type = WellType.OIL_INJECTOR
                case _:
                    well_type = WellType.PRODUCER

            well_to_modify.well_type = well_type

    def get_unique_names_in_network(self) -> list[str]:
        """Extracts all names from a network including all the nodes, wells and connections.

        Returns:
            list[str]: list of all the unique names from the network including nodes, wells and connections

        """
        constraint_names_to_add = []
        constraint_names_to_add.extend([x.name for x in self.nodes.get_all() if x.name is not None])
        constraint_names_to_add.extend([x.name for x in self.well_connections.get_all()
                                        if x.name is not None])
        constraint_names_to_add.extend([x.name for x in self.connections.get_all() if x.name is not None])
        constraint_names_to_add.extend([x.name for x in self.wellbores.get_all() if x.name is not None])
        constraint_names_to_add.extend([x.name for x in self.wellheads.get_all() if x.name is not None])
        constraint_names_to_add = list(set(constraint_names_to_add))

        return constraint_names_to_add

    def find_network_element_with_dict(self, name: str, search_dict: dict[str, None | float | str | int],
                                       network_element_type: Literal['nodes', 'connections', 'well_connections',
                                       'wellheads', 'wellbores', 'constraints', 'targets']) -> Any:
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
        self.get_load_status()
        if network_element_type == 'constraints':
            network_element_to_search = self.constraints.get_all().get(name, None)
        else:
            # retrieve the getter method on the network attribute
            network_element = getattr(self, f'{network_element_type}', None)
            if network_element is None:
                raise ValueError(f'Network has no elements associated with the {network_element_type=} requested')

            network_element_to_search = [x for x in network_element.get_all() if x.name == name]

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
