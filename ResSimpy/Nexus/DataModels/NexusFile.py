from dataclasses import dataclass
from typing import Optional

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
