from dataclasses import dataclass
from typing import Optional

from ResSimpy.Completion import Completion


@dataclass(kw_only=True)
class NexusCompletion(Completion):
    __measured_depth: Optional[float] = None

    def __init__(self, date: str, i: Optional[int] = None, j: Optional[int] = None, k: Optional[int] = None,
                 skin: Optional[float] = None, depth: Optional[float] = None, well_radius: Optional[float] = None,
                 x: Optional[float] = None, y: Optional[float] = None, angle_a: Optional[float] = None,
                 angle_v: Optional[float] = None, grid: Optional[str] = None, measured_depth: Optional[float] = None):
        self.__measured_depth = measured_depth
        super().__init__(date, i, j, k, skin, depth, well_radius, x, y, angle_a, angle_v, grid)
