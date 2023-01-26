from dataclasses import dataclass
from typing import Optional

from ResSimpy.Nexus import nexus_file_operations


@dataclass(kw_only=True)
class NexusFile:
    """ Class to deal with origin and structure of Nexus files and preserve origin of include files
    Attributes:
        location (Optional[str]): Path to the original file being opened. Defaults to None.
        includes (Optional[list[str]]): list of file paths that the file contains. Defaults to None.
        origin (Optional[str]): Where the file was opened from. Defaults to None.
        includes_objects (Optional[list['NexusFile']]): The include files but generated as a NexusFile instance. \
            Defaults to None.
    """
    location: Optional[str] = None
    includes: Optional[list[str]] = None
    origin: Optional[str] = None
    includes_objects: Optional[list['NexusFile']] = None

    def __init__(self, location: Optional[str] = None, includes: Optional[list[str]] = None,
                 origin: Optional[str] = None, includes_objects: Optional[list['NexusFile']] = None,
                 run_generator: bool = True):
        self.location: Optional[str] = location
        self.includes: Optional[list[str]] = includes
        self.origin: Optional[str] = origin
        self.includes_objects: Optional[list['NexusFile']] = includes_objects
        if run_generator:
            self.generate_included_file_objects()

    @classmethod
    def generate_file_include_structure(cls, file_path: str, origin: Optional[str] = None):
        """generates a nexus file instance for a provided text file with information storing the included files

        Args:
            file_path (str): path to a file
            origin (Optional[str], optional): Where the file was opened from. Defaults to None.

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
            origin=origin,
            )

        return nexus_file

    def generate_included_file_objects(self):
        """Builds NexusFile objects for any include files that have been found in the original instance
        """
        # check if there are any includes and exit if not
        if not self.includes:
            return None

        self.includes_objects = []
        for file_path in self.includes:
            inc_file = self.generate_file_include_structure(file_path, origin=self.location)
            self.includes_objects.append(inc_file)

        return self.includes_objects

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
