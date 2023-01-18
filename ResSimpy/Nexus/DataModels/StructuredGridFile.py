from dataclasses import dataclass
from typing import Optional


@dataclass
class VariableEntry:
    def __init__(self, modifier=None, value=None):
        self.modifier = modifier
        self.value = value

    def __eq__(self, other):
        if not isinstance(other, VariableEntry):
            return NotImplemented
        return self.value == other.value and self.modifier == other.modifier


class PropertyToLoad:
    def __init__(self, token, modifiers, property):
        self.token = token
        self.modifiers = modifiers
        self.property = property


@dataclass
class StructuredGridFile:
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

        if data is not None:
            for name, value in data.items():
                setattr(self, name, self.__wrap(value))

    def __wrap(self, value):
        if isinstance(value, (tuple, list, set, frozenset)):
            return type(value)([self._wrap(v) for v in value])
        else:
            return StructuredGridFile(value) if isinstance(value, dict) else value
