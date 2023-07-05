from abc import ABC, abstractmethod
from dataclasses import dataclass

from ResSimpy.Simulator import Simulator


@dataclass(kw_only=True)
class Network(ABC):
    __model: Simulator
