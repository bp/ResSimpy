"""A class representing a single completion from a Nexus wells file."""
from __future__ import annotations
from dataclasses import dataclass

from typing import Optional, Union

# Use correct Self type depending upon Python version
import sys

from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.NexusEnums import DateFormatEnum
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

from ResSimpy.DataModelBaseClasses.Completion import Completion
from ResSimpy.Nexus.DataModels.NexusRelPermEndPoint import NexusRelPermEndPoint
from ResSimpy.Utils.to_dict_generic import to_dict


@dataclass(kw_only=True, repr=False)
class NexusCompletion(Completion):
    """A class representing a completion specific to a Nexus Model. Inherits from Completion.

    Additional Attributes:
        measured_depth (Optional[float]): Measured depth of a completion. 'MD' in Nexus
        well_indices (Optional[float]): Well index used to calculate performance of the completion. 'WI' in Nexus
        partial_perf (Optional[float]): Partial penetration factor. 'PPERF' in Nexus
        cell_number (Optional[int]): cell number for the completion in unstructured grids. 'CELL' in Nexus
        portype (Optional[str]): indicates the pore type for the completion FRACTURE OR MATRIX. 'PORTYPE' in Nexus
        sector (None | str | int): the section of the wellbore to which this completion flows. 'SECT' in Nexus
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
    __polymer_block_radius: Optional[float] = None
    __polymer_well_radius: Optional[float] = None
    __rel_perm_end_point: Optional[NexusRelPermEndPoint] = None

    def __init__(self, date: str, i: Optional[int] = None, j: Optional[int] = None, k: Optional[int] = None,
                 skin: Optional[float] = None, depth: Optional[float] = None, well_radius: Optional[float] = None,
                 x: Optional[float] = None, y: Optional[float] = None, angle_a: Optional[float] = None,
                 angle_v: Optional[float] = None, grid: Optional[str] = None, measured_depth: Optional[float] = None,
                 well_indices: Optional[float] = None, depth_to_top: Optional[float] = None,
                 depth_to_bottom: Optional[float] = None, depth_to_top_str: Optional[str] = None,
                 depth_to_bottom_str: Optional[str] = None, rel_perm_method: Optional[int] = None,
                 dfactor: Optional[float] = None, status: Optional[str] = None, partial_perf: Optional[float] = None,
                 cell_number: Optional[int] = None, perm_thickness_ovr: Optional[float] = None,
                 peaceman_well_block_radius: Optional[float] = None, fracture_mult: Optional[float] = None,
                 sector: Union[None, str, int] = None, well_group: Optional[str] = None, zone: Optional[int] = None,
                 angle_open_flow: Optional[float] = None, temperature: Optional[float] = None,
                 flowsector: Optional[int] = None, parent_node: Optional[str] = None, mdcon: Optional[float] = None,
                 pressure_avg_pattern: Optional[int] = None, length: Optional[float] = None,
                 permeability: Optional[float] = None, non_darcy_model: Optional[str] = None,
                 comp_dz: Optional[float] = None, layer_assignment: Optional[int] = None,
                 polymer_bore_radius: Optional[float] = None, polymer_well_radius: Optional[float] = None,
                 portype: Optional[str] = None, rel_perm_end_point: Optional[NexusRelPermEndPoint] = None,
                 perm_thickness_mult: Optional[float] = None,
                 date_format: Optional[DateFormatEnum.DateFormat] = None,
                 start_date: Optional[str] = None,
                 unit_system: Optional[UnitSystem] = None,
                 ) -> None:
        """Initialises the NexusCompletion class.

        Args:
            date: str representing the date of the completion
            i: (Optional[int]): The structured grid cell location in the x direction.
            j: (Optional[int]): The structured grid cell location in the y direction.
            k: Optional[int]: The structured grid cell location in the z direction.
            skin: Optional[float]: The skin value for the completion.
            depth: Optional[float]: The depth of the completion.
            well_radius: Optional[float]: The well radius.
            x: Optional[float]: The x location of the well in distance units/coordinates.
            y: Optional[float]: The y location of the well in distance units/coordinates.
            angle_a: Optional[float]: the angle relative to the local I axis.
            angle_v: Optional[float]: the angle relative to the true vertical axis (global Z axis).
            grid: Optional[str]: the grid name to which the completion data applies.
            depth_to_top: Optional[float]: depth to the top of a completion interval.
            depth_to_bottom: Optional[float]: depth to the bottom of the completion interval.
            perm_thickness_ovr: Optional[float]: permeability thickness override value to use for the
            completion interval.
            dfactor: Optional[float]: non-darcy factor to use for rate dependent skin calculations.
            rel_perm_method: Optional[int]: rel perm method to use for the completion.
            status: Optional[str]: the status of the layer, can be 'ON' or 'OFF'
            date_format: Optional[DateFormatEnum.DateFormat]: The date format to use for the date as an enum.
            peaceman_well_block_radius: Optional[float]: The pressure equivalent radius of the grid block
            start_date: Optional[str]: The start date of the simulation.
            unit_system: Optional[UnitSystem]: The unit system to use for the completion.
            measured_depth: Optional[float]: Measured depth of a completion. 'MD' in Nexus
            well_indices: Optional[float]: Well index used to calculate performance of the completion. 'WI' in Nexus
            depth_to_top_str: Optional[str]: when depth to top is provided as a string it covers all the completion.
            depth_to_bottom_str: Optional[str]: When depth to bottom is provided as a string it covers all the
            completion.
            rel_perm_method: Optional[int]: The relative permeability method number to use for the completion.
            dfactor: Optional[float]: The non-darcy factor to use for rate dependent skin calculations.
            status: Optional[str]: The status of the layer, can be 'ON' or 'OFF'
            partial_perf: Optional[float]: Partial penetration factor. 'PPERF' in Nexus
            cell_number: Optional[int]: cell number for the completion in unstructured grids.
            perm_thickness_ovr: Optional[float]: Permeability thickness override value to use for the completion.
            peaceman_well_block_radius: Optional[float]: The pressure equivalent radius of the grid block.
            fracture_mult: Optional[float]: The multiplier for the fracture.
            sector: Union[None, str, int]: The section of the wellbore to which this completion flows.
            well_group: Optional[str]: The group of the well.
            zone: Optional[int]: The zone of the well.
            angle_open_flow: Optional[float]: The angle of the open flow.
            temperature: Optional[float]: The temperature of the completion.
            flowsector: Optional[int]: The flow sector of the completion.
            parent_node: Optional[str]: The parent node of the completion.
            mdcon: Optional[float]: The mdcon of the completion.
            pressure_avg_pattern: Optional[int]: The block pattern to take the pressure for the completion inflow.
            length: Optional[float]: The length of the completion.
            permeability: Optional[float]: The permeability of the completion.
            non_darcy_model: Optional[str]: The non-darcy model to use for the completion.
            comp_dz: Optional[float]: the dz of the completion.
            layer_assignment: Optional[int]: The layer assignment of the completion.
            polymer_bore_radius: Optional[float]: The effective polymer bore radius of the completion.
            polymer_well_radius: Optional[float]: The effective polymer well radius of the completion.
            portype: Optional[str]: The pore type for the completion FRACTURE OR MATRIX. 'PORTYPE' in Nexus
            rel_perm_end_point: Optional[NexusRelPermEndPoint]: instance of the NexusRelPermEndPoint class holding the
            rel perm end point data settings.
            perm_thickness_mult: Optional[float]: The multiplier that is applied to the permeability-thickness.
            'KHMULT' in Nexus.
            date_format: Optional[DateFormatEnum.DateFormat]: The date format to use for the date as an enum.
            start_date: Optional[str]: The start date of the simulation.
            unit_system: Optional[UnitSystem]: The unit system to use for the completion.
        """
        self.__measured_depth = measured_depth

        self.__well_indices = well_indices  # TODO: rename this to singular
        self.__partial_perf = partial_perf
        self.__depth_to_top_str = depth_to_top_str
        self.__depth_to_bottom_str = depth_to_bottom_str
        self.__cell_number = cell_number
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
        self.__polymer_block_radius = polymer_bore_radius
        self.__polymer_well_radius = polymer_well_radius
        self.__portype = portype
        self.__rel_perm_end_point = rel_perm_end_point

        if unit_system is None:
            unit_system = UnitSystem.ENGLISH

        super().__init__(date=date, i=i, j=j, k=k, skin=skin, depth=depth, well_radius=well_radius, x=x, y=y,
                         angle_a=angle_a, angle_v=angle_v, grid=grid, depth_to_top=depth_to_top,
                         depth_to_bottom=depth_to_bottom, perm_thickness_ovr=perm_thickness_ovr, dfactor=dfactor,
                         rel_perm_method=rel_perm_method, status=status, date_format=date_format, start_date=start_date,
                         unit_system=unit_system, peaceman_well_block_radius=peaceman_well_block_radius,
                         perm_thickness_mult=perm_thickness_mult)

    @property
    def measured_depth(self) -> float | None:
        """Returns the measured depth of a completion."""
        return self.__measured_depth

    @property
    def well_indices(self) -> float | None:
        """Returns the well index used to calculate performance of the completion."""
        return self.__well_indices

    @property
    def partial_perf(self) -> float | None:
        """Returns the partial penetration factor.
        'PPERF' in Nexus.
        """
        return self.__partial_perf

    @property
    def cell_number(self) -> int | None:
        """Returns the cell number for the completion in unstructured grids."""
        return self.__cell_number

    @property
    def portype(self) -> str | None:
        """Returns the pore type for the completion fracture or MATRIX."""
        return self.__portype

    @property
    def fracture_mult(self) -> float | None:
        """Returns the multiplier for the fracture."""
        return self.__fracture_mult

    @property
    def sector(self) -> None | str | int:
        """Returns the section of the wellbore to which this completion flows."""
        return self.__sector

    @property
    def well_group(self) -> str | None:
        """Returns the group of the well."""
        return self.__well_group

    @property
    def zone(self) -> int | None:
        """Returns the zone of the well."""
        return self.__zone

    @property
    def angle_open_flow(self) -> float | None:
        """Returns the angle of the openflow."""
        return self.__angle_open_flow

    @property
    def temperature(self) -> float | None:
        """Returns the temperature of the completion."""
        return self.__temperature

    @property
    def flowsector(self) -> int | None:
        """Returns the flow sector of the completion."""
        return self.__flowsector

    @property
    def parent_node(self) -> str | None:
        """Returns the parent node of the completion."""
        return self.__parent_node

    @property
    def mdcon(self) -> float | None:
        """Returns the mdcon of the completion."""
        return self.__mdcon

    @property
    def pressure_avg_pattern(self) -> int | None:
        """Returns the block pattern to take the pressure for the completion inflow."""
        return self.__pressure_avg_pattern

    @property
    def length(self) -> float | None:
        """Return the length of the completion."""
        return self.__length

    @property
    def permeability(self) -> float | None:
        """Returns permeability of the completion."""
        return self.__permeability

    @property
    def non_darcy_model(self) -> str | None:
        """Returns non-darcy model to use for the completion."""
        return self.__non_darcy_model

    @property
    def comp_dz(self) -> float | None:
        """Returns dz of the completion."""
        return self.__comp_dz

    @property
    def layer_assignment(self) -> int | None:
        """Returns layer assignment of the completion."""
        return self.__layer_assignment

    @property
    def polymer_block_radius(self) -> float | None:
        """Returns polymer block radius of the completion."""
        return self.__polymer_block_radius

    @property
    def polymer_well_radius(self) -> float | None:
        """Returns effective polymer well radius of the completion."""
        return self.__polymer_well_radius

    @property
    def rel_perm_end_point(self) -> NexusRelPermEndPoint | None:
        """Returns instance of the NexusRelPermEndPoint class
        that holds relative permeability endpoints data storage.
        """
        return self.__rel_perm_end_point

    @property
    def kh_mult(self) -> Optional[float]:
        """Returns the perm thickness multiplier."""
        return self.perm_thickness_mult

    @property
    def depth_to_top_str(self) -> str | None:
        """Returns depth to the top of the completion interval."""
        return self.__depth_to_top_str

    @property
    def depth_to_bottom_str(self) -> str | None:
        """Returns depth to the bottom of the completion interval."""
        return self.__depth_to_bottom_str

    def to_dict(self, keys_in_keyword_style: bool = False, add_date: bool = True, add_units: bool = False,
                add_iso_date: bool = False,
                include_nones: bool = True, units_as_string: bool = True) -> \
            dict[str, None | str | int | float]:
        """Returns dictionary of the completion attributes.

        Args:
            keys_in_keyword_style(bool = False): if true returns the key values as simulator keywords,
            otherwise returns the attribute name as stored by ressimpy.
            add_date(bool = True): if True adds the date to the dictionary.
            add_units(bool = False): if True adds the units to the dictionary.
            add_iso_date(bool = False): if True adds the iso date to the dictionary.
            include_nones(bool = True): if True adds the includes Nones values from object in the dictionary.
            units_as_string(bool = True): if True, converts the object's units to a string value rather than an enum.
        """

        attribute_dict = to_dict(self, keys_in_keyword_style, add_date=add_date, add_iso_date=add_iso_date,
                                 add_units=add_units, include_nones=include_nones)
        parent_attribute_dict = super().to_dict(keys_in_keyword_style=keys_in_keyword_style, add_date=add_date,
                                                add_units=add_units, include_nones=include_nones,
                                                units_as_string=units_as_string, add_iso_date=add_iso_date)

        attribute_dict.update(parent_attribute_dict)
        if self.rel_perm_end_point is not None:
            attribute_dict.update(self.rel_perm_end_point.to_dict())
        return attribute_dict

    @property
    def completion_is_perforation(self) -> bool:
        """Determines if the supplied completion is a perforation or not."""

        if not isinstance(self, NexusCompletion):
            raise ValueError(f"Attempting to compare invalid object: {type(self)}")

        # If we don't have any non-none values for these properties, assume the default values, which mean that the
        # layer is perforated
        if self.partial_perf is None and self.well_indices is None and self.status is None \
                and self.kh_mult is None and self.perm_thickness_ovr is None:
            return True

        return ((self.partial_perf is None or self.partial_perf > 0) and
                (self.well_indices is None or self.well_indices > 0) and
                (self.perm_thickness_ovr is None or self.perm_thickness_ovr > 0) and
                (self.kh_mult is None or self.kh_mult > 0) and
                (self.length is None or self.length > 0) and
                (self.status != 'OFF'))

    @staticmethod
    def get_keyword_mapping() -> dict[str, tuple[str, type]]:
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
            'RADB': ('peaceman_well_block_radius', float),
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
            'RADBP': ('polymer_block_radius', float),
            'RADWP': ('polymer_well_radius', float),
            'KHMULT': ('perm_thickness_mult', float),
        }

        return nexus_mapping

    @staticmethod
    def valid_attributes() -> list[str]:
        """Lists all possible attributes for the object that relate to a Nexus keyword."""
        return [v[0] for v in NexusCompletion.get_keyword_mapping().values()]

    @classmethod
    def from_dict(cls: type[Self], input_dictionary: dict[str, None | float | int | str],
                  date_format: DateFormat) -> Self:
        """Generates a NexusCompletion from a dictionary."""
        skip_mapping_keys = ['date', 'date_format', 'unit_system', 'start_date', 'iso_date']
        for input_attr in input_dictionary:
            if input_attr in skip_mapping_keys:
                continue
            elif input_attr not in cls.valid_attributes():
                raise AttributeError(f'Unexpected keyword "{input_attr}" found within {input_dictionary}')
        date = input_dictionary.get('date', None)
        date_format_str = input_dictionary.get('date_format', None)
        if date_format_str is not None and isinstance(date_format_str, str):
            converted_date_format_str = date_format_str.replace('/', '_')
            completion_date_format = DateFormat[converted_date_format_str]
        else:
            completion_date_format = date_format
        if date is None:
            raise AttributeError(f'No date provided for the completion, instead got {date=}')

        date = str(date)

        if 'start_date' not in input_dictionary or not isinstance(input_dictionary['start_date'], str):
            raise ValueError(f"Invalid start date found: {input_dictionary}")

        if 'unit_system' not in input_dictionary or not isinstance(input_dictionary['unit_system'], UnitSystem):
            raise ValueError(f"Invalid unit system found: {input_dictionary}")

        constructed_class = cls(date=date, date_format=completion_date_format,
                                unit_system=input_dictionary['unit_system'], start_date=input_dictionary['start_date'])
        constructed_class.update(input_dictionary)
        return constructed_class

    def update(self, input_dictionary: dict[str, None | float | int | str]) -> None:
        """Updates a completion based on a dictionary of attributes."""
        for k, v in input_dictionary.items():
            if v is None:
                continue
            if hasattr(self, '_NexusCompletion__' + k):
                setattr(self, '_NexusCompletion__' + k, v)
            elif hasattr(super(), '_Completion__' + k):
                setattr(self, '_Completion__' + k, v)
