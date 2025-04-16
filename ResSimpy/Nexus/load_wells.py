from __future__ import annotations

import warnings
from typing import Optional, TYPE_CHECKING
from datetime import time, timedelta

from ResSimpy.Time.ISODateTime import ISODateTime
from ResSimpy.Nexus.DataModels.NexusWellMod import NexusWellMod
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
import ResSimpy.Nexus.nexus_file_operations as nfo
import ResSimpy.FileOperations.file_operations as fo
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.NexusCompletion import NexusCompletion
from ResSimpy.Nexus.DataModels.NexusRelPermEndPoint import NexusRelPermEndPoint
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.NexusKeywords.wells_keywords import WELLS_KEYWORDS
from ResSimpy.Utils.invert_nexus_map import nexus_keyword_to_attribute_name

from ResSimpy.Nexus.DataModels.NexusWell import NexusWell

if TYPE_CHECKING:
    from ResSimpy.Nexus.NexusWells import NexusWells


def load_wells(nexus_file: NexusFile, start_date: str, default_units: UnitSystem, parent_wells_instance: NexusWells,
               model_date_format: DateFormat) -> tuple[list[NexusWell], DateFormat]:
    """Loads a list of Nexus Well instances and populates it with the wells completions over time from a wells file.

    Args:
        nexus_file (NexusFile): NexusFile containing the wellspec files.
        start_date (str): starting date of the wellspec file as a string.
        default_units (UnitSystem): default units to use if no units are found.
        parent_wells_instance (NexusWells): The NexusWells object this function will load the wells into.
        model_date_format (DateFormat): Date format specified in the FCS file.

    Raises:
        ValueError: If no value is found after a TIME card.
        ValueError: If no well name is found after a WELLSPEC keyword.
        ValueError: If no valid wells are found in the wellspec file.

    Returns:
        A tuple containing:
        list[NexusWell]: list of Nexus well classes contained within a wellspec file.
        DateFormat: The date format found in the wellspec file if present, otherwise just the model date format.
    """
    date_format = model_date_format
    file_as_list = nexus_file.get_flat_list_str_file
    well_name: Optional[str] = None
    wellspec_file_units: Optional[UnitSystem] = None

    iw: Optional[str] = None
    jw: Optional[str] = None
    kw: Optional[str] = None
    md: Optional[str] = None
    skin: Optional[str] = None
    depth: Optional[str] = None
    x_value: Optional[str] = None
    y_value: Optional[str] = None
    angla: Optional[str] = None
    anglv: Optional[str] = None
    grid: Optional[str] = None
    wi: Optional[str] = None
    dtop: Optional[str] = None
    dbot: Optional[str] = None
    partial_perf: Optional[str] = None
    well_radius: Optional[str] = None

    perm_thickness_ovr: Optional[str] = None
    dfactor: Optional[str] = None
    rel_perm_method: Optional[str] = None
    status: Optional[str] = None

    cell_number: Optional[str] = None
    peaceman_well_block_radius: Optional[str] = None
    portype: Optional[str] = None
    fracture_mult: Optional[str] = None
    sector: Optional[str] = None
    well_group: Optional[str] = None
    zone: Optional[str] = None
    angle_open_flow: Optional[str] = None
    temperature: Optional[str] = None
    flowsector: Optional[str] = None
    parent_node: Optional[str] = None
    mdcon: Optional[str] = None
    pressure_avg_pattern: Optional[str] = None
    length: Optional[str] = None
    permeability: Optional[str] = None
    non_darcy_model: Optional[str] = None
    comp_dz: Optional[str] = None
    layer_assignment: Optional[str] = None
    polymer_bore_radius: Optional[str] = None
    polymer_well_radius: Optional[str] = None
    perm_thickness_mult: Optional[float] = None

    # End point values:
    swl: Optional[str] = None
    swr: Optional[str] = None
    swu: Optional[str] = None
    sgl: Optional[str] = None
    sgr: Optional[str] = None
    sgu: Optional[str] = None
    swro: Optional[str] = None
    sgro: Optional[str] = None
    sgrw: Optional[str] = None
    krw_swro: Optional[str] = None
    krw_swu: Optional[str] = None
    krg_sgro: Optional[str] = None
    krg_sgu: Optional[str] = None
    kro_swl: Optional[str] = None
    kro_swr: Optional[str] = None
    kro_sgl: Optional[str] = None
    kro_sgr: Optional[str] = None
    krw_sgl: Optional[str] = None
    krw_sgr: Optional[str] = None
    krg_sgrw: Optional[str] = None
    sgtr: Optional[str] = None
    sotr: Optional[str] = None
    header_values: dict[str, None | int | float | str] = {
        'IW': iw, 'JW': jw, 'L': kw, 'MD': md, 'SKIN': skin, 'DEPTH': depth, 'X': x_value, 'Y': y_value,
        'ANGLA': angla, 'ANGLV': anglv, 'GRID': grid, 'WI': wi, 'DTOP': dtop, 'DBOT': dbot, 'RADW': well_radius,
        'PPERF': partial_perf, 'CELL': cell_number, 'KH': perm_thickness_ovr, 'D': dfactor, 'IRELPM': rel_perm_method,
        'STAT': status, 'RADB': peaceman_well_block_radius, 'PORTYPE': portype, 'FM': fracture_mult, 'SECT': sector,
        'GROUP': well_group, 'ZONE': zone, 'ANGLE': angle_open_flow, 'TEMP': temperature, 'FLOWSECT': flowsector,
        'PARENT': parent_node, 'MDCON': mdcon, 'IPTN': pressure_avg_pattern, 'LENGTH': length, 'K': permeability,
        'ND': non_darcy_model, 'DZ': comp_dz, 'LAYER': layer_assignment, 'RADBP': polymer_bore_radius,
        'RADWP': polymer_well_radius, 'KHMULT': perm_thickness_mult
    }
    end_point_scaling_header_values: dict[str, None | int | float | str] = {
        'SWL': swl, 'SWR': swr, 'SWU': swu, 'SGL': sgl, 'SGR': sgr, 'SGU': sgu,
        'SWRO': swro, 'SGRO': sgro, 'SGRW': sgrw, 'KRW_SWRO': krw_swro, 'KRW_SWU': krw_swu, 'KRG_SGRO': krg_sgro,
        'KRG_SGU': krg_sgu, 'KRO_SWL': kro_swl, 'KRO_SWR': kro_swr, 'KRO_SGL': kro_sgl, 'KRO_SGR': kro_sgr,
        'KRW_SGL': krw_sgl, 'KRW_SGR': krw_sgr, 'KRG_SGRW': krg_sgrw, 'SGTR': sgtr, 'SOTR': sotr,
    }
    # add end point scaling header to the header values we search for:
    header_values.update(end_point_scaling_header_values)

    header_index: int = -1
    wellspec_found: bool = False
    current_date: str = start_date
    wells: list[NexusWell] = [] if parent_wells_instance._wells is None else parent_wells_instance._wells
    well_name_list: list[str] = [x.well_name.upper() for x in parent_wells_instance._wells]

    exclude_section: bool = False

    for index, line in enumerate(file_as_list):
        uppercase_line = line.upper()

        trimmed_line = line.strip()

        if trimmed_line.startswith('!') or nfo.get_next_value(0, [trimmed_line]) is None:
            continue

        if len(trimmed_line) > 0 and trimmed_line[0] == '[':
            exclude_section = True

        if exclude_section:
            if ']' in trimmed_line and trimmed_line[0] != '!' and trimmed_line[0] != 'C':
                exclude_section = False
            else:
                continue

        # If we haven't got the units yet, check to see if this line contains a declaration for them.
        if wellspec_file_units is None:
            for unit in UnitSystem:
                if unit.value in uppercase_line and (line.find('!') > line.find(unit.value) or line.find('!') == -1):
                    wellspec_file_units = unit

        if nfo.check_token('DATEFORMAT', line):
            new_date_format_str = fo.get_token_value(token='DATEFORMAT', token_line=line, file_list=file_as_list)

            if new_date_format_str is None:
                raise ValueError(f"Cannot find the date format associated with the DATEFORMAT card in {line=} at line"
                                 f" number {index}")

            model_date_format_str = model_date_format.name.replace('_', '/')
            if new_date_format_str != model_date_format_str:
                warnings.warn(f"Wells date format of {new_date_format_str} inconsistent with base model format of "
                              f"{model_date_format_str}")

            converted_format_str = new_date_format_str.replace('/', '_')

            if not hasattr(DateFormat, converted_format_str):
                raise ValueError(f"Invalid Date Format found: '{new_date_format_str}' at line {index}")

            date_format = DateFormat[converted_format_str]

        if nfo.check_token('TIME', line):
            time_value = fo.get_expected_token_value(token='TIME', token_line=line, file_list=file_as_list,
                                                     custom_message="Cannot find the date associated with the TIME "
                                                                    f"card in {line=} at line number {index}")
            if time_value.upper() != 'PLUS':
                current_date = time_value
            else:
                plus_value = fo.get_expected_token_value(token='PLUS', token_line=line, file_list=file_as_list,
                                                         custom_message="Cannot find the date associated with the TIME "
                                                         f"PLUS card in {line=} at line number {index}")
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

        if nfo.check_token('WELLMOD', line):
            wellmod = __get_inline_well_mod(line, current_date=current_date, unit_system=wellspec_file_units,
                                            wells_loaded=wells, start_date=start_date, date_format=date_format)
            wellmodname = wellmod.well_name
            if wellmodname.upper() not in well_name_list:
                warnings.warn(f"Cannot find well name '{wellmodname}' in wellspec file: '{nexus_file.location}'")
            else:
                wells[well_name_list.index(wellmodname.upper())].wellmods.append(wellmod)

        if nfo.check_token('WELLSPEC', uppercase_line):
            initial_well_name = nfo.get_expected_token_value(token='WELLSPEC', token_line=line, file_list=file_as_list,
                                                             custom_message="Cannot find well name following WELLSPEC "
                                                                            "keyword")
            well_name = initial_well_name.strip('\"')
            wellspec_found = True
            continue

        # Load in the column headings, which appear after the well name
        header_index, headers = __load_wellspec_table_headings(header_index, header_values, index, line, well_name)

        if header_index == -1:
            continue

        if well_name is None:
            raise ValueError(f"No wells found in file: {nexus_file.location}")

        if wellspec_found:
            if current_date is None:
                current_date = start_date
            # reset the storage dictionary to prevent completion properties being carried forward from earlier timestep
            header_values = {k: None for k in header_values}
            if wellspec_file_units is None:
                wellspec_file_units = default_units

            # Load in each line of the table
            completions = __load_wellspec_table_completions(
                nexus_file, header_index, header_values, headers, current_date, end_point_scaling_header_values,
                date_format, unit_system=wellspec_file_units, start_date=start_date)

            if well_name.upper() in well_name_list:
                wells[well_name_list.index(well_name.upper())].completions.extend(completions)
            else:
                new_well = NexusWell(completions=completions, well_name=well_name, unit_system=wellspec_file_units,
                                     wellmods=[], parent_wells_instance=parent_wells_instance)
                well_name_list.append(well_name.upper())
                wells.append(new_well)
            wellspec_found = False
            header_index = -1
    return wells, date_format


