from typing import Optional, Union

import ResSimpy.Nexus.nexus_file_operations as nfo
from ResSimpy.Nexus.DataModels.NexusWell import NexusWell
from ResSimpy.Nexus.DataModels.NexusCompletion import NexusCompletion
from ResSimpy.UnitsEnum import Units


def load_wells(wellspec_file_path: str, start_date: str, default_units: Units) -> list[NexusWell]:
    file_as_list = nfo.load_file_as_list(wellspec_file_path)

    well_name: Optional[str] = None
    wellspec_file_units: Optional[Units] = None
    completions: list[NexusCompletion] = []
    headers: list[str] = []

    iw: Optional[str] = None
    jw: Optional[str] = None
    kw: Optional[str] = None
    well_radius: Optional[str] = None
    units_values: dict[str, Units] = {'ENGLISH': Units.OILFIELD, 'METRIC': Units.METRIC_KPA,
                                      'METKG/CM2': Units.METRIC_KGCM2, 'METBAR': Units.METRIC_BARS, 'LAB': Units.LAB}
    header_values: dict[str, Union[Optional[int], Optional[float], Optional[str]]] = {'IW': iw, 'JW': jw, 'L': kw,
                                                                                      'RADW': well_radius}
    header_index = -1

    for index, line in enumerate(file_as_list):
        uppercase_line = line.upper()

        # If we haven't got the units yet, check to see if this line contains a declaration for them.
        if wellspec_file_units is None:
            for key in units_values.keys():
                if key in uppercase_line and (line.find('!') > line.find(key) or line.find('!') == -1):
                    wellspec_file_units = units_values[key]

        if 'WELLSPEC' in uppercase_line:
            initial_well_name = nfo.get_token_value(token='WELLSPEC', token_line=line, file_list=file_as_list)
            if initial_well_name is None:
                raise ValueError("Cannot find well name following WELLSPEC keyword")
            well_name = initial_well_name.strip('\"')
            continue

        # Load in the column headings, which appear after the well name
        header_index = __load_wellspec_table_headings(header_index, header_values, headers, index, line, well_name)

        if header_index != -1:
            break

    if well_name is None:
        raise ValueError(f"No wells found in file: {wellspec_file_path}")

    # Load in each line of the table
    completions = __load_wellspec_table_completions(file_as_list, header_index, header_values, headers, start_date)

    if wellspec_file_units is None:
        wellspec_file_units = default_units

    wells = [NexusWell(completions=completions, well_name=well_name, units=wellspec_file_units)]
    return wells


def __load_wellspec_table_completions(file_as_list, header_index, header_values, headers, start_date):
    completions: list[NexusCompletion] = []

    for line in file_as_list[header_index + 1:]:
        trimmed_line = line
        valid_line = True
        for column in headers:
            value = nfo.get_next_value(0, [trimmed_line], trimmed_line)
            if value is None:
                valid_line = False
                break

            header_values[column] = value
            trimmed_line = trimmed_line.replace(value, "", 1)

        if valid_line:
            new_completion = NexusCompletion(i=(None if header_values['IW'] is None else int(header_values['IW'])),
                                             j=(None if header_values['JW'] is None else int(header_values['JW'])),
                                             k=(None if header_values['L'] is None else int(header_values['L'])),
                                             well_radius=(None if header_values['RADW'] is None else float(
                                                 header_values['RADW'])),
                                             date=start_date)

            completions.append(new_completion)

    return completions


def __load_wellspec_table_headings(header_index: int,
                                   header_values: dict[str, Union[Optional[int], Optional[float], Optional[str]]],
                                   headers: list[str], index: int, line: str, well_name: Optional[str]) -> int:
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
    return header_index
