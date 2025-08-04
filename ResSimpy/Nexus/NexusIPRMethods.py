"""Class for collection of IPRs."""
from __future__ import annotations
from typing import Optional, MutableMapping, TYPE_CHECKING
import pandas as pd

import ResSimpy.Nexus.nexus_file_operations as nfo
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.NexusIPRMethod import NexusIprMethod
from ResSimpy.Nexus.nexus_file_operations import read_table_to_df

if TYPE_CHECKING:
    from ResSimpy import NexusSimulator


class NexusIprMethods:
    __inputs: MutableMapping[int, NexusIprMethod]
    __files: dict[int, NexusFile]
    __model: NexusSimulator
    __has_been_loaded: bool = False

    def __init__(self, model: NexusSimulator, tables: Optional[list[NexusIprMethod]] = None) -> None:
        """Class for collections of IPRs.

        Args:
            tables: Collections of IPR tables
            model: NexusSimulator instance
        """

        if tables is None:
            self.tables = []
        else:
            self.tables = tables

        self.__model = model

    def read_iprtables_as_df(self, file_as_list: list[str]) -> pd.DataFrame:
        """Reads in IPR files from Nexus into a dataframe.

        Args:
            file_as_list (list): File as list of strings.
        """

        date = ''
        reading_line = False
        table_lines: list[str] = []
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
                new_iprtable = NexusIprMethod(date=date, table=df)
                self.tables.append(new_iprtable)

                all_tables.append(df)
                table_lines = []
                continue

            if reading_line:
                table_lines.append(line)

        return pd.concat(all_tables, ignore_index=True) if all_tables else pd.DataFrame()

    def get_all(self) -> list[NexusIprMethod]:
        """Returns loaded IPRTables."""
        if not self.__has_been_loaded:
            self.load()
        return self.tables

    def load(self) -> None:
        """Loads IPRTables."""
        ipr_files = self.__model.model_files.ipr_files

        if ipr_files is not None:
            for ipr_file in ipr_files.values():
                self.read_iprtables_as_df(file_as_list=ipr_file.get_flat_list_str_file)
            self.__has_been_loaded = True
        else:
            raise ValueError("""IPR files are missing. Can not load IPRTables.""")
