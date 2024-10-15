"""Class that holds all the constraints for a NexusNetwork object.

This class is responsible for loading, modifying and removing constraints from the NexusNetwork object. This class is
also responsible for writing the constraints to the Nexus deck. An instance of this is held within the Network class
as "constraints".
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional, cast
from uuid import UUID

import pandas as pd
import re

from ResSimpy.DataModelBaseClasses.Constraint import Constraint
from ResSimpy.GenericContainerClasses.Constraints import Constraints
from ResSimpy.Nexus.nexus_collect_tables import collect_all_tables_to_objects
from ResSimpy.Nexus.DataModels.Network.NexusConstraint import NexusConstraint
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Utils.obj_to_dataframe import obj_to_dataframe
import ResSimpy.Nexus.nexus_file_operations as nfo

if TYPE_CHECKING:
    from ResSimpy.Nexus.NexusNetwork import NexusNetwork
    from ResSimpy.Nexus.NexusSimulator import NexusSimulator


@dataclass
class NexusConstraints(Constraints):
    """Class that holds all the constraints for a NexusNetwork object.

    This class is responsible for loading, modifying and removing constraints from the NexusNetwork object. This
    class is also responsible for writing the constraints to the Nexus deck.

    Attributes:
        constraints: dict[str, list[NexusConstraint]]: dictionary of all constraints defined within a model,
        keyed by the node or well name.
    """
    _constraints: dict[str, list[NexusConstraint]] = field(default_factory=dict)

    def __init__(self, parent_network: NexusNetwork, model: NexusSimulator) -> None:
        """Initialises the NexusConstraints class.

        Args:
            parent_network (NexusNetwork): the network object that the constraints are associated with.
            model (NexusSimulator): the model object that the constraints are associated with.
        """
        self.__parent_network: NexusNetwork = parent_network
        self._constraints: dict[str, list[NexusConstraint]] = {}
        self.__model: NexusSimulator = model

    def get_all(self, object_name: Optional[str] = None, date: Optional[str] = None) -> \
            dict[str, list[NexusConstraint]]:
        """Get the constraints of the existing model with optional parameters to filter for name and date.

        Args:
            object_name (Optional[str]): name of the connection, node or wellname to return. Defaults to None.
            date (Optional[str]): date in model format to filter the dates to in the constraints
        Returns: dict[str, list[NexusConstraint]] dictionary of all constraints defined within a model, keyed by the \
            name of the well/node.
        """
        self.__parent_network.get_load_status()

        if object_name is None:
            constraints_to_return = self._constraints
        else:
            constraints_to_return = {k: v for k, v in self._constraints.items() if k == object_name}

        if date is None:
            return constraints_to_return

        date_filtered_constraints = {}
        for constraint_name, constraint_list in constraints_to_return.items():
            new_constraint_list = [x for x in constraint_list if x.date == date]
            if len(new_constraint_list) > 0:
                date_filtered_constraints[constraint_name] = new_constraint_list
        return date_filtered_constraints

    def get_df(self) -> pd.DataFrame:
        """Creates a dataframe representing all processed constraint data in a surface file.

        Returns:
            DataFrame: of the properties of the constraint through time with each row representing \
                a change in constraint.
        """
        self.__parent_network.get_load_status()
        list_constraints: list[Constraint] = []
        for well_constraints in self._constraints.values():
            list_constraints.extend(well_constraints)
        obj_to_dataframe(list_constraints)

        return obj_to_dataframe(list_constraints)

    def get_overview(self) -> str:
        """Returns overview of Constraints."""
        raise NotImplementedError('To be implemented')

    def load(self, surface_file: NexusFile, start_date: str, default_units: UnitSystem) -> None:
        """Loads nexus surface file.

        Args:
            surface_file(NexusFile): File path of the Nexus surface file.
            start_date(str): Start date of the run.
            default_units(UnitSystem): default units used if not units are found.
        """
        # CONSTRAINT keyword represents a table with a header and columns.
        # CONSTRAINTS keyword represents a list of semi structured constraints with a well_name and then constraints
        if surface_file.file_content_as_list is not None:
            contents_str = "\n".join(surface_file.file_content_as_list)
            contents_str_line_continuation = re.sub(">\\s*\\n", "", contents_str)
            new_contents_list = contents_str_line_continuation.splitlines()
            surface_file.file_content_as_list = new_contents_list
        _, new_constraints = collect_all_tables_to_objects(surface_file,
                                                           {
                                                               'CONSTRAINTS': NexusConstraint,
                                                               'CONSTRAINT': NexusConstraint,
                                                               'QMULT': NexusConstraint
                                                           },
                                                           start_date=start_date,
                                                           default_units=default_units,
                                                           date_format=self.__model.date_format)
        self._add_to_memory(new_constraints)

    def _add_to_memory(self, additional_constraints: Optional[dict[str, list[NexusConstraint]]]) -> None:
        """Adds additional constraints to memory within the NexusConstraints object.

            If user adds constraints list this will not be reflected in the Nexus deck at this time.

        Args:
        ----
            additional_constraints (Optional[dict[str, list[NexusConstraint]]]): additional constraints to add as a list
        """
        if additional_constraints is None:
            return
        for name, constraints in additional_constraints.items():
            # this does not guarantee the constraints are ordered by datetime
            existing_constraints = self._constraints.get(name, [])
            existing_constraints.extend(constraints)
            self._constraints[name] = existing_constraints

    def find_by_properties(self, object_name: str, constraint_dict: dict[str, None | float | str | int]) -> \
            NexusConstraint:
        """Finds a uniquely matching constraint from a given set of properties in a dictionary of attributes.

        Args:
            object_name (str): name of the node to which the constraint is applied (node name/well name)
            constraint_dict (dict[str, float | str | int]): dictionary of attributes to match on. \
            Allows for partial matches if it finds a unique constraint.

        Returns:
            NexusConstraint of an existing constraint in the model that uniquely matches the provided \
            constraint_dict constraint
        """
        self.__parent_network.get_load_status()
        found_object_from_network = self.__parent_network.find_network_element_with_dict(object_name, constraint_dict,
                                                                                         'constraints')
        # ensure typing is consistent
        if isinstance(found_object_from_network, NexusConstraint):
            return found_object_from_network
        else:
            raise TypeError(f'Wrong object type returned expected NexusConstraint, '
                            f'instead returned {type(found_object_from_network)}')

    def remove(self, constraint_dict: Optional[dict[str, None | float | str | int]] = None,
               constraint_id: Optional[UUID] = None) -> None:
        """Remove a constraint based on closest matching constraint, requires node name and date.

        Needs one of at least constraint dict or constraint id.

        Args:
            constraint_dict (Optional[dict[str, float | str | int]]): Constraint matching these attributes will be
                removed. Defaults to None.
            constraint_id (Optional[UUID]): Constraint matching this id will be removed.
                Will not be used if constraint dict is provided. Defaults to None.
        """
        self.__parent_network.get_load_status()

        if constraint_dict is None and constraint_id is None:
            raise ValueError('no options provided for both constraint_id and constraint_dict')
        if constraint_dict is not None:
            name = constraint_dict.get('name', None)
            if name is None:
                raise ValueError(f'No well or node name provided instead got {name}')
            name = str(name)
            # check for wildcards
            if '*' in name:
                raise NotImplementedError(f'Removing constraints with wildcards is currently unsupported, for {name=}')
            constraint_to_remove = self.find_by_properties(name, constraint_dict)
            constraint_id = constraint_to_remove.id
        if constraint_id is None:
            raise ValueError(f'No constraint found with {constraint_id=}')
        # find which file and remove from the file as list
        surface_file = self.__find_which_surface_file_from_id(constraint_id)
        surface_file.remove_object_from_file_as_list([constraint_id])
        # remove from memory
        removed_constraint = None
        for name, list_constraints in self._constraints.items():
            for i, constraint in enumerate(list_constraints):
                if constraint.id == constraint_id:
                    removed_constraint = list_constraints.pop(i)
        # remove the constraints table if there are no more for that date timestamp
        if removed_constraint is None:
            raise ValueError(f'No constraint found with {constraint_id=}')
        date_of_constraint_removed = removed_constraint.date
        if date_of_constraint_removed is None:
            return
        # search the loaded constraints for constraints on the same date as the removed constraint
        # if there are none then remove the table
        if not any(z for x, y in self._constraints.items() for z in y if z.date == date_of_constraint_removed):
            self.__remove_empty_token_table(date_of_constraint_removed, surface_file=surface_file, token='CONSTRAINTS')
            self.__remove_empty_token_table(date_of_constraint_removed, surface_file=surface_file, token='QMULT',
                                            remove_header=True)
        return

    def __remove_empty_token_table(self, date: str, surface_file: NexusFile, token: str = 'CONSTRAINTS',
                                   remove_header: bool = False) -> None:
        """Removes a table for a given date if it has no other dates for that constraint."""
        # TODO promote this to a higher level function
        keyword_map = {x: y[0] for x, y in NexusConstraint.get_keyword_mapping().items()}
        file_content = surface_file.get_flat_list_str_file
        token_line_number = -1
        end_token_line_number = -1
        found_date = False
        for i, line in enumerate(file_content):
            if nfo.check_token('TIME', line) and \
                    nfo.get_expected_token_value(token='TIME', token_line=line, file_list=file_content[i:]) == date:
                found_date = True
            if found_date and nfo.check_token(token, line):
                token_line_number = i
            elif found_date and nfo.check_token('END' + token, line):
                end_token_line_number = i
            if token_line_number > 0 and end_token_line_number > 0:
                break
        if end_token_line_number > token_line_number:
            if remove_header:
                header_index, headers = nfo.get_table_header(file_content[token_line_number:end_token_line_number],
                                                             keyword_map)
                header_index = token_line_number + header_index
            # remove the last one first to avoid index errors
            surface_file.remove_from_file_as_list(end_token_line_number)
            if remove_header:
                surface_file.remove_from_file_as_list(header_index)
            surface_file.remove_from_file_as_list(token_line_number)

    def __find_which_surface_file_from_id(self, constraint_id: UUID) -> NexusFile:
        """Finds the surface file with the object id requested."""
        # TODO: make this generic with the find_which_wellspec_file_from_completion_id.

        if self.__model.model_files.surface_files is None:
            raise ValueError(f'No surface file found in fcs file at {self.__model.model_files.location}')
        surface_files = [x for x in self.__model.model_files.surface_files.values() if
                         x.object_locations is not None and constraint_id in x.object_locations]
        if len(surface_files) == 0:
            raise FileNotFoundError(f'No surface file found with an existing constraint that has: {constraint_id=}')
        surface_file = surface_files[0]
        if surface_file.file_content_as_list is None:
            raise FileNotFoundError(f'No file content found in file: {surface_file.location} '
                                    f'with an existing constraint that has: {constraint_id=}')
        return surface_file

    def add(self, constraint_to_add: dict[str, None | float | int | str | UnitSystem] | Constraint,
            comments: str | None = None) -> None:
        """Adds a constraint to the network and corresponding surface file.

        Args:
            constraint_to_add (dict[str, float | int | str | UnitSystem] | NexusConstraint): properties of \
            the constraints or a constraint object
            comments (str | None): add optional post line comments
        """
        self.__parent_network.get_load_status()

        # add to memory
        if isinstance(constraint_to_add, dict):
            name = constraint_to_add.get('name', None)
            if name is None:
                raise ValueError('Input arguments or constraint_to_add dictionary must contain a name for the node.')
            new_constraint = NexusConstraint(constraint_to_add)
        else:
            new_constraint = cast(NexusConstraint, constraint_to_add)
            name = new_constraint.name
        if name is None:
            raise ValueError('No name found in the provided constraint object.')
        # check for wildcards
        name = str(name)
        if '*' in name:
            raise NotImplementedError('Adding constraints with wildcards is currently unsupported')
        self._add_to_memory({name: [new_constraint]})

        # add to the file
        if self.__model.model_files.surface_files is None:
            raise FileNotFoundError('No well file found, cannot modify ')

        file_to_add_to = self.__model.model_files.surface_files[1]

        file_as_list = file_to_add_to.get_flat_list_str_file
        if file_as_list is None:
            raise ValueError(f'No file content found in the surface file specified at {file_to_add_to.location}')

        constraint_date = new_constraint.date
        if constraint_date is None:
            raise ValueError(f'Require date for adding constraint to, instead got {new_constraint.date}')
        new_constraint_text = []
        date_comparison = -1
        date_index = -1
        new_constraint_index = -1
        id_line_locs = []
        new_table_needed = False
        new_date_needed = False
        new_qmults_table_needed = False
        correct_for_padding = 0
        # check for need to add qmult table
        qmult_keywords = ['qmult_oil_rate', 'qmult_gas_rate', 'qmult_water_rate']
        # if any of the qmults are defined in the new constraint then add a qmult table
        add_qmults = any(getattr(new_constraint, x, None) for x in qmult_keywords)
        if len(file_as_list) < 2:
            # pad the file if it is empty or only has one line
            new_table_needed = True
            file_as_list.append('\n')
            # ensure the padding is added to the file through the new_constraint_text at the end of the file.
            new_constraint_text.append('\n')
            correct_for_padding = -1
        for index, line in enumerate(file_as_list):
            if nfo.check_token('TIME', line):
                constraint_date_from_file = nfo.get_expected_token_value('TIME', line, [line])
                date_comparison = self.__model._sim_controls.compare_dates(constraint_date_from_file, constraint_date)
                if date_comparison == 0:
                    date_index = index
                    continue

                elif date_comparison > 0 and date_index >= 0:
                    # if a date that is greater than the additional constraint then we have overshot and need to
                    # add in a new table or time card
                    # this is the case where we don't need to write a new time card
                    new_table_needed = True
                    new_constraint_index = index - 1

                elif date_comparison > 0:
                    new_table_needed = True
                    new_date_needed = True
                    new_constraint_index = index
                else:
                    continue
            if nfo.check_token('ENDCONSTRAINTS', line) and date_comparison == 0:
                # find the end of a constraint table and add the new constraint
                new_constraint_index = index
                constraint_string = new_constraint.to_table_line([])
                new_constraint_text.append(constraint_string)
                id_line_locs = [new_constraint_index]
            elif index == len(file_as_list) - 1 and date_index < 0 and not nfo.check_token('ENDQMULT', line):
                # if we're on the final line of the file and we haven't yet set a constraint index
                new_table_needed = True
                new_constraint_index = index + 1
                new_date_needed = True
                if add_qmults:
                    new_qmults_table_needed = True
            elif index == len(file_as_list) - 1 and date_index == 0 and not nfo.check_token('ENDQMULT', line):
                new_table_needed = True
                new_constraint_index = index + 1
                new_date_needed = False
                if add_qmults:
                    new_qmults_table_needed = True

            if new_date_needed:
                # if the date card doesn't exist then add it to the file first
                new_constraint_text.append(f'TIME {constraint_date}\n')

            if new_table_needed:
                new_constraint_text.append('CONSTRAINTS\n')
                new_constraint_text.append(new_constraint.to_table_line([]))
                new_constraint_text.append('ENDCONSTRAINTS\n')
                new_constraint_text.append('\n')
                line_id = new_constraint_index + len(new_constraint_text) - 3 + correct_for_padding
                id_line_locs = [line_id]

            if add_qmults and new_qmults_table_needed:
                new_constraint_text.extend(new_constraint.write_qmult_table())
                # add id location for the qmult table as well
                line_id = new_constraint_index + len(new_constraint_text) - 2 + correct_for_padding
                id_line_locs.append(line_id)
                add_qmults = False
            elif add_qmults and nfo.check_token('ENDQMULT', line) and date_comparison == 0:
                # find the end of the table of qmults that already exist
                new_qmult_index = index
                qmult_string = new_constraint.write_qmult_values()
                new_qmult_object_ids = {new_constraint.id: [new_qmult_index]}
                file_to_add_to.add_to_file_as_list(additional_content=[qmult_string], index=new_qmult_index,
                                                   additional_objects=new_qmult_object_ids)
                add_qmults = False

            if new_constraint_index >= 0 and not add_qmults:
                # once we have found where to add constraint then add the constraint to file and update file ids
                new_constraint_object_ids = {
                    new_constraint.id: id_line_locs
                }
                file_to_add_to.add_to_file_as_list(additional_content=new_constraint_text, index=new_constraint_index,
                                                   additional_objects=new_constraint_object_ids, comments=comments)
                break

    def modify(self, name: str,
               current_constraint: dict[str, None | float | int | str] | Constraint,
               new_constraint_props: dict[str, None | float | int | str | UnitSystem] | Constraint,
               comments: Optional[str] = None) \
            -> None:
        """Modify an existing constraint.

        Retains existing constraint values that are not overridden by the new constraint properties.

        Args:
            name (str): The well name
            current_constraint (dict[str, None | float | int | str] | Constraint): dictionary or constraint object\
            with enough attributes to identify a unique existing constraint in the model.
            new_constraint_props (dict[str, None | float | int | str] | Constraint): dictionary or constraint to \
            update the constraint with.
            comments (Optional[str]): ??
        """

        def clean_constraint_inputs(constraint: dict[str, None | float | int | str] | Constraint) -> \
                dict[str, None | float | int | str]:
            """Cleans up an input ensuring consistent type is returned."""
            if isinstance(constraint, Constraint):
                cleaned_dict = constraint.to_dict()
            else:
                cleaned_dict = constraint
            return cleaned_dict

        cleaned_current_constraint = clean_constraint_inputs(current_constraint)
        cleaned_new_constraint = clean_constraint_inputs(new_constraint_props)

        existing_constraint_obj = self.find_by_properties(name, cleaned_current_constraint)
        self.remove(constraint_id=existing_constraint_obj.id)
        combination_of_constraints = existing_constraint_obj.to_dict()
        combination_of_constraints.update(cleaned_new_constraint)

        self.add(combination_of_constraints, comments)