def __load_wellspec_table_completions(nexus_file: NexusFile, header_index: int,
                                      header_values: dict[str, None | int | float | str],
                                      headers: list[str], date: str,
                                      end_point_scaling_header_values: dict[str, None | int | float | str],
                                      date_format: DateFormat,
                                      unit_system: UnitSystem,
                                      start_date: None | str = None,
                                      ) -> list[NexusCompletion]:
    """Loads a completion table in for a single WELLSPEC keyword.

        Loads in the next available completions following a WELLSPEC keyword and a header line.

    Args:
        nexus_file (NexusFile): The Nexus file containing the completions.
        header_index (int): index number of the header in the file as list parameter
        header_values (dict[str, Union[Optional[int], Optional[float], Optional[str]]]): dictionary of column \
            headings to populate from the table
        headers (list[str]): list of strings containing the headers from the wellspec table
        date (str): date to populate the completion class with.
        end_point_scaling_header_values (dict): dictionary containing the header values for thes special end point
        scaling columns.
        date_format (DateFormat): date format as a DateFormat Enum to use for the completion.
        unit_system (UnitSystem): unit system as a UnitSystem Enum to use for the completion.
        start_date (Optional[str]): start date of the model.

    Returns:
        list[NexusCompletion]: list of nexus completions for a given table.
    """

    def convert_header_value_float(key: str) -> Optional[float]:
        value = header_values[key]
        if value == 'NA':
            value = None
        if value is None:
            return None
        try:
            value = float(value)
        except ValueError:
            warnings.warn(f"Cannot convert {value=} to float")
            value = None
        return value

    def convert_header_value_int(key: str) -> Optional[int]:
        value = header_values[key]
        if value == 'NA':
            value = None
        return None if value is None else int(value)

    completions: list[NexusCompletion] = []
    file_as_list: list[str] = nexus_file.get_flat_list_str_file

    exclude_section = False

    for index, line in enumerate(file_as_list[header_index + 1:]):
        # check for end of table lines:
        # TODO update with a more robust table end checker function
        end_of_table = nfo.nexus_token_found(line, WELLS_KEYWORDS)
        if end_of_table:
            return completions

        trimmed_line = line.strip()

        # Exclude block comments
        if len(trimmed_line) > 0 and trimmed_line[0] == '[':
            exclude_section = True

        if exclude_section:
            if ']' in trimmed_line and trimmed_line[0] != '!' and trimmed_line[0] != 'C':
                exclude_section = False
                continue
            else:
                continue

        valid_line, header_values = nfo.table_line_reader(header_values, headers, line)
        # if a valid line is found load a completion otherwise continue
        if not valid_line:
            continue

        # create a rel perm end point scaling object if it exists for a given completion
        rel_perm_dict = {key.lower(): convert_header_value_float(key) for key
                         in header_values if key in end_point_scaling_header_values}
        if any(rel_perm_dict.values()):
            new_rel_perm_end_point = NexusRelPermEndPoint(**rel_perm_dict)
        else:
            new_rel_perm_end_point = None

        new_completion = NexusCompletion(
            date=date,
            i=convert_header_value_int('IW'),
            j=convert_header_value_int('JW'),
            k=convert_header_value_int('L'),
            skin=convert_header_value_float('SKIN'),
            depth=convert_header_value_float('DEPTH'),
            well_radius=convert_header_value_float('RADW'),
            x=convert_header_value_float('X'),
            y=convert_header_value_float('Y'),
            angle_a=convert_header_value_float('ANGLA'),
            angle_v=convert_header_value_float('ANGLV'),
            grid=(None if header_values['GRID'] is None else str(header_values['GRID'])),
            measured_depth=convert_header_value_float('MD'),
            well_indices=convert_header_value_float('WI'),
            depth_to_top=convert_header_value_float('DTOP'),
            depth_to_bottom=convert_header_value_float('DBOT'),
            depth_to_top_str=(None if header_values['DTOP'] is None else str(header_values['DTOP'])),
            depth_to_bottom_str=(None if header_values['DBOT'] is None else str(header_values['DBOT'])),
            rel_perm_method=convert_header_value_int('IRELPM'),
            dfactor=convert_header_value_float('D'),
            status=(None if header_values['STAT'] is None else str(header_values['STAT'])),
            partial_perf=convert_header_value_float('PPERF'),
            cell_number=convert_header_value_int('CELL'),
            perm_thickness_ovr=convert_header_value_float('KH'),
            peaceman_well_block_radius=convert_header_value_float('RADB'),
            fracture_mult=convert_header_value_float('FM'),
            sector=convert_header_value_int('SECT'),
            well_group=(None if header_values['GROUP'] is None else str(header_values['GROUP'])),
            zone=convert_header_value_int('ZONE'),
            angle_open_flow=convert_header_value_float('ANGLE'),
            temperature=convert_header_value_float('TEMP'),
            flowsector=convert_header_value_int('FLOWSECT'),
            parent_node=(None if header_values['PARENT'] is None else str(header_values['PARENT'])),
            mdcon=convert_header_value_float('MDCON'),
            pressure_avg_pattern=convert_header_value_int('IPTN'),
            length=convert_header_value_float('LENGTH'),
            permeability=convert_header_value_float('K'),
            non_darcy_model=(None if header_values['ND'] is None else str(header_values['ND'])),
            comp_dz=convert_header_value_float('DZ'),
            layer_assignment=convert_header_value_int('LAYER'),
            polymer_bore_radius=convert_header_value_float('RADBP'),
            polymer_well_radius=convert_header_value_float('RADWP'),
            portype=(None if header_values['PORTYPE'] is None else str(header_values['PORTYPE'])),
            rel_perm_end_point=new_rel_perm_end_point,
            perm_thickness_mult=convert_header_value_float('KHMULT'),
            date_format=date_format,
            unit_system=unit_system,
            start_date=start_date,
        )

        nexus_file.add_object_locations(new_completion.id, [index + header_index + 1])

        completions.append(new_completion)

    return completions


