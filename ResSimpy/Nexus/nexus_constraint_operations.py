"""Key functions for reading in nexus constraints and populating objects with the data."""
from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from ResSimpy.Nexus.DataModels.Network.NexusConstraint import NexusConstraint
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.DataModels.NexusWellList import NexusWellList
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.Nexus.nexus_file_operations import get_next_value, correct_datatypes
from ResSimpy.Utils.invert_nexus_map import nexus_keyword_to_attribute_name
import fnmatch

if TYPE_CHECKING:
    from ResSimpy.FileOperations.File import File


def load_inline_constraints(file_as_list: list[str], constraint: type[NexusConstraint], current_date: Optional[str],
                            unit_system: UnitSystem, property_map: dict[str, tuple[str, type]],
                            existing_constraints: dict[str, list[NexusConstraint]], nexus_file: File,
                            start_line_index: int, date_format: DateFormat, welllists: list[NexusWellList],
                            network_names: Optional[list[str]] = None, start_date: str | None = None) -> None:
    """Loads table of constraints with the wellname/node first and the constraints following inline
        uses previous set of constraints as still applied to the well.

    Args:
    ----
        file_as_list (list[str]): file represented as a list of strings
        constraint (NexusConstraint): object to store the attributes extracted from each row.
        current_date (str): the current date in the table
        unit_system (UnitSystem): Unit system enum
        property_map (dict[str, tuple[str, type]]): Mapping of nexus keywords to attributes
        existing_constraints (dict[str, NexusConstraint]): all existing constraints from previous lines of the \
            surface file
        nexus_file (File): The Nexus file containing the constraints.
        start_line_index (int): The index of the line in the file to start loading from.
        network_names (Optional[list[str]]): list of names for all nodes, wells and connections in a nexus network.
            Used in deriving constraints from wildcards. Defaults to None.
        date_format (Optional[DateFormat]): The date format of the object.
        welllists (list[WellList]): A list of all the WELLLISTs loaded in so far.
        start_date (str | None): The start date of the model. Defaults to None.

    Returns:
    -------
        dict[UUID, int]: dictionary of object locations derived from inline table.
    """
    welllist_names = [x.name for x in welllists]
    for index, line in enumerate(file_as_list):
        properties_dict: dict[str, str | float | UnitSystem | None] = {'date': current_date, 'unit_system': unit_system}
        # first value in the line has to be the node/wellname
        name = get_next_value(0, [line])
        constraint_names_to_add: list[str] = []
        if name is None:
            continue
        properties_dict['name'] = name
        if '*' in name:
            if network_names is None:
                raise ValueError('No existing nodes found to add wildcards to')
            else:
                # filter names that match the pattern
                constraint_names_to_add = fnmatch.filter(network_names, name)
        elif name in welllist_names:
            # If the name refers to a welllist, apply the constraints to all of the wells in that.
            welllist_for_constraining = next(x for x in welllists if x.name == name)
            wellnames_in_welllist = welllist_for_constraining.wells
            constraint_names_to_add.extend(wellnames_in_welllist)
        else:
            constraint_names_to_add.append(name)

        trimmed_line = line.replace(name, "", 1)
        next_value = get_next_value(0, [trimmed_line])
        # loop through the line for each set of constraints
        while next_value is not None:
            token_value = next_value.upper()
            if token_value in ['CLEAR', 'CLEARP', 'CLEARQ', 'CLEARLIMIT', 'CLEARALQ']:
                properties_dict[nexus_keyword_to_attribute_name(constraint.get_keyword_mapping(), token_value)] = True
                trimmed_line = trimmed_line.replace(next_value, "", 1)
                next_value = get_next_value(0, [trimmed_line])
                if next_value is None:
                    break
                token_value = next_value.upper()

            elif token_value == 'ACTIVATE' or token_value == 'DEACTIVATE':
                properties_dict.update({'active_node': token_value == 'ACTIVATE'})
                trimmed_line = trimmed_line.replace(next_value, "", 1)
                next_value = get_next_value(0, [trimmed_line])
                if next_value is None:
                    break
                token_value = next_value.upper()

            trimmed_line = trimmed_line.replace(next_value, "", 1)
            # extract the attribute name for the given nexus constraint token
            if property_map.get(token_value, None) is None:
                # if the next token found along isn't a valid property then move to the next line.
                break

            attribute = property_map[token_value][0]
            next_value = get_next_value(0, [trimmed_line])
            if next_value is None:
                raise ValueError(f'No value found after {token_value} in {line}')
            elif next_value == 'MULT':
                try:
                    attribute = property_map[token_value + '_MULT'][0]
                except AttributeError:
                    raise AttributeError(f'Unexpected MULT keyword following {token_value}')
                properties_dict[attribute] = True

            else:
                properties_dict[attribute] = correct_datatypes(next_value, float)
            trimmed_line = trimmed_line.replace(next_value, "", 1)
            next_value = get_next_value(0, [trimmed_line])

        # Loop through all objects that should have the constraints applied to them
        for name_of_node in constraint_names_to_add:
            # first check if there are any existing constraints created for the well this timestep
            properties_dict['name'] = name_of_node
            well_constraints = existing_constraints.get(name_of_node, None)
            if well_constraints is not None:
                latest_constraint = well_constraints[-1]
                if latest_constraint.date == current_date:
                    latest_constraint.update(properties_dict, True)
                    nexus_file.add_object_locations(latest_constraint.id, [index + start_line_index])
                else:
                    # otherwise take a copy of the previous constraint and add the additional properties
                    new_constraint = constraint(properties_dict, date_format=date_format, start_date=start_date)
                    well_constraints.append(new_constraint)
                    nexus_file.add_object_locations(new_constraint.id, [index + start_line_index])
            else:
                new_constraint = constraint(properties_dict, date_format=date_format, start_date=start_date)
                existing_constraints[name_of_node] = [new_constraint]
                nexus_file.add_object_locations(new_constraint.id, [index + start_line_index])


def __clear_constraints(token_value: str, constraint: type[NexusConstraint]) -> dict[str, None]:
    """Replicates behaviour of the clear keyword in nexus constraints by creating a dictionary filled with \
    Nones for the relevant parameters.
    """
    match token_value:
        case 'CLEAR':
            constraint_clearing_dict = constraint.get_rate_constraints_map()
            constraint_clearing_dict.update(constraint.get_pressure_constraints_map())
            constraint_clearing_dict.update(constraint.get_limit_constraints_map())
        case 'CLEARQ':
            constraint_clearing_dict = constraint.get_rate_constraints_map()
        case 'CLEARLIMIT':
            constraint_clearing_dict = constraint.get_limit_constraints_map()
        case 'CLEARP':
            constraint_clearing_dict = constraint.get_pressure_constraints_map()
        case 'CLEARALQ':
            constraint_clearing_dict = constraint.get_alq_constraints_map()
        case _:
            constraint_clearing_dict = {}
    return {x[0]: None for x in constraint_clearing_dict.values()}
