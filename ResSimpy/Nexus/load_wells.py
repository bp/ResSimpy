from typing import Optional

import ResSimpy.Nexus.nexus_file_operations as nfo
from ResSimpy.Nexus.DataModels.NexusWell import NexusWell
from ResSimpy.Nexus.DataModels.NexusCompletion import NexusCompletion
from ResSimpy.UnitsEnum import Units


def load_wells(wellspec_file_path: str, start_date: str, default_units: Units) -> list[NexusWell]:
    """Loads a list of Nexus Well instances and populates it with the wells completions over time from a wells file
    Args:
        wellspec_file_path (str): file path to the wellspec file to read.
        start_date (str): starting date of the wellspec file as a string.
        default_units (Units): default units to use if no units are found.
    Raises:
        ValueError: If no value is found after a TIME card.
        ValueError: If no well name is found after a WELLSPEC keyword.
        ValueError: If no valid wells are found in the wellspec file.

    Returns:
        list[NexusWell]: list of Nexus well classes contained within a wellspec file.
    """

    file_as_list = nfo.load_file_as_list(wellspec_file_path)
    well_name: Optional[str] = None
    wellspec_file_units: Optional[Units] = None
    completions: list[NexusCompletion] = []
    headers: list[str] = []

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
    units_values: dict[str, Units] = {'ENGLISH': Units.OILFIELD, 'METRIC': Units.METRIC_KPA,
                                      'METKG/CM2': Units.METRIC_KGCM2, 'METBAR': Units.METRIC_BARS, 'LAB': Units.LAB}
    header_values: dict[str, None | int | float | str] = {
        'IW': iw, 'JW': jw, 'L': kw, 'MD': md, 'SKIN': skin, 'DEPTH': depth, 'X': x_value, 'Y': y_value,
        'ANGLA': angla, 'ANGLV': anglv, 'GRID': grid, 'WI': wi, 'DTOP': dtop, 'DBOT': dbot, 'RADW': well_radius,
        'PPERF': partial_perf}
    header_index: int = -1
    wellspec_found: bool = False
    current_date: Optional[str] = None
    wells: list[NexusWell] = []
    well_name_list: list[str] = []

    for index, line in enumerate(file_as_list):
        uppercase_line = line.upper()

        # If we haven't got the units yet, check to see if this line contains a declaration for them.
        if wellspec_file_units is None:
            for key in units_values.keys():
                if key in uppercase_line and (line.find('!') > line.find(key) or line.find('!') == -1):
                    wellspec_file_units = units_values[key]

        if nfo.check_token('TIME', line):
            current_date = nfo.get_token_value(token='TIME', token_line=line, file_list=file_as_list)
            if current_date is None:
                raise ValueError(f"Cannot find the date associated with the TIME card in {line=} at line number \
                                 {index}")

        if 'WELLSPEC' in uppercase_line:
            initial_well_name = nfo.get_token_value(token='WELLSPEC', token_line=line, file_list=file_as_list)
            if initial_well_name is None:
                raise ValueError("Cannot find well name following WELLSPEC keyword")
            well_name = initial_well_name.strip('\"')
            wellspec_found = True
            continue

        if well_name is None:
            raise ValueError(f"No wells found in file: {wellspec_file_path}")

        # Load in the column headings, which appear after the well name
        header_index, headers = __load_wellspec_table_headings(header_index, header_values, index, line, well_name)

        if header_index == -1:
            continue

        if wellspec_found:
            if current_date is None:
                current_date = start_date
            # Load in each line of the table
            completions = __load_wellspec_table_completions(
                file_as_list, header_index, header_values, headers, current_date)

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


def __load_wellspec_table_completions(file_as_list: list[str], header_index: int,
                                      header_values: dict[str, None | int | float | str],
                                      headers: list[str], start_date: str) -> list[NexusCompletion]:
    """Loads a completion table in for a single WELLSPEC keyword. \
        Loads in the next available completions following a WELLSPEC keyword and a header line.

    Args:
        file_as_list (list[str]): File represented as a list of strings
        header_index (int): index number of the header in the file as list parameter
        header_values (dict[str, Union[Optional[int], Optional[float], Optional[str]]]): dictionary of column \
            headings to populate from the table
        headers (list[str]): list of strings containing the headers from the wellspec table
        start_date (str): date to populate the completion class with.

    Returns:
        list[NexusCompletion]: list of nexus completions for a given table.
    """
    def convert_header_value_float(key: str, header_values=header_values) -> Optional[float]:
        value = header_values[key]
        if value == 'NA':
            value = None
        return None if value is None else float(value)

    def convert_header_value_int(key, header_values=header_values) -> Optional[int]:
        value = header_values[key]
        if value == 'NA':
            value = None
        return None if value is None else int(value)

    completions: list[NexusCompletion] = []

    for line in file_as_list[header_index + 1:]:
        # check for end of table lines:
        end_of_table = nfo.check_token('TIME', line) or nfo.check_token('WELLSPEC', line)
        if end_of_table:
            return completions
        trimmed_line = line
        valid_line = True
        for column in headers:
            value = nfo.get_next_value(0, [trimmed_line], trimmed_line)
            if value is None:
                valid_line = False
                break

            header_values[column] = value
            trimmed_line = trimmed_line.replace(value, "", 1)
        # if a valid line is found load a completion otherwise continue
        if not valid_line:
            continue
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
            date=start_date,
        )

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
        tuple[int, list[str]]: _description_
    """
    headers = [] if headers is None else headers

    if well_name is not None:
        for key in header_values.keys():
            if nfo.check_token(key, line):
                header_line = line
                header_index = index
                # Map the headers
                next_column_heading = nfo.get_next_value(start_line_index=0, file_as_list=[line],
                                                         search_string=line)
                trimmed_line = header_line

                while next_column_heading is not None:
                    headers.append(next_column_heading)
                    trimmed_line = trimmed_line.replace(next_column_heading, "", 1)
                    next_column_heading = nfo.get_next_value(index, [trimmed_line], trimmed_line)

                if len(headers) > 0:
                    break
    return header_index, headers