def __load_wellspec_table_headings(header_index: int, header_values: dict[str, None | int | float | str],
                                   index: int, line: str, well_name: Optional[str],
                                   headers: Optional[list[str]] = None) -> tuple[int, list[str]]:
    """Loads in the wellspec headers from a line in a file.

    Args:
        header_index (int): index of the header
        header_values (dict[str, Union[Optional[int], Optional[float], Optional[str]]]): dictionary of column \
            headings to populate from the table
        index (int): starting index to search from
        line (str): line to extract header values from
        well_name (Optional[str]): well name from the previous WELLSPEC keyword
        headers (Optional[list[str]], optional): list of headers to append the next set of found headers to. \
            Defaults to None and will create a new list to return if None.

    Returns:
        tuple[int, list[str]]: index in the file as list for the header, list of headers found in the file
    """
    headers = [] if headers is None else headers
    next_column_heading: Optional[str]
    if well_name is None:
        return header_index, headers

    for key in header_values.keys():
        if nfo.check_token(key, line):
            header_line = line.upper()
            header_index = index
            # Map the headers (first time get the expected value as check token guarantees at least 1 value)
            next_column_heading = fo.get_expected_next_value(start_line_index=0, file_as_list=[line]).upper()
            trimmed_line = header_line

            while next_column_heading is not None:
                headers.append(next_column_heading)
                trimmed_line = trimmed_line.replace(next_column_heading, "", 1)
                next_column_heading = nfo.get_next_value(0, [trimmed_line], trimmed_line)

            if len(headers) > 0:
                break
    return header_index, headers


