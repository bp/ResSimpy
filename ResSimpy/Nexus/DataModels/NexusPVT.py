from dataclasses import dataclass, field
from typing import Union
import pandas as pd
# import sys
# sys.path.insert(0, '/tcchou/isebo0/Testing/github_repos/ResSimpy')
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Utils.factory_methods import get_empty_dict_union


@dataclass
class NexusPVT():
    """ Class to hold Nexus PVT properties
    Attributes:
        location (Optional[str]): Path to the original file being opened. Defaults to None.
        includes (Optional[list[str]]): list of file paths that the file contains. Defaults to None.
        origin (Optional[str]): Where the file was opened from. Defaults to None.
        includes_objects (Optional[list[NexusFile]]): The include files but generated as a NexusFile instance. \
            Defaults to None.
    """
    properties: dict[str, Union[str, dict, int, float, pd.DataFrame]] = field(default_factory=get_empty_dict_union)

    def read_properties_from_file(self, file_path: str):
        file_obj = NexusFile.generate_file_include_structure(file_path, origin=None)
        file_as_list = file_obj.get_flat_list_str_file()

        print(file_as_list)


# pvt_obj = NexusPVT()
# pvt_obj.read_properties_from_file('/tccother/scratch/ECHELON/psvm/nexus/orig_psvm/nexus_data/m194_rev38_17_03/m194_pvt_01.dat')
