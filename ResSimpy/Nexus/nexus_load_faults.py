
import re
import numpy as np
import pandas as pd

from ResSimpy.Nexus.NexusKeywords.structured_grid_keywords import FAULT_FACE_MAPPING
from ResSimpy.Utils.general_utilities import is_number
from ResSimpy.FileOperations import file_operations as fo


def load_nexus_fault_mult_table_from_list(file_as_list: list[str]) -> pd.DataFrame:
    """Reads a Nexus (!) format list of file contents containing one or more MULT keywords and
    returns a dataframe with the MULT rows.

    Args:
        file_as_list (list[str]): List of strings representing the lines of a Nexus file.

    Returns:
        pd.DataFrame: DataFrame containing the MULT table data with columns:
            ['i1', 'i2', 'j1', 'j2', 'k1', 'k2', 'mult', 'grid', 'name', 'face']
    """

    dfs = []

    num_tables = 0
    is_table = False
    is_record = False
    name = face = 'NONE'
    grid = 'ROOT'  # nexus default grid

    face_dict = FAULT_FACE_MAPPING

    chunks: list[str] = []
    for line in file_as_list:
        tokens = fo.split_line(line, upper=False)
        line_without_comments = ' '.join(tokens)
        if len(tokens) == 0:
            continue
        if is_table:
            if is_number(tokens[0]):
                is_record = True

            if is_record and (not is_number(tokens[0])):
                data = chunks[0:]
                d_elems = np.array([np.array(data[i].split()) for i in range(len(data))])
                # fill empty elements with zero
                lens = np.array([len(i) for i in d_elems])
                # Mask of valid places in each row
                mask = np.arange(lens.max()) < lens[:, None]
                # Setup output array and put elements from data into masked positions
                outdata = np.zeros(mask.shape, dtype=d_elems.dtype)
                outdata[mask] = np.concatenate(d_elems)
                df = pd.DataFrame(outdata)
                for column in df.columns:
                    try:
                        df[column] = pd.to_numeric(df[column], errors="coerce")
                    except ValueError:
                        pass
                df.columns = ['i1', 'i2', 'j1', 'j2', 'k1', 'k2', 'mult']
                df['grid'] = grid
                df['name'] = name
                df['face'] = face
                dfs.append(df)
                num_tables += 1

                is_table = False
                is_record = False
                chunks = []

        if is_table:
            if re.match("(.*)GRID(.*)", tokens[0]):
                if len(tokens) > 0:
                    grid = tokens[1]
            elif re.match("(.*)FNAME(.*)", tokens[0]):
                if len(tokens) > 0:
                    name = tokens[1]
            else:
                if re.match(r"^MULT$", tokens[0]):
                    is_table = False
                    is_record = False
                    chunks = []
                else:
                    chunks.append(line_without_comments.strip())

        if re.match(r"^MULT$", tokens[0]):
            if len(tokens) > 0:
                face = face_dict[tokens[1]]
            if 'MINUS' in tokens:
                face += '-'  # indicates data apply to 'negative' faces of specified cells
            grid = 'ROOT'  # nexus default
            name = 'NONE'
            is_table = True

    if is_table:
        if is_record:
            data = chunks[0:]
            d_elems = np.array([np.array(data[i].split()) for i in range(len(data))])
            # fill empty elements with zero
            lens = np.array([len(i) for i in d_elems])
            # Mask of valid places in each row
            mask = np.arange(lens.max()) < lens[:, None]
            # Setup output array and put elements from data into masked positions
            outdata = np.zeros(mask.shape, dtype=d_elems.dtype)
            outdata[mask] = np.concatenate(d_elems)
            df = pd.DataFrame(outdata)
            for column in df.columns:
                try:
                    df[column] = pd.to_numeric(df[column], errors="coerce")
                except ValueError:
                    pass
            df.columns = ['i1', 'i2', 'j1', 'j2', 'k1', 'k2', 'mult']
            df['grid'] = grid
            df['name'] = name
            df['face'] = face
            dfs.append(df)
            num_tables += 1

            is_table = False
            is_record = False
            chunks = []

    if not dfs:
        return pd.DataFrame()

    fault_df = pd.concat(dfs).reset_index(drop=True)

    convert_dict = {'i1': int, 'i2': int, 'j1': int, 'j2': int, 'k1': int, 'k2': int, 'mult': float}
    fault_df = fault_df.astype(convert_dict)

    return fault_df