def __get_inline_well_mod(line: str, current_date: str, unit_system: UnitSystem | None,
                          wells_loaded: list[NexusWell], start_date: str, date_format: DateFormat) -> NexusWellMod:
    """Returns a NexusWellMod object from a WELLMOD line. e.g. `WELLMOD well_name KH CON value`.

    Args:
        line (str): line to extract the wellmod from
        current_date (str): current date in the file
        unit_system (UnitSystem | None): Unit system enum
        wells_loaded (list[NexusWell]): list of wells loaded, used for determining the number of completions in the well
        start_date (str): The model start date.
        date_format (DateFormat): The date format.
    """
    keyword_mapping = NexusWellMod.get_keyword_mapping()
    next_value = nfo.get_next_value(0, [line], line)
    counter = 0
    prop: None | str = None
    method: None | str = None
    well_mod_dict: dict[str, None | float | int | str | list[float]] = \
        {'date': current_date, 'unit_system': unit_system}
    trimmed_line = line
    name_for_well_mod: None | str = None
    while next_value is not None:
        if next_value.upper() == 'WELLMOD':
            pass
        elif counter == 1:
            name_for_well_mod = next_value
            well_mod_dict.update({'well_name': name_for_well_mod})
        elif counter == 2:
            prop = next_value
        elif counter == 3:
            method = next_value
        elif counter == 4:
            if method is not None and method.upper() == 'VAR':
                var_array: list[float] = []
                current_datetime_as_iso: ISODateTime = ISODateTime.convert_to_iso(current_date, date_format, start_date)
                number_completions = __get_number_completions(well_name=name_for_well_mod,
                                                              wells_loaded=wells_loaded, line=line,
                                                              current_iso_date=current_datetime_as_iso)
                completion_counter = 0
                while completion_counter < number_completions:
                    next_value = fo.get_expected_next_value(0, [trimmed_line], trimmed_line)
                    if '*' in next_value:
                        vect_length, vect_value = next_value.split('*', 1)
                        var_array.extend([float(vect_value)] * int(vect_length))
                        completion_counter += int(vect_length)
                    else:
                        var_array.append(float(next_value))
                        completion_counter += 1
                    if completion_counter != number_completions:
                        trimmed_line = trimmed_line.replace(next_value, "", 1)
                value_found: list[float] | float = var_array.copy()
                if next_value is None:
                    raise ValueError(f"Cannot find value for {prop=} in {line=}")
            else:
                value_found = float(next_value)
            if prop is None:
                raise ValueError(f"Cannot find property name for value {value_found} in {line=}")
            attribute_name = nexus_keyword_to_attribute_name(keyword_mapping, prop)
            well_mod_dict.update({attribute_name: value_found})
            # reset the counter for the next property
            counter = 1

        trimmed_line = trimmed_line.replace(next_value, "", 1)
        next_value = nfo.get_next_value(0, [trimmed_line], trimmed_line)
        counter += 1

    return NexusWellMod(wellmod_dict=well_mod_dict, date=current_date, date_format=date_format, start_date=start_date)


def __get_number_completions(well_name: str | None, current_iso_date: ISODateTime, wells_loaded: list[NexusWell],
                             line: str) -> int:
    """Returns the number of completions for a given well name.

    Args:
        well_name (str | None): name of the well to find the number of completions for
        current_date (str): current date in the file
        wells_loaded (list[NexusWell]): list of wells loaded, used for determining the number of completions in the well
        current_iso_date (ISODateTime): The date of the completion in ISO format.
        line (str): The line in the file.

    Returns:
        int: number of completions for a given well name.
    """
    if well_name is None:
        raise ValueError(f"No well name found for the wellmod in the wellspec file in line:\n{line}")
    number_completions = 0
    for well in wells_loaded:
        if well.well_name.upper() != well_name.upper():
            continue

        completion_dates = [x.iso_date for x in well.completions if x.iso_date is not None and x.iso_date
                            <= current_iso_date]
        # get the most recent completions
        number_completions = len([x for x in completion_dates if x == max(completion_dates)])
        break

    return number_completions
