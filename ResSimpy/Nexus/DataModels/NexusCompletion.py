from __future__ import annotations
from dataclasses import dataclass

from typing import Optional, Union, TypedDict


# Use correct Self type depending upon Python version
import sys

from ResSimpy.Nexus.NexusEnums import DateFormatEnum
from ResSimpy.Utils.obj_to_table_string import to_string

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

from ResSimpy.Completion import Completion
from ResSimpy.Nexus.DataModels.NexusRelPermEndPoint import NexusRelPermEndPoint
from ResSimpy.Utils.generic_repr import generic_repr
from ResSimpy.Utils.to_dict_generic import to_dict


@dataclass(kw_only=True)
class NexusCompletion(Completion):
    """A class representing a completion specific to a Nexus Model. Inherits from Completion.

    Additional Attributes:
        measured_depth (Optional[float]): Measured depth of a completion. 'MD' in Nexus
        well_indices (Optional[float]): Well index used to calculate performance of the completion. 'WI' in Nexus
        partial_perf (Optional[float]): Partial penetration factor. 'PPERF' in Nexus
        cell_number (Optional[int]): cell number for the completion in unstructured grids. 'CELL' in Nexus
        bore_radius (Optional[float]): Well bore radius. 'RADB' in Nexus
        portype (Optional[str]): indicates the pore type for the completion FRACTURE OR MATRIX. 'PORTYPE' in Nexus
        sector (None | str | int): the section of the wellbore to which this completion flows. 'SECT' in Nexus
        khmult (Optional[float]): the multiplier that is applied to the permeability-thickness. 'KHMULT' in Nexus.
    """

    __measured_depth: Optional[float] = None
    __well_indices: Optional[float] = None
    __partial_perf: Optional[float] = None
    __cell_number: Optional[int] = None
    __bore_radius: Optional[float] = None
    __portype: Optional[str] = None
    __fracture_mult: Optional[float] = None
    __sector: Union[None, str, int] = None
    __well_group: Optional[str] = None
    __zone: Optional[int] = None
    __angle_open_flow: Optional[float] = None
    __temperature: Optional[float] = None
    __flowsector: Optional[int] = None
    __parent_node: Optional[str] = None
    __mdcon: Optional[float] = None
    __pressure_avg_pattern: Optional[int] = None
    __length: Optional[float] = None
    __permeability: Optional[float] = None
    __non_darcy_model: Optional[str] = None
    __comp_dz: Optional[float] = None
    __layer_assignment: Optional[int] = None
    __polymer_bore_radius: Optional[float] = None
    __polymer_well_radius: Optional[float] = None
    __rel_perm_end_point: Optional[NexusRelPermEndPoint] = None
    __kh_mult: Optional[float] = None

    def __init__(self, date: str, i: Optional[int] = None, j: Optional[int] = None, k: Optional[int] = None,
                 skin: Optional[float] = None, depth: Optional[float] = None, well_radius: Optional[float] = None,
                 x: Optional[float] = None, y: Optional[float] = None, angle_a: Optional[float] = None,
                 angle_v: Optional[float] = None, grid: Optional[str] = None, measured_depth: Optional[float] = None,
                 well_indices: Optional[float] = None, depth_to_top: Optional[float] = None,
                 depth_to_bottom: Optional[float] = None, rel_perm_method: Optional[int] = None,
                 dfactor: Optional[float] = None, status: Optional[str] = None, partial_perf: Optional[float] = None,
                 cell_number: Optional[int] = None, perm_thickness_ovr: Optional[float] = None,
                 bore_radius: Optional[float] = None, fracture_mult: Optional[float] = None,
                 sector: Union[None, str, int] = None, well_group: Optional[str] = None, zone: Optional[int] = None,
                 angle_open_flow: Optional[float] = None, temperature: Optional[float] = None,
                 flowsector: Optional[int] = None, parent_node: Optional[str] = None, mdcon: Optional[float] = None,
                 pressure_avg_pattern: Optional[int] = None, length: Optional[float] = None,
                 permeability: Optional[float] = None, non_darcy_model: Optional[str] = None,
                 comp_dz: Optional[float] = None, layer_assignment: Optional[int] = None,
                 polymer_bore_radius: Optional[float] = None, polymer_well_radius: Optional[float] = None,
                 portype: Optional[str] = None, rel_perm_end_point: Optional[NexusRelPermEndPoint] = None,
                 kh_mult: Optional[float] = None,
                 date_format: Optional[DateFormatEnum.DateFormat] = None,
                 no_of_days: Optional[str] = None
                 ) -> None:
        self.__measured_depth = measured_depth
        self.__well_indices = well_indices
        self.__partial_perf = partial_perf

        self.__cell_number = cell_number
        self.__bore_radius = bore_radius
        self.__fracture_mult = fracture_mult
        self.__sector = sector
        self.__well_group = well_group
        self.__zone = zone
        self.__angle_open_flow = angle_open_flow
        self.__temperature = temperature
        self.__flowsector = flowsector
        self.__parent_node = parent_node
        self.__mdcon = mdcon
        self.__pressure_avg_pattern = pressure_avg_pattern
        self.__length = length
        self.__permeability = permeability
        self.__non_darcy_model = non_darcy_model
        self.__comp_dz = comp_dz
        self.__layer_assignment = layer_assignment
        self.__polymer_bore_radius = polymer_bore_radius
        self.__polymer_well_radius = polymer_well_radius
        self.__portype = portype
        self.__rel_perm_end_point = rel_perm_end_point
        self.__kh_mult = kh_mult
        self.date_format = date_format
        self.no_of_days = no_of_days

        super().__init__(date=date, i=i, j=j, k=k, skin=skin, depth=depth, well_radius=well_radius, x=x, y=y,
                         angle_a=angle_a, angle_v=angle_v, grid=grid, depth_to_top=depth_to_top,
                         depth_to_bottom=depth_to_bottom, perm_thickness_ovr=perm_thickness_ovr, dfactor=dfactor,
                         rel_perm_method=rel_perm_method, status=status)

    def __repr__(self) -> str:
        return generic_repr(self)

    @property
    def measured_depth(self):
        return self.__measured_depth

    @property
    def well_indices(self):
        return self.__well_indices

    @property
    def partial_perf(self):
        return self.__partial_perf

    @property
    def cell_number(self):
        return self.__cell_number

    @property
    def bore_radius(self):
        return self.__bore_radius

    @property
    def portype(self):
        return self.__portype

    @property
    def fracture_mult(self):
        return self.__fracture_mult

    @property
    def sector(self):
        return self.__sector

    @property
    def well_group(self):
        return self.__well_group

    @property
    def zone(self):
        return self.__zone

    @property
    def angle_open_flow(self):
        return self.__angle_open_flow

    @property
    def temperature(self):
        return self.__temperature

    @property
    def flowsector(self):
        return self.__flowsector

    @property
    def parent_node(self):
        return self.__parent_node

    @property
    def mdcon(self):
        return self.__mdcon

    @property
    def pressure_avg_pattern(self):
        return self.__pressure_avg_pattern

    @property
    def length(self):
        return self.__length

    @property
    def permeability(self):
        return self.__permeability

    @property
    def non_darcy_model(self):
        return self.__non_darcy_model

    @property
    def comp_dz(self):
        return self.__comp_dz

    @property
    def layer_assignment(self):
        return self.__layer_assignment

    @property
    def polymer_bore_radius(self):
        return self.__polymer_bore_radius

    @property
    def polymer_well_radius(self):
        return self.__polymer_well_radius

    @property
    def rel_perm_end_point(self):
        return self.__rel_perm_end_point

    @property
    def kh_mult(self):
        return self.__kh_mult

    def to_dict(self) -> dict[str, None | float | int | str]:
        attribute_dict: dict[str, None | float | int | str] = to_dict(self, add_units=False)

        attribute_dict.update(super().to_dict())
        if self.rel_perm_end_point is not None:
            attribute_dict.update(self.rel_perm_end_point.to_dict())
        return attribute_dict

    @staticmethod
    def completion_is_perforation(completion: NexusCompletion) -> bool:
        """Determines if the supplied completion is a perforation or not."""

        # If we don't have any non-none values for these properties, assume the default values, which mean that the
        # layer is perforated
        if completion.partial_perf is None and completion.well_indices is None and completion.status is None \
                and completion.kh_mult is None and completion.perm_thickness_ovr is None:
            return True

        return ((completion.partial_perf is None or completion.partial_perf > 0) and
                (completion.well_indices is None or completion.well_indices > 0) and
                (completion.perm_thickness_ovr is None or completion.perm_thickness_ovr > 0) and
                (completion.kh_mult is None or completion.kh_mult > 0) and
                (completion.length is None or completion.length > 0) and
                (completion.status != 'OFF'))

    @staticmethod
    def completion_is_shutin(completion: NexusCompletion) -> bool:
        """Determines if the supplied completion is a shut-in or not."""
        return not NexusCompletion.completion_is_perforation(completion)

    @staticmethod
    def get_nexus_mapping() -> dict[str, tuple[str, type]]:
        """Returns a dictionary of mapping from nexus keyword to attribute name."""

        nexus_mapping: dict[str, tuple[str, type]] = {
            'IW': ('i', int),
            'JW': ('j', int),
            'L': ('k', int),
            'MD': ('measured_depth', float),
            'SKIN': ('skin', float),
            'DEPTH': ('depth', float),
            'X': ('x', float),
            'Y': ('y', float),
            'ANGLA': ('angle_a', float),
            'ANGLV': ('angle_v', float),
            'GRID': ('grid', str),
            'WI': ('well_indices', float),
            'DTOP': ('depth_to_top', float),
            'DBOT': ('depth_to_bottom', float),
            'RADW': ('well_radius', float),
            'PPERF': ('partial_perf', float),
            'CELL': ('cell_number', int),
            'KH': ('perm_thickness_ovr', float),
            'D': ('dfactor', float),
            'IRELPM': ('rel_perm_method', int),
            'STAT': ('status', str),
            'RADB': ('bore_radius', float),
            'PORTYPE': ('portype', str),
            'FM': ('fracture_mult', float),
            'SECT': ('sector', int),
            'GROUP': ('well_group', str),
            'ZONE': ('zone', int),
            'ANGLE': ('angle_open_flow', float),
            'TEMP': ('temperature', float),
            'FLOWSECT': ('flowsector', int),
            'PARENT': ('parent_node', str),
            'MDCON': ('mdcon', float),
            'IPTN': ('pressure_avg_pattern', int),
            'LENGTH': ('length', float),
            'K': ('permeability', float),
            'ND': ('non_darcy_model', str),
            'DZ': ('comp_dz', float),
            'LAYER': ('layer_assignment', int),
            'RADBP': ('polymer_bore_radius', float),
            'RADWP': ('polymer_well_radius', float),
            'KHMULT': ('kh_mult', float),
        }

        return nexus_mapping

    class InputDictionary(TypedDict, total=False):
        date: str
        i: Optional[int]
        j: Optional[int]
        k: Optional[int]
        measured_depth: Optional[float]
        skin: Optional[float]
        depth: Optional[float]
        x: Optional[float]
        y: Optional[float]
        angle_a: Optional[float]
        angle_v: Optional[float]
        grid: Optional[str]
        well_indices: Optional[float]
        depth_to_top: Optional[float]
        depth_to_bottom: Optional[float]
        well_radius: Optional[float]
        partial_perf: Optional[float]
        cell_number: Optional[int]
        perm_thickness_ovr: Optional[float]
        dfactor: Optional[float]
        rel_perm_method: Optional[int]
        status: Optional[str]
        bore_radius: Optional[float]
        portype: Optional[str]
        fracture_mult: Optional[float]
        sector: Optional[int]
        well_group: Optional[str]
        zone: Optional[int]
        angle_open_flow: Optional[float]
        temperature: Optional[float]
        flowsector: Optional[int]
        parent_node: Optional[str]
        mdcon: Optional[float]
        pressure_avg_pattern: Optional[int]
        length: Optional[float]
        permeability: Optional[float]
        non_darcy_model: Optional[str]
        comp_dz: Optional[float]
        layer_assignment: Optional[int]
        polymer_bore_radius: Optional[float]
        polymer_well_radius: Optional[float]
        kh_mult: Optional[float]

    @classmethod
    def from_dict(cls, input_dictionary: InputDictionary) -> Self:
        """Generates a NexusCompletion from a dictionary."""
        try:
            return cls(**input_dictionary)
        except AttributeError:
            raise AttributeError(f'Unexpected keyword found within {input_dictionary}')

    def update(self, input_dictionary: InputDictionary) -> None:
        for k, v in input_dictionary.items():
            if v is None:
                continue
            if hasattr(self, '_NexusCompletion__' + k):
                setattr(self, '_NexusCompletion__' + k, v)
            elif hasattr(super(), '_Completion__' + k):
                setattr(self, '_Completion__' + k, v)

    def completion_to_wellspec_row(self, headers: list[str]) -> list[str]:
        """Takes a completion object and returns the attribute values as a string in the order of headers provided.

        Args:
            headers (list[str]): list of header values in Nexus keyword format

        Returns:
            string of the values in the order of the headers provided.

        """
        completion_list_string = [to_string(self, headers)]
        return completion_list_string
