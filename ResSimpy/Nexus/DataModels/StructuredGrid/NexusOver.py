from dataclasses import dataclass

from ResSimpy.DataModelBaseClasses.Over import Over


@dataclass
class NexusOver(Over):
    """Used to represent a line from an OVER table in a Nexus file.

    Attributes:
        array (str): The arrays to be modified by the over.
        i1 (int): The start of the i range.
        i2 (int): The end of the i range.
        j1 (int): The start of the j range.
        j2 (int): The end of the j range.
        k1 (int): The start of the k range.
        k2 (int): The end of the k range.
        operator (str): The operator to be assigned to the range.
        value (float): The value to be assigned to the range.
        threshold (float): The value for which GE or LE is used.
    """

    def to_string(self) -> str:
        """Converts the over to a string for writing to a Nexus file."""
        return_str = 'OVER'
        return_str += f" {self.array}"
        return_str += '\n'
        if self.grid != 'ROOT':
            return_str += f"GRID {self.grid}\n"
        if self.fault_name:
            return_str += f"FNAME {self.fault_name}\n"
        return_str += f"{self.i1} {self.i2} {self.j1} {self.j2} {self.k1} {self.k2} {self.operator}{self.value}\n"
        return return_str
