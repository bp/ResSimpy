from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional
from uuid import UUID

import pandas as pd

from ResSimpy.Nexus.nexus_collect_tables import collect_all_tables_to_objects
from ResSimpy.Nexus.DataModels.Network.NexusConstraint import NexusConstraint
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.NexusEnums.UnitsEnum import UnitSystem
from ResSimpy.Utils.obj_to_dataframe import obj_to_dataframe

if TYPE_CHECKING:
    from ResSimpy.Nexus.NexusNetwork import NexusNetwork
    from ResSimpy.Nexus.NexusSimulator import NexusSimulator


@dataclass
class NexusConstraints:
    __constraints: dict[str, list[NexusConstraint]] = field(default_factory=lambda: {})

    def __init__(self, parent_network: NexusNetwork, model: NexusSimulator) -> None:
        self.__parent_network: NexusNetwork = parent_network
        self.__constraints: dict[str, list[NexusConstraint]] = {}
        self.__model: NexusSimulator = model

    def get_constraints(self, object_name: Optional[str] = None, date: Optional[str] = None) -> \
            dict[str, list[NexusConstraint]]:
        """Get the constraints of the existing model with optional parameters to filter for name and date
        Args:
            object_name (Optional[str]): name of the connection, node or wellname to return. Defaults to None.
            date (Optional[str]): date in model format to filter the dates to in the constraints
        Returns: dict[str, list[NexusConstraint]] dictionary of all constraints defined within a model, keyed by the \
            name of the well/node.
        """
        self.__parent_network.get_load_status()

        if object_name is None:
            constraints_to_return = self.__constraints
        else:
            constraints_to_return = {k: v for k, v in self.__constraints.items() if k == object_name}

        if date is None:
            return constraints_to_return

        date_filtered_constraints = {}
        for constraint_name, constraint_list in constraints_to_return.items():
            new_constraint_list = [x for x in constraint_list if x.date == date]
            if len(new_constraint_list) > 0:
                date_filtered_constraints[constraint_name] = new_constraint_list
        return date_filtered_constraints

    def get_constraint_df(self) -> pd.DataFrame:
        """Creates a dataframe representing all processed constraint data in a surface file
        Returns:
            DataFrame: of the properties of the constraint through time with each row representing \
                a change in constraint.
        """
        self.__parent_network.get_load_status()
        list_constraints = []
        for well_constraints in self.__constraints.values():
            list_constraints.extend(well_constraints)
        obj_to_dataframe(list_constraints)

        return obj_to_dataframe(list_constraints)

    def get_constraint_overview(self) -> str:
        raise NotImplementedError('To be implemented')

    def load_constraints(self, surface_file: NexusFile, start_date: str, default_units: UnitSystem) -> None:
        # CONSTRAINT keyword represents a table with a header and columns.
        # CONSTRAINTS keyword represents a list of semi structured constraints with a well_name and then constraints
        new_constraints = collect_all_tables_to_objects(surface_file,
                                                        {
                                                            'CONSTRAINTS': NexusConstraint,
                                                            'CONSTRAINT': NexusConstraint,
                                                            'QMULT': NexusConstraint
                                                            },
                                                        start_date=start_date,
                                                        default_units=default_units)
        cons_list = new_constraints.get('CONSTRAINTS')
        if isinstance(cons_list, list):
            raise ValueError(
                'Incompatible data format for additional constraints. Expected type "dict" instead got "list"')
        self.add_constraints(cons_list)

    def add_constraints(self, additional_constraints: Optional[dict[str, list[NexusConstraint]]]) -> None:
        """Adds additional constraints to memory within the NexusConstraints object.
            If user adds constraints list this will not be reflected in the Nexus deck at this time.

        Args:
        ----
            additional_constraints (list[NexusConstraint]): additional constraints to add as a list
        """
        if additional_constraints is None:
            return
        self.__constraints.update(additional_constraints)

    def find_constraint(self, object_name: str, constraint_dict: dict[str, float | str | int]) -> NexusConstraint:
        # get the name, filter by name, then filter by properties, check for uniqueness as an option?
        # TODO implement this with tests. Give it a dictionary and then filter out the constraints to give one
        #  that matches
        # implement a fuzzy matching (i.e. will work when not all the dictionary parameters are present
        constraints = self.__constraints[object_name]

        matching_constraints = []
        for constraint in constraints:
            for prop, value in constraint_dict.items():
                if getattr(constraint, prop) == value:
                    continue
                else:
                    break
            else:
                matching_constraints.append(constraint)

        if len(matching_constraints) == 1:
            return matching_constraints[0]
        else:
            raise ValueError(f'No unique matching constraints with the properties provided.'
                             f'Instead found: {len(matching_constraints)} matching constraints.')

    def remove_constraint(self, constraint_dict: Optional[dict[str, float | str | int]] = None,
                          constraint_id: Optional[UUID] = None) -> None:
        """Remove a constraint based on closest matching constraint, requires node name and date.\
        Needs one of at least constraint dict or constraint id.

        Args:
            constraint_dict (Optional[dict[str, float | str | int]]): Constraint matching these attributes will be
                removed. Defaults to None.
            constraint_id (Optional[UUID]): Constraint matching this id will be removed.
                Will not be used if constraint dict is provided. Defaults to None.
        """

        if constraint_dict is None and constraint_id is None:
            raise ValueError('no options provided for both constraint_id and constraint_dict')
        if constraint_dict is not None:
            constraint_to_remove = self.find_constraint(str(constraint_dict['name']), constraint_dict)
            constraint_id = constraint_to_remove.id
        if constraint_id is None:
            raise ValueError(f'No constraint found with {constraint_id=}')
        # find which file and remove from the file as list
        surface_file = self.__find_which_surface_file_from_id(constraint_id)
        surface_file.remove_object_from_file_as_list([constraint_id])
        # remove from memory
        for name, list_constraints in self.__constraints.items():
            for i, constraint in enumerate(list_constraints):
                if constraint.id == constraint_id:
                    list_constraints.pop(i)

    def __find_which_surface_file_from_id(self, constraint_id: UUID) -> NexusFile:
        """Finds the surface file with the object id requested."""
        # TODO: make this generic with the find_which_wellspec_file_from_completion_id.

        if self.__model.fcs_file.surface_files is None:
            raise ValueError(f'No surface file found in fcs file at {self.__model.fcs_file.location}')
        surface_files = [x for x in self.__model.fcs_file.surface_files.values() if
                         x.object_locations is not None and constraint_id in x.object_locations]
        if len(surface_files) == 0:
            raise FileNotFoundError(f'No surface file found with an existing constraint that has: {constraint_id=}')
        surface_file = surface_files[0]
        if surface_file.file_content_as_list is None:
            raise FileNotFoundError(f'No file content found in file: {surface_file.location} '
                                    f'with an existing constraint that has: {constraint_id=}')
        return surface_file
