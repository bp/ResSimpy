from typing import Optional, Union

import ResSimpy.Nexus.nexus_file_operations as nfo
from ResSimpy.Nexus.DataModels.NexusWell import NexusWell
from ResSimpy.Nexus.DataModels.NexusCompletion import NexusCompletion
from ResSimpy.UnitsEnum import Units
from typing import Literal


def load_wells(wellspec_file_path: str, start_date: str, default_units: Units) -> list[NexusWell]:
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

    well_radius: Optional[str] = None
    units_values: dict[str, Units] = {'ENGLISH': Units.OILFIELD, 'METRIC': Units.METRIC_KPA,
                                      'METKG/CM2': Units.METRIC_KGCM2, 'METBAR': Units.METRIC_BARS, 'LAB': Units.LAB}
    header_values: dict[str, Union[Optional[int], Optional[float], Optional[str]]] = {
        'IW': iw, 'JW': jw, 'L': kw, 'MD': md, 'SKIN': skin, 'DEPTH': depth, 'X': x_value, 'Y': y_value,
        'ANGLA': angla, 'ANGLV': anglv, 'GRID': grid, 'WI': wi, 'DTOP': dtop, 'DBOT': dbot, 'RADW': well_radius}
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

        # Load in the column headings, which appear after the well name
        header_index, headers = __load_wellspec_table_headings(header_index, header_values, index, line, well_name)

        if header_index == -1:
            continue

        if well_name is None:
            raise ValueError(f"No wells found in file: {wellspec_file_path}")

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


def __load_wellspec_table_completions(file_as_list, header_index, header_values, headers, start_date):
    completions: list[NexusCompletion] = []

    # def access_header_value(header_values: dict[str, Union[Optional[int], Optional[float], Optional[str]]],
    #                         key: str, how: Literal['int', 'float', 'string']):
    #     if header_values[key] is None:
    #         return None
    #     match how:
    #         case 'int':
    #             return int(header_values[key])
    #         case 'float':
    #             return float(header_values[key])
    #         case 'string':
    #             return str(header_values[key])

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

        if valid_line:
            new_completion = NexusCompletion(
                i=(None if header_values['IW'] is None else int(header_values['IW'])),
                j=(None if header_values['JW'] is None else int(header_values['JW'])),
                k=(None if header_values['L'] is None else int(header_values['L'])),
                grid=(None if header_values['GRID'] is None else header_values['GRID']),
                well_radius=(None if header_values['RADW'] is None else float(header_values['RADW'])),
                measured_depth=(None if header_values['MD'] is None else float(header_values['MD'])),
                skin=(None if header_values['SKIN'] is None else float(header_values['SKIN'])),
                depth=(None if header_values['DEPTH'] is None else float(header_values['DEPTH'])),
                x=(None if header_values['X'] is None else float(header_values['X'])),
                y=(None if header_values['Y'] is None else float(header_values['Y'])),
                angle_a=(None if header_values['ANGLA'] is None else float(header_values['ANGLA'])),
                angle_v=(None if header_values['ANGLV'] is None else float(header_values['ANGLV'])),
                well_indices=(None if header_values['WI'] is None else float(header_values['WI'])),
                depth_to_top=(None if header_values['DTOP'] is None else float(header_values['DTOP'])),
                depth_to_bottom=(None if header_values['DBOT'] is None else float(header_values['DBOT'])),
                date=start_date,
            )

            completions.append(new_completion)

    return completions


def __load_wellspec_table_headings(header_index: int,
                                   header_values: dict[str, Union[Optional[int], Optional[float], Optional[str]]],
                                   index: int, line: str, well_name: Optional[str],
                                   headers: Optional[list[str]] = None) -> tuple[int, list[str]]:
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
