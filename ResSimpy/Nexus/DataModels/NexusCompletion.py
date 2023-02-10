from dataclasses import dataclass
from typing import Optional

from ResSimpy.Completion import Completion


@dataclass(kw_only=True)
class NexusCompletion(Completion):
    """
    A class representing a completion specific to a Nexus Model. Inherits from Completion
    Additional Attributes:
        measured_depth (Optional[float]): Measured depth of a completion. 'MD' in Nexus
        well_indices (Optional[float]): Well index used to calculate performance of the completion. 'WI' in Nexus
        partial_perf (Optional[float]): Partial penetration factor. 'PPERF' in Nexus
    """
    # TODO: flesh out the attributes in this class
    __measured_depth: Optional[float] = None
    __well_indices: Optional[float] = None
    __partial_perf: Optional[float] = None

    def __init__(self, date: str, i: Optional[int] = None, j: Optional[int] = None, k: Optional[int] = None,
                 skin: Optional[float] = None, depth: Optional[float] = None, well_radius: Optional[float] = None,
                 x: Optional[float] = None, y: Optional[float] = None, angle_a: Optional[float] = None,
                 angle_v: Optional[float] = None, grid: Optional[str] = None, measured_depth: Optional[float] = None,
                 well_indices: Optional[float] = None, depth_to_top: Optional[float] = None,
                 depth_to_bottom: Optional[float] = None, partial_perf: Optional[float] = None):

        self.__measured_depth = measured_depth
        self.__well_indices = well_indices
        self.__partial_perf = partial_perf

        super().__init__(date=date, i=i, j=j, k=k, skin=skin, depth=depth, well_radius=well_radius, x=x, y=y,
                         angle_a=angle_a, angle_v=angle_v, grid=grid, depth_to_top=depth_to_top,
                         depth_to_bottom=depth_to_bottom)

    @property
    def measured_depth(self):
        return self.__measured_depth

    @property
    def well_indices(self):
        return self.__well_indices

    @property
    def partial_perf(self):
        return self.__partial_perf

    def to_dict(self) -> dict[str, None | float | int | str]:
        attribute_dict: dict[str, None | float | int | str] = {
            'measured_depth': self.__measured_depth,
            'well_indices': self.__well_indices,
            'partial_perf': self.__partial_perf,
        }
        attribute_dict.update(super().to_dict())
        return attribute_dict
