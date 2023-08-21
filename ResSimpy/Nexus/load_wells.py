from __future__ import annotations
from typing import Optional
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
import ResSimpy.Nexus.nexus_file_operations as nfo
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.NexusWell import NexusWell
from ResSimpy.Nexus.DataModels.NexusCompletion import NexusCompletion
from ResSimpy.Nexus.DataModels.NexusRelPermEndPoint import NexusRelPermEndPoint
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.NexusKeywords.wells_keywords import WELLS_KEYWORDS


def load_wells(nexus_file: NexusFile, start_date: str, default_units: UnitSystem,
               date_format: DateFormat) -> list[NexusWell]:
    """Loads a list of Nexus Well instances and populates it with the wells completions over time from a wells file.

    Args:
        nexus_file (NexusFile): NexusFile containing the wellspec files.
        start_date (str): starting date of the wellspec file as a string.
        default_units (UnitSystem): default units to use if no units are found.
        date_format (DateFormat): Date format specified in the FCS file.

    Raises:
        ValueError: If no value is found after a TIME card.
        ValueError: If no well name is found after a WELLSPEC keyword.
        ValueError: If no valid wells are found in the wellspec file.

    Returns:
        list[NexusWell]: list of Nexus well classes contained within a wellspec file.
    """

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
    bore_radius: Optional[str] = None
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
    kh_mult: Optional[float] = None

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
        'STAT': status, 'RADB': bore_radius, 'PORTYPE': portype, 'FM': fracture_mult, 'SECT': sector,
        'GROUP': well_group, 'ZONE': zone, 'ANGLE': angle_open_flow, 'TEMP': temperature, 'FLOWSECT': flowsector,
        'PARENT': parent_node, 'MDCON': mdcon, 'IPTN': pressure_avg_pattern, 'LENGTH': length, 'K': permeability,
        'ND': non_darcy_model, 'DZ': comp_dz, 'LAYER': layer_assignment, 'RADBP': polymer_bore_radius,
        'RADWP': polymer_well_radius, 'KHMULT': kh_mult
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
    current_date: Optional[str] = None
    wells: list[NexusWell] = []
    well_name_list: list[str] = []

    for index, line in enumerate(file_as_list):
        uppercase_line = line.upper()

        # If we haven't got the units yet, check to see if this line contains a declaration for them.
        if wellspec_file_units is None:
            for unit in UnitSystem:
                if unit.value in uppercase_line and (line.find('!') > line.find(unit.value) or line.find('!') == -1):
                    wellspec_file_units = unit

        if nfo.check_token('TIME', line):
            current_date = nfo.get_token_value(token='TIME', token_line=line, file_list=file_as_list)
            if current_date is None:
                raise ValueError(f"Cannot find the date associated with the TIME card in {line=} at line number \
                                 {index}")

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
            # Load in each line of the table
            completions = __load_wellspec_table_completions(
                nexus_file, header_index, header_values, headers, current_date, end_point_scaling_header_values,
                date_format)

            if wellspec_file_units is None:
                wellspec_file_units = default_units

            if well_name in well_name_list:
                wells[well_name_list.index(well_name)].completions.extend(completions)
            else:
                new_well = NexusWell(completions=completions, well_name=well_name, units=wellspec_file_units)
                well_name_list.append(well_name)
                wells.append(new_well)
            wellspec_found = False
    return wells


def __load_wellspec_table_completions(nexus_file: NexusFile, header_index: int,
                                      header_values: dict[str, None | int | float | str],
                                      headers: list[str], start_date: str,
                                      end_point_scaling_header_values: dict[str, None | int | float | str],
                                      date_format: DateFormat
                                      ) -> list[NexusCompletion]:
    """Loads a completion table in for a single WELLSPEC keyword. \
        Loads in the next available completions following a WELLSPEC keyword and a header line.

    Args:
        header_index (int): index number of the header in the file as list parameter
        header_values (dict[str, Union[Optional[int], Optional[float], Optional[str]]]): dictionary of column \
            headings to populate from the table
        headers (list[str]): list of strings containing the headers from the wellspec table
        start_date (str): date to populate the completion class with.

    Returns:
        list[NexusCompletion]: list of nexus completions for a given table.
    """

    def convert_header_value_float(key: str) -> Optional[float]:
        value = header_values[key]
        if value == 'NA':
            value = None
        return None if value is None else float(value)

    def convert_header_value_int(key: str) -> Optional[int]:
        value = header_values[key]
        if value == 'NA':
            value = None
        return None if value is None else int(value)

    completions: list[NexusCompletion] = []
    file_as_list: list[str] = nexus_file.get_flat_list_str_file

    for index, line in enumerate(file_as_list[header_index + 1:]):
        # check for end of table lines:
        # TODO update with a more robust table end checker function
        end_of_table = nfo.nexus_token_found(line, WELLS_KEYWORDS)
        if end_of_table:
            return completions
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
            i=convert_header_value_int('IW'),
            j=convert_header_value_int('JW'),
            k=convert_header_value_int('L'),
            # keep grid = 'NA' as 'NA' and not None
            grid=(None if header_values['GRID'] is None else str(header_values['GRID'])),
            well_radius=convert_header_value_float('RADW'),
            measured_depth=convert_header_value_float('MD'),
            skin=convert_header_value_float('SKIN'),
            depth=convert_header_value_float('DEPTH'),
            x=convert_header_value_float('X'),
            y=convert_header_value_float('Y'),
            angle_a=convert_header_value_float('ANGLA'),
            angle_v=convert_header_value_float('ANGLV'),
            well_indices=convert_header_value_float('WI'),
            depth_to_top=convert_header_value_float('DTOP'),
            depth_to_bottom=convert_header_value_float('DBOT'),
            partial_perf=convert_header_value_float('PPERF'),
            cell_number=convert_header_value_int('CELL'),
            perm_thickness_ovr=convert_header_value_float('KH'),
            dfactor=convert_header_value_float('D'),
            rel_perm_method=convert_header_value_int('IRELPM'),
            status=(None if header_values['STAT'] is None else str(header_values['STAT'])),
            bore_radius=convert_header_value_float('RADB'),
            portype=(None if header_values['PORTYPE'] is None else str(header_values['PORTYPE'])),
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
            rel_perm_end_point=new_rel_perm_end_point,
            date=start_date,
            kh_mult=convert_header_value_float('KHMULT'),
            date_format=date_format
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
            next_column_heading = nfo.get_expected_next_value(start_line_index=0, file_as_list=[line]).upper()
            trimmed_line = header_line

            while next_column_heading is not None:
                headers.append(next_column_heading)
                trimmed_line = trimmed_line.replace(next_column_heading, "", 1)
                next_column_heading = nfo.get_next_value(0, [trimmed_line], trimmed_line)

            if len(headers) > 0:
                break
    return header_index, headers
