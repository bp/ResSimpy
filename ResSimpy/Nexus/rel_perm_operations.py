from __future__ import annotations
from typing import Optional
import ResSimpy.Nexus.nexus_file_operations as nfo


def get_relperm_combined_fluid_column_heading(table_heading: str) -> str:
    """Returns the combined rel perm fluid perm heading for a Nexus Relperm table.

    Args:
        table_heading (str): heading for the rel perm table, expects one of (WOTABLE, GOTABLE, GWTABLE).

    Returns:
        str: one of (KROW, KROG, KRWG) defaults to KRWG if one of the expected table_headings is not given
    """
    rel_perm_header_map = {
        'WOTABLE': 'KROW',
        'GOTABLE': 'KROG',
        'GWTABLE': 'KRWG',
    }
    column_heading = rel_perm_header_map.get(table_heading, 'KRWG')

    return column_heading


def get_relperm_single_fluid_column_heading(table_heading: str) -> str:
    """Returns the single fluid heading for a Nexus Relperm table.

    Args:
        table_heading (str): heading for the rel perm table, expects one of (WOTABLE, GOTABLE, GWTABLE)

    Returns:
        str: heading for the single fluid rel perm header one of (KRG, KRW)
    """
    if table_heading == 'GOTABLE':
        column_heading = 'KRG'
    else:
        column_heading = 'KRW'

    return column_heading


def get_relperm_base_saturation_column_heading(table_heading: str) -> str:
    """Returns the column heading for the base saturation column.

    Args:
        table_heading (str): heading for the rel perm table, expects one of (WOTABLE, GOTABLE, GWTABLE)

    Returns:
        str: heading for the saturation based on the table header one of (SG, SW)
    """

    if table_heading == 'GOTABLE':
        column_heading = 'SG'
    else:
        column_heading = 'SW'

    return column_heading


def load_nexus_relperm_table(relperm_file_path: str) -> dict[str, list[tuple[float, float]]]:
    """Loads in a Nexus relperm table and returns a dictionary with two lists, one with the relperm values for the
    single fluid, and the other with the values for combined fluids.

    Args:
        relperm_file_path (str): path to a single Nexus rel perm file.

    Raises:
        ValueError: if the table header cannot be found for the rel perm table

    Returns:
        dict[str, list[tuple[float, float]]]: dictionary containing two entries one for the column (KRG, KRW)
        and one for one of (KROW, KROG, KRWG) depending on the type of table read.
        Each list entry consists of a tuple of (saturation, relperm value)
    """

    file_as_list = nfo.load_file_as_list(relperm_file_path)

    # Find the column headings line (assume it is the first non-commented out line after the table heading)
    possible_table_headings = ['GWTABLE', 'WOTABLE', 'GOTABLE']
    header_index = None
    table_heading = None

    for index, line in enumerate(file_as_list):
        first_value_in_line = nfo.get_next_value(0, [line], line)
        if first_value_in_line in possible_table_headings:
            table_heading = first_value_in_line
            header_index = index + 1
            break

    if header_index is None or table_heading is None:
        raise ValueError("Cannot find the header for this relperm table")

    # Read in the header line to get the column order
    header_line = file_as_list[header_index]
    columns: list[str] = []

    next_column_heading = nfo.get_next_value(0, [header_line], header_line)
    next_line = header_line
    while next_column_heading is not None:
        columns.append(next_column_heading)
        next_line = next_line.replace(next_column_heading, "", 1)
        next_column_heading = nfo.get_next_value(0, [next_line], next_line)

    # Load in each row from the table
    all_values: list[Optional[dict[str, str]]] = []

    for line in file_as_list[header_index + 1:]:
        trimmed_line = line
        line_values: Optional[dict[str, str]] = {}
        for column in columns:
            value = nfo.get_next_value(0, [trimmed_line], trimmed_line)

            # If we hit a comment or blank line, assume that we've reached the end of our table
            if value is None:
                line_values = None
                break

            trimmed_line = trimmed_line.replace(value, "", 1)

            if line_values is not None:
                line_values[column] = value
        if line_values is not None:
            all_values.append(line_values)
        elif len(all_values) > 0:
            # We've reached the end of the table, finish reading the lines now
            break

    # Retrieve the water and gas values, and return them
    single_fluid_relperms = []  # E.g. Water
    combined_fluid_relperms = []  # E.g. Water-Oil

    single_fluid_column_heading = get_relperm_single_fluid_column_heading(
        table_heading)
    combined_fluid_column_heading = get_relperm_combined_fluid_column_heading(
        table_heading)
    base_saturation_heading = get_relperm_base_saturation_column_heading(
        table_heading)

    for index, row in enumerate(all_values):
        if row is None:
            continue
        single_fluid_relperms.append(
            (float(row[base_saturation_heading]),
             float(row[single_fluid_column_heading]))
        )
        combined_fluid_relperms.append(
            (float(row[base_saturation_heading]), float(
                row[combined_fluid_column_heading]))
        )

    return {'single_fluid': single_fluid_relperms, 'combined_fluids': combined_fluid_relperms}
