from typing import Optional, Dict

import ResSimpy.Nexus.nexus_file_operations as nfo
from ResSimpy.Nexus.DataModels.NexusWell import NexusWell
from ResSimpy.Well import Well
from ResSimpy.Nexus.DataModels.NexusCompletion import NexusCompletion


def load_wells(well_file: str, start_date: str) -> list[Well]:
    file_as_list = nfo.load_file_as_list(well_file)

    well_name: Optional[str] = None
    completions: list[NexusCompletion] = []
    headers: list[str] = []

    iw: Optional[int] = None
    jw: Optional[int] = None
    kw: Optional[int] = None
    well_radius: Optional[float] = None
    header_values = {'IW': iw, 'JW': jw, 'L': kw, 'RADW': well_radius}
    header_index = -1

    for index, line in enumerate(file_as_list):

        if 'WELLSPEC' in line:
            well_name = nfo.get_token_value(token='WELLSPEC', token_line=line, file_list=file_as_list).strip('\"')
            continue

        # Load in the column headings, which appear after the well name
        if well_name is not None:
            for key in header_values.keys():
                if key in line:
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

    # Load in each line of the table
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
            new_completion = NexusCompletion(i=(int(header_values['IW'])), j=int(header_values['JW']),
                                             k=int(header_values['L']), well_radius=float(header_values['RADW']),
                                             date=start_date)

            completions.append(new_completion)

    well = [NexusWell(completions=completions, well_name=well_name)]
    return well
