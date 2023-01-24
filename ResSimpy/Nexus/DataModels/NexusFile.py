from dataclasses import dataclass
from typing import Optional

# to deal with origin and structure of Nexus files and preserve origin of include files


@dataclass
class NexusFile:
    location: Optional[str] = None
    includes: Optional[list[str]] = None
    origin: Optional[str] = None

    def export_network_lists(self):
        """ Exports lists of connections from and to for use in network graphs

        Returns:
            tuple[list]: _description_
        """
        from_list = [self.origin]
        to_list = [self.location]
        if self.includes is not None:
            from_list += [self.location] * len(self.includes)
            to_list += self.includes

        return from_list, to_list
