"""Functions for collecting tables from a Nexus file to populate Nexus objects."""
from __future__ import annotations

from typing import Any, Optional

from ResSimpy.File import File
from ResSimpy.Nexus.DataModels.Network.NexusConstraint import NexusConstraint
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.nexus_constraint_operations import load_inline_constraints
from ResSimpy.Nexus.nexus_file_operations import check_property_in_line, check_token, get_expected_token_value, \
    check_list_tokens, load_table_to_objects
from ResSimpy.Nexus.nexus_load_well_list import load_well_lists


# TODO refactor the collection of tables to an object with proper typing
def collect_all_tables_to_objects(nexus_file: File, table_object_map: dict[str, Any], start_date: Optional[str],
                                  default_units: Optional[UnitSystem]) -> \
        tuple[dict[str, list[Any]], dict[str, list[NexusConstraint]]]:
    """Loads all tables from a given file.

    Args:
    ----
    nexus_file (File): NexusFile representation of the file.
    table_object_map (dict[str, Storage_Object]): dictionary containing the name of the table as keys and \
                the object type to store the data from each row into. Require objects to have a get_keyword_mapping \
                function
    model: (NexusSimulator): main simulator object

    Raises:
    ------
    TypeError: if the unit system found in the property check is not a valid enum UnitSystem.

    Returns:
    -------
    tuple[dict[str, list[DataObject]], dict[str, list[NexusConstraint]]]: a tuple of two dictionaries of lists of \
    DataObjects. The first element is a dictionary of lists of objects keyed with the NexusTable name associated with \
    the object. The second element is a dictionary of lists of NexusConstraints keyed with the well name associated \
    with the constraint.
    """
    current_date = start_date
    nexus_object_results: dict[str, list[Any]] = {x: [] for x in table_object_map}
    nexus_constraints: dict[str, list[NexusConstraint]] = {}

    file_as_list: list[str] = nexus_file.get_flat_list_str_file
    table_start: int = -1
    table_end: int = -1
    property_dict: dict = {}
    token_found: Optional[str] = None
    network_names: list[str] = []
    for index, line in enumerate(file_as_list):
        # check for changes in unit system
        check_property_in_line(line, property_dict, file_as_list)
        unit_system = property_dict.get('UNIT_SYSTEM', default_units)
        if not isinstance(unit_system, UnitSystem):
            raise TypeError(f"Value found for {unit_system=} of type {type(unit_system)} \
                                not compatible, expected type UnitSystem Enum")
        if check_token('TIME', line):
            current_date = get_expected_token_value(
                token='TIME', token_line=line, file_list=file_as_list,
                custom_message=f"Cannot find the date associated with the TIME card in {line=} at line number {index}")
            continue
        if table_start < 0:
            token_found = check_list_tokens(list(table_object_map.keys()), line)
            if token_found is None or check_token('WELLCONTROL', line):
                continue
            # if a token is found get the starting index of the table
            table_start = index + 1
        if token_found is None:
            continue
        token_found = token_found.upper()

        if table_start > 0 and check_token('END' + token_found, line):
            table_end = index
        # if we have a complete table to read in start reading it into objects
        if 0 < table_start <= table_end:
            # cover for the case where we aren't currently reading in the table to an object.
            # if no object is provided by the map for the token found then skip the keyword and reset the tracking vars
            if table_object_map[token_found] is None:
                table_start = -1
                table_end = -1
                token_found = None
                continue
            list_objects = None
            property_map = table_object_map[token_found].get_keyword_mapping()
            if token_found == 'CONSTRAINTS':
                load_inline_constraints(file_as_list=file_as_list[table_start:table_end],
                                        constraint=table_object_map[token_found],
                                        current_date=current_date,
                                        unit_system=unit_system,
                                        property_map=property_map,
                                        existing_constraints=nexus_constraints,
                                        nexus_file=nexus_file,
                                        start_line_index=table_start,
                                        network_names=network_names,
                                        )

            elif token_found == 'QMULT' or token_found == 'CONSTRAINT':
                list_objects = load_table_to_objects(file_as_list=file_as_list[table_start:table_end],
                                                     row_object=table_object_map[token_found],
                                                     property_map=property_map,
                                                     current_date=current_date,
                                                     unit_system=unit_system,
                                                     nexus_obj_dict=nexus_constraints,
                                                     preserve_previous_object_attributes=True)

            elif token_found == 'WELLLIST':
                list_objects = load_well_lists(file_as_list=file_as_list[table_start-1:table_end],
                                               current_date=current_date,
                                               previous_well_lists=nexus_object_results[token_found],
                                               )

            else:
                list_objects = load_table_to_objects(file_as_list=file_as_list[table_start:table_end],
                                                     row_object=table_object_map[token_found],
                                                     property_map=property_map,
                                                     current_date=current_date,
                                                     unit_system=unit_system)

            # store objects found into right dictionary
            list_of_token_obj = nexus_object_results[token_found]
            # This statement ensures that CONSTRAINT that are found in tables are actually added to the dictionary
            # under the same key as constraints to preserve their order
            if (token_found == 'CONSTRAINT' or token_found == 'QMULT') and list_objects is not None:
                for constraint, id_index in list_objects:
                    if isinstance(constraint, NexusConstraint):
                        obj_id = constraint.id
                        well_name = constraint.name
                    else:
                        obj_id = constraint
                        well_name = None
                    correct_line_index = id_index + table_start
                    nexus_file.add_object_locations(obj_id, [correct_line_index])
                    if well_name is None:
                        continue
                    if nexus_constraints.get(well_name, None) is not None:
                        nexus_constraints[well_name].append(constraint)
                    else:
                        nexus_constraints[well_name] = [constraint]

            elif list_objects is not None and isinstance(list_of_token_obj, list):
                list_of_token_obj.extend([x[0] for x in list_objects])
                # add the names from the nodes into the network names for wildcards
                network_names.extend([x.name for x in list_of_token_obj])
                for new_object, id_index in list_objects:
                    correct_line_index = id_index + table_start
                    # temporary try statement until all objects have an id property
                    try:
                        obj_id = new_object.id
                        nexus_file.add_object_locations(obj_id, [correct_line_index])
                    except AttributeError:
                        pass
            # reset indices for further tables
            table_start = -1
            table_end = -1
            token_found = None
    return nexus_object_results, nexus_constraints
