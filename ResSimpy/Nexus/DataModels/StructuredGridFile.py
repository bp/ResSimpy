from dataclasses import dataclass
from typing import Optional


@dataclass
class VariableEntry:
    modifier: Optional[str] = None
    value: Optional[str] = None


@dataclass
class PropertyToLoad:
    token: str
    modifiers: list[str]
    property: VariableEntry


@dataclass(kw_only=True)
class StructuredGridFile:
    netgrs: VariableEntry = VariableEntry()
    porosity: VariableEntry = VariableEntry()
    sw: VariableEntry = VariableEntry()
    kx: VariableEntry = VariableEntry()
    ky: VariableEntry = VariableEntry()
    kz: VariableEntry = VariableEntry()
    # Grid dimensions
    range_x: Optional[int]
    range_y: Optional[int]
    range_z: Optional[int]

    def __init__(self, data: Optional[dict] = None):
        self.netgrs = VariableEntry()
        self.porosity = VariableEntry()
        self.sw = VariableEntry()
        self.kx = VariableEntry()
        self.ky = VariableEntry()
        self.kz = VariableEntry()
        # Grid dimensions
        self.range_x: Optional[int] = None
        self.range_y: Optional[int] = None
        self.range_z: Optional[int] = None

        # Use the dict provided to populate the properties
        if data is not None:
            for name, value in data.items():
                setattr(self, name, self.__wrap(value))

    def __wrap(self, value):
        if isinstance(value, (tuple, list, set, frozenset)):
            return type(value)([self.__wrap(v) for v in value])
        else:
            return StructuredGridFile(value) if isinstance(value, dict) else value
