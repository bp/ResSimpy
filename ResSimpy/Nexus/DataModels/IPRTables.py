"""Class for collection of IPRs"""
import os
from typing import Optional
import pandas as pd

import ResSimpy.Nexus.nexus_file_operations as nfo
from ResSimpy.Nexus.DataModels.IPRTable import IPRTable
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.nexus_file_operations import read_table_to_df


class IPRTables:
    __inputs: list[IPRTable]
    __files: dict[int, NexusFile]

    def __init__(self, tables: Optional[list[IPRTable]] = None, files: Optional[dict[int, NexusFile]] = None,
                 inputs: Optional[list[IPRTable]] = None) -> None:
        """ Class for collections of IPRs
        Args:
            tables: Collections of IPR tables.
            inputs(Optional[list[IPRTable]]): Collection of Nexus IPR methods.
            files(Optional[list[IPRTable]]): Collection of IPR files.
        """

        if tables is None:
            self.tables = []
        else:
            self.tables = tables

        self.__inputs = inputs
        self.__files = files

    def load_iprtables(self) -> None:
        """loads a collection of iprtables"""
        if self.__files is not None and len(self.__files) > 0:
            for table_line in self.__files.keys():
                ipr_file = self.__files[table_line]
                if ipr_file.location is None:
                    raise ValueError(f'Unable to find ipr table file: {ipr_file}')
                if os.path.isfile(ipr_file.location):
                    self.read_iprtables_as_df(file_as_list=ipr_file.get_flat_list_str_file)

    def read_iprtables_as_df(self, file_as_list: list[str]) -> pd.DataFrame:
        """Reads in IPR files from Nexus into a dataframe.

        Args:
            file_as_list (list): File as list of strings.
        """

        date = ''
        reading_line = False
        table_lines = []
        all_tables = []

        for line in file_as_list:
            if nfo.check_token('TIME', line):
                date = nfo.get_expected_token_value(token='TIME', token_line=line, file_list=[line])
            if nfo.check_token('IPRTABLE', line):
                reading_line = True
                continue
            if nfo.check_token('ENDIPRTABLE', line):
                reading_line = False

                df = read_table_to_df(file_as_list=table_lines)
                new_iprtable = IPRTable(date=date, table=df)
                self.tables.append(new_iprtable)

                all_tables.append(df)
                table_lines = []
                continue

            if reading_line:
                table_lines.append(line)

        return pd.concat(all_tables, ignore_index=True) if all_tables else pd.DataFrame()
