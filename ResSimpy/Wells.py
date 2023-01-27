from dataclasses import dataclass, field
from typing import Type
from abc import ABC

from ResSimpy.Well import Well


@dataclass(kw_only=True)
class Wells(ABC):
    def get_wells(self):
        raise NotImplementedError("Implement this in the derived class")

    def get_wells_df(self):
        raise NotImplementedError("Implement this in the derived class")