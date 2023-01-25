from dataclasses import dataclass
from typing import Optional

from ResSimpy.Nexus import nexus_file_operations

# to deal with origin and structure of Nexus files and preserve origin of include files


@dataclass
class NexusFile:
    """
    Attributes:
        location (Optional[str]): Path to the original file being opened
        includes (Optional[list[str]]): list of file paths that the file contains
        origin (Optional[str]): Where the file was opened from
    """
    location: Optional[str] = None
    includes: Optional[list[str]] = None
    origin: Optional[str] = None

    def export_network_lists(self):
        """ Exports lists of connections from and to for use in network graphs

        Raises:
            ValueError: If the from and to lists are not the same length
        Returns:
            tuple[list]: list of to and from file paths where the equivalent indexes relate to a connection
        """
        from_list = [self.origin]
        to_list = [self.location]
        if not [self.origin]:
            to_list = []
        if self.includes is not None:
            from_list += [self.location] * len(self.includes)
            to_list += self.includes
        if len(from_list) != len(to_list):
            raise ValueError(f"{from_list=} and {to_list=} are not the same length")

        return from_list, to_list

    @classmethod
    def generate_file_include_structure(cls, file_path: str):
        """generates a nexus file instance for a provided text file with information storing the included files

        Args:
            file_path (str): path to a file

        Returns:
            NexusFile: a class instance for NexusFile with knowledge of include files
        """
        # load file as list and clean up file
        file_as_list = nexus_file_operations.load_file_as_list(file_path)
        file_as_list = nexus_file_operations.strip_file_of_comments(file_as_list)

        # search for the INCLUDE keyword and append to a list:
        inc_file_list = []
        for line in file_as_list:
            if "INCLUDE" in line.upper():
                inc_file_path = nexus_file_operations.get_token_value('INCLUDE', line, [line])
                if inc_file_path is not None:
                    inc_file_list.append(inc_file_path)

        nexus_file = cls(
            location=file_path,
            includes=inc_file_list,
            origin=None,
            )

        return nexus_file
