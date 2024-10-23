from dataclasses import dataclass

from ResSimpy.DataModelBaseClasses.Multir import Multir


@dataclass
class NexusMultir(Multir):
    region_1: int
    region_2: int
    tmult: float
    directions: None | str = None
    std_connections: bool = True
    non_std_connections: bool = True

    def __init__(self, region_1: int, region_2: int, tmult: float, directions: None | str,
                 std_connections: bool, non_std_connections: bool) -> None:
        """Used to represent a line from a MULTIR table in a Nexus file.

        Args:
            region_1 (int): The first region number.
            region_2 (int): The second region number.
            tmult (float): The transmissibility multiplier for the connection.
            directions (str): The directions of the multir.
            std_connections (str): Applies to standard connections.
            non_std_connections (str): Applies to non-standard connections.
        """
        super().__init__(region_1, region_2, tmult, directions, std_connections, non_std_connections)

    def to_string(self) -> str:
        """Converts the multir to a string for writing to a Nexus file."""
        std_connections_str = 'STD' if self.std_connections else ''
        non_std_connections_str = 'NONSTD' if self.non_std_connections else ''

        return (f"{self.region_1}\t{self.region_2}\t{self.tmult}\t{self.directions}\t"
                f"{std_connections_str}\t{non_std_connections_str}\n")
