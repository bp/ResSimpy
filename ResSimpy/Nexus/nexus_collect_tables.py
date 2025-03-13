"""Functions for collecting tables from a Nexus file to populate Nexus objects."""
from __future__ import annotations

import fnmatch
from datetime import timedelta, time
from typing import Any, Optional

import ResSimpy.FileOperations.file_operations as fo
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.FileOperations.File import File
from ResSimpy.FileOperations.file_operations import get_next_value, get_expected_token_value
from ResSimpy.Nexus.DataModels.Network.NexusActivationChange import NexusActivationChange
from ResSimpy.Nexus.DataModels.Network.NexusConLists import NexusConLists
from ResSimpy.Nexus.DataModels.Network.NexusConstraint import NexusConstraint
from ResSimpy.Nexus.DataModels.Network.NexusWellLists import NexusWellLists
from ResSimpy.Nexus.DataModels.NexusWellList import NexusWellList
from ResSimpy.Nexus.NexusEnums.ActivationChangeEnum import ActivationChangeEnum
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.Nexus.nexus_constraint_operations import load_inline_constraints
from ResSimpy.Nexus.nexus_file_operations import check_property_in_line, check_token, check_list_tokens, \
    load_table_to_objects
from ResSimpy.Nexus.nexus_load_list_table import load_table_to_lists
from ResSimpy.Time.ISODateTime import ISODateTime


