from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Union, TypedDict

from ResSimpy.Completion import Completion
from ResSimpy.Nexus.DataModels.NexusRelPermEndPoint import NexusRelPermEndPoint
from ResSimpy.Utils.generic_repr import generic_repr


@dataclass(kw_only=True)
class NexusCompletion(Completion):
    """
    A class representing a completion specific to a Nexus Model. Inherits from Completion
    Additional Attributes:
        measured_depth (Optional[float]): Measured depth of a completion. 'MD' in Nexus
        well_indices (Optional[float]): Well index used to calculate performance of the completion. 'WI' in Nexus
        partial_perf (Optional[float]): Partial penetration factor. 'PPERF' in Nexus
        cell_number (Optional[int]): cell number for for the completion in unstructured grids. 'CELL' in Nexus
        bore_radius (Optional[float]): Well bore radius. 'RADB' in Nexus
        portype (Optional[str]): indicates the pore type for the completion FRACTURE OR MATRIX. 'PORTYPE' in Nexus
        sector (None | str | int): the section of the wellbore to which this completion flows. 'SECT' in Nexus
        khmult (Optional[float]): the multiplier that is applied to the permeability-thickness. 'KHMULT' in Nexus
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
                 kh_mult: Optional[float] = None
                 ):
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

        super().__init__(date=date, i=i, j=j, k=k, skin=skin, depth=depth, well_radius=well_radius, x=x, y=y,
                         angle_a=angle_a, angle_v=angle_v, grid=grid, depth_to_top=depth_to_top,
                         depth_to_bottom=depth_to_bottom, perm_thickness_ovr=perm_thickness_ovr, dfactor=dfactor,
                         rel_perm_method=rel_perm_method, status=status)

    def __repr__(self):
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
        attribute_dict: dict[str, None | float | int | str] = {
            'measured_depth': self.__measured_depth,
            'well_indices': self.__well_indices,
            'partial_perf': self.__partial_perf,
            'cell_number': self.__cell_number,
            'bore_radius': self.__bore_radius,
            'portype': self.__portype,
            'fracture_mult': self.__fracture_mult,
            }
        attribute_dict.update(super().to_dict())
        if self.rel_perm_end_point is not None:
            attribute_dict.update(self.rel_perm_end_point.to_dict())
        return attribute_dict

    @staticmethod
    def completion_is_perforation(completion: NexusCompletion) -> bool:
        """Determines if the supplied completion is a perforation or not"""

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
        """Determines if the supplied completion is a shut-in or not"""
        return not NexusCompletion.completion_is_perforation(completion)

    @staticmethod
    def nexus_mapping() -> dict[str, tuple[str, type]]:
        """returns a dictionary of mapping from nexus keyword to attribute name"""

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

    class InputDictionary(TypedDict):
        date: str
        i: int
        j: int
        k: int
        measured_depth: float
        skin: float
        depth: float
        x: float
        y: float
        angle_a: float
        angle_v: float
        grid: str
        well_indices: float
        depth_to_top: float
        depth_to_bottom: float
        well_radius: float
        partial_perf: float
        cell_number: int
        perm_thickness_ovr: float
        dfactor: float
        rel_perm_method: int
        status: str
        bore_radius: float
        portype: str
        fracture_mult: float
        sector: int
        well_group: str
        zone: int
        angle_open_flow: float
        temperature: float
        flowsector: int
        parent_node: str
        mdcon: float
        pressure_avg_pattern: int
        length: float
        permeability: float
        non_darcy_model: str
        comp_dz: float
        layer_assignment: int
        polymer_bore_radius: float
        polymer_well_radius: float
        kh_mult: float

    @classmethod
    def from_dict(cls, input_dictionary: InputDictionary) -> NexusCompletion:
        """generates a NexusCompletion from a dictionary"""
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
