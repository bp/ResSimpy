from dataclasses import dataclass
from abc import ABC


@dataclass(kw_only=True)
class Wells(ABC):
    def get_wells(self):
        raise NotImplementedError("Implement this in the derived class")

    def get_wells_df(self):
        raise NotImplementedError("Implement this in the derived class")