# TODO refactor the collection of tables to an object with proper typing
def collect_all_tables_to_objects(nexus_file: File, table_object_map: dict[str, Any], start_date: Optional[str],
                                  default_units: Optional[UnitSystem], date_format: DateFormat) -> \
        tuple[dict[str, list[Any]], dict[str, list[NexusConstraint]]]:
    """Loads all tables from a given file.

    Args:
    ----
        nexus_file (File): NexusFile representation of the file.
        table_object_map (dict[str, Storage_Object]): dictionary containing the name of the table as keys and \
                    the object type to store the data from each row into. Require objects to have a get_keyword_mapping\
                    function
        model: (NexusSimulator): main simulator object
        start_date (Optional[str]): The model start date.
        default_units (Optional[UnitSystem]): The default unit system the Nexus model is set to.
        date_format (Optional[DateFormat]): The date format of the object.

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
    well_names: list[str] = []
    well_lists: list[NexusWellList] = []
    is_deactivate_block = False
    is_activate_block = False
    is_actions_block = False
    is_constraints_block = False
    default_crossflow: Optional[str] = None
    default_shutin: Optional[str] = None
    for index, line in enumerate(file_as_list):
        # check for changes in unit system
        check_property_in_line(line, property_dict, file_as_list)
        unit_system = property_dict.get('UNIT_SYSTEM', default_units)
        if not isinstance(unit_system, UnitSystem):
            raise TypeError(f"Value found for {unit_system=} of type {type(unit_system)} \
                                not compatible, expected type UnitSystem Enum")

        if current_date is None:
            raise ValueError("Unable to determine date for object")

        # Important!: DEACTIVATE can also appear in the ACTIONS table in the surface network and CONSTRAINTS tables.
        # If we are already in one of those blocks, we don't want to consider it a new activate / deactivate block.
        if fo.check_token('ACTIONS', line=line):
            is_actions_block = True
        if fo.check_token('ENDACTIONS', line=line):
            is_actions_block = False
        if fo.check_token('CONSTRAINTS', line=line):
            is_constraints_block = True
        if fo.check_token('ENDCONSTRAINTS', line=line):
            is_constraints_block = False

        if not is_actions_block and not is_constraints_block:
            is_activate_block, is_deactivate_block, should_continue = \
                __activate_deactivate_checks(line=line,
                                             is_activate_block=is_activate_block,
                                             is_deactivate_block=is_deactivate_block,
                                             current_date=current_date,
                                             start_date=start_date,
                                             date_format=date_format,
                                             nexus_object_results=nexus_object_results)

            if should_continue:
                # If we have already read in all the values for this line in the previous call, continue onto the next
                # line.
                continue

        if check_token('TIME', line) and table_start < 0:
            time_value = get_expected_token_value(
                token='TIME', token_line=line, file_list=file_as_list,
                custom_message=f"Cannot find the date associated with the TIME card in {line=} at line number {index}")
            if time_value.upper() != 'PLUS':
                current_date = time_value
            else:
                plus_value = get_expected_token_value(token='PLUS', token_line=line, file_list=file_as_list,
                                                      custom_message="Cannot find the date associated with the TIME "
                                                                     f"PLUS card in {line=} at line number {index}")

                if current_date is None:
                    raise ValueError("Cannot calculate PLUS date without access to the initial date.")
                else:
                    new_datetime = ISODateTime.convert_to_iso(
                        current_date, date_format, start_date) + timedelta(days=float(plus_value))

                if date_format == DateFormat.DD_MM_YYYY:
                    if new_datetime.time() == time(0, 0, 0, 0):
                        current_date = new_datetime.strftime('%d/%m/%Y')
                    else:
                        current_date = new_datetime.strftime('%d/%m/%Y(%H:%M:%S)')
                elif date_format == DateFormat.MM_DD_YYYY:
                    if new_datetime.time() == time(0, 0, 0, 0):
                        current_date = new_datetime.strftime('%m/%d/%Y')
                    else:
                        current_date = new_datetime.strftime('%m/%d/%Y(%H:%M:%S)')
            continue

        if table_start < 0:
            token_found = check_list_tokens(list(table_object_map.keys()), line)
            if token_found is None or check_token('WELLCONTROL', line):
                default_crossflow, default_shutin = __set_crossflow_and_shutin_defaults(default_crossflow,
                                                                                        default_shutin,
                                                                                        file_as_list, index, line)
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
                                        date_format=date_format,
                                        welllists=well_lists,
                                        start_date=start_date)

            elif token_found == 'QMULT' or token_found == 'CONSTRAINT':
                list_objects = load_table_to_objects(file_as_list=file_as_list[table_start:table_end],
                                                     row_object=table_object_map[token_found],
                                                     property_map=property_map,
                                                     current_date=current_date,
                                                     unit_system=unit_system,
                                                     constraint_obj_dict=nexus_constraints,
                                                     preserve_previous_object_attributes=True,
                                                     date_format=date_format,
                                                     welllists=well_lists,
                                                     start_date=start_date)

            elif token_found in [NexusWellLists.table_header(), NexusConLists.table_header()]:
                list_objects = load_table_to_lists(file_as_list=file_as_list[table_start - 1:table_end],
                                                   row_object=table_object_map[token_found],
                                                   table_header=token_found,
                                                   current_date=current_date,
                                                   previous_lists=nexus_object_results[token_found],
                                                   date_format=date_format)

                # If there is already a matching Welllist for this timestamp, update that with the additional changes,
                # rather than adding another one.
                existing_welllist = next(
                    (x for x in nexus_object_results[NexusWellLists.table_header()] if
                     x.name == list_objects[0][0].name and
                     x.date == list_objects[0][0].date), None)

                if existing_welllist is not None:
                    existing_welllist.elements_in_the_list = list_objects[0][0].wells
                    list_objects = []
                if token_found == NexusWellLists.table_header():
                    well_lists = [x[0] for x in list_objects]

            else:
                list_objects = load_table_to_objects(file_as_list=file_as_list[table_start:table_end],
                                                     row_object=table_object_map[token_found],
                                                     property_map=property_map,
                                                     current_date=current_date,
                                                     unit_system=unit_system, date_format=date_format,
                                                     well_names=well_names, start_date=start_date)

            # store objects found into right dictionary
            list_of_token_obj = nexus_object_results[token_found]
            # This statement ensures that CONSTRAINTs that are found in tables are actually added to the dictionary
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
                # wildcards do not apply to LIST type nexus objects like WELLLIST.
                if 'LIST' not in token_found:
                    network_names.extend([x.name for x in list_of_token_obj])
                if token_found == 'WELLS':
                    well_names.extend([x.name for x in list_of_token_obj if x.name not in well_names])
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

        if 'WELLS' in nexus_object_results.keys():
            __apply_default_connection_values(nexus_object_results=nexus_object_results,
                                              default_crossflow=default_crossflow, default_shutin=default_shutin)

    return nexus_object_results, nexus_constraints


def __set_crossflow_and_shutin_defaults(default_crossflow: Optional[str], default_shutin: Optional[str],
                                        file_as_list: list[str], index: int, line: str) -> tuple[Optional[str],
                                                                                                 Optional[str]]:
    """Sets the default values for Crossflow and Shutin."""
    if check_token(token='CROSSFLOW', line=line):
        crossflow_value = get_expected_token_value(token='CROSSFLOW', token_line=line,
                                                   file_list=file_as_list[index:])

        default_crossflow = crossflow_value
    if check_token(token='SHUTINON', line=line):
        default_shutin = 'ON'
    elif check_token(token='SHUTINOFF', line=line):
        default_shutin = 'OFF'
    elif check_token(token='SHUTIN_CELLGRAD', line=line):
        default_shutin = 'CELLGRAD'
    return default_crossflow, default_shutin


def __apply_default_connection_values(nexus_object_results: dict[str, list[Any]], default_crossflow: Optional[str],
                                      default_shutin: Optional[str]) -> None:
    """Applies the values for Crossflow from the defaults if they aren't set separately in a table."""
    all_connections = nexus_object_results['WELLS'] + nexus_object_results['GASWELLS']
    for connection in all_connections:
        if connection.crossflow is None:
            connection.crossflow = default_crossflow
        if connection.crossshut is None:
            connection.crossshut = default_shutin


def __activate_deactivate_checks(line: str, is_activate_block: bool,
                                 is_deactivate_block: bool, current_date: str, start_date: str | None,
                                 date_format: DateFormat, nexus_object_results: dict[str, list[Any]]) \
        -> tuple[bool, bool, bool]:
    """Checks if the line being read is the start of an activate / deactivate block, and if it is, sets the property on
    the related Wellconnection objects found.

    Returns:
    tuple[bool, bool, bool]: a tuple of three bools, stating whether the following text is an activate block, whether \
        it is a deactivate block, and whether the loop calling this method should continue to the next line.
    """
    # Handle activation / deactivation of well connections
    if check_token('DEACTIVATE', line):
        is_deactivate_block = True
        return is_activate_block, is_deactivate_block, True

    if check_token('ACTIVATE', line):
        is_activate_block = True
        return is_activate_block, is_deactivate_block, True

    if not is_activate_block and not is_deactivate_block:
        return is_activate_block, is_deactivate_block, False

    if check_token('CONNECTION', line):
        return is_activate_block, is_deactivate_block, True

    if check_token('ENDDEACTIVATE', line) or check_token('ENDACTIVATE', line):
        is_deactivate_block = False
        is_activate_block = False
        return is_activate_block, is_deactivate_block, True

    # loop through all the connection names found in the block, and create the ActivationChange objects.
    found_connections = []
    affected_connection_name = get_next_value(start_line_index=0, file_as_list=[line])

    # Get a list of all the distinct connection names that might be affected.
    all_well_connection_names = []
    connection_types = {'WELLS', 'GASWELLS', 'NODECON'} & set(nexus_object_results)
    for connection_type in connection_types:
        all_well_connection_names.extend([connection.name for
                                          connection in nexus_object_results[connection_type]])
    all_well_connections = list(dict.fromkeys(all_well_connection_names))

    while affected_connection_name is not None:
        change = ActivationChangeEnum.ACTIVATE if is_activate_block else ActivationChangeEnum.DEACTIVATE
        # If a wildcard is found, ensure that all connections that match the wildcard are dealt with.
        if '*' in affected_connection_name:
            all_affected_well_connections = [x for x in all_well_connections if
                                             fnmatch.fnmatch(x.casefold(), affected_connection_name.casefold())]

            # Create an object for each affected connection
            for connection in all_affected_well_connections:
                new_activation_change = NexusActivationChange(change=change, name=connection,
                                                              date=current_date,
                                                              start_date=start_date, date_format=date_format)
                nexus_object_results['ACTIVATE_DEACTIVATE'].append(new_activation_change)

        else:
            new_activation_change = NexusActivationChange(change=change, name=affected_connection_name,
                                                          date=current_date, start_date=start_date,
                                                          date_format=date_format)
            nexus_object_results['ACTIVATE_DEACTIVATE'].append(new_activation_change)

        found_connections.append(affected_connection_name)
        # Move to the next value
        affected_connection_name = get_next_value(start_line_index=0, file_as_list=[line],
                                                  ignore_values=found_connections)

    return is_activate_block, is_deactivate_block, False
