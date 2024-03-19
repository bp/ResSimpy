"""Used to represent a connection between two nodes in a Nexus network."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.NodeConnection import NodeConnection


@dataclass(repr=False)
class NexusNodeConnection(NodeConnection):
    """Used to represent a connection between two nodes in a Nexus network.

    Attributes:
    hyd_method: hydraulic lift correlation method used (METHOD)
    pvt_method: pvt method number (IPVT)
    water_method: water method number (IWAT)
    bat_method: bat method number (IBAT)
    elevation_profile: elevation profile as a string (ELEVPR)
    measured_depth_in: measured depth of the input node (MDIN)
    measured_depth_out: measured depth of the output node (MDOUT)
    diameter: diameter of the connecting pipe (DIAMETER)
    inner_diameter: outer diameter of the pipe (INNERDIAM)
    roughness: roughness of the pipe (ROUGHNESS)
    heat_transfer_coeff: the heat transfer coefficient of the pipe (HTC)
    temperature_profile: temperature profile used for the connection. (TEMPPR)
    length: length of the connection (LENGTH)
    delta_depth: change in depth between node_in and node_out (DDEPTH)
    connection_number: used in place of name as a numbered connection (NUMBER)
    seawater_profile: seawater profile used. (SEAWPR)
    rate_mult: multiplier to the rate (RATEMULT)
    polymer: whether polymer is a stream here (POLYMER)
    dp_add: Additional delta pressure (DPADD).
    """

    hyd_method: Optional[str | int] = None
    pvt_method: Optional[int] = None
    bat_method: Optional[int] = None
    water_method: Optional[int] = None
    elevation_profile: Optional[str] = None
    measured_depth_in: Optional[float] = None
    measured_depth_out: Optional[float] = None
    diameter: Optional[float] = None
    inner_diameter: Optional[float] = None
    roughness: Optional[float] = None
    heat_transfer_coeff: Optional[float] = None
    temperature_profile: Optional[float] = None
    length: Optional[float] = None
    delta_depth: Optional[float] = None
    connection_number: Optional[int] = None
    seawater_profile: Optional[str] = None
    rate_mult: Optional[float] = None
    polymer: Optional[str] = None
    unit_system: Optional[UnitSystem] = None
    dp_add: Optional[float] = None
    dt_add: Optional[float] = None
    temperature_in: Optional[float] = None
    temperature_out: Optional[float] = None
    tracer: Optional[str] = None
    heat_conductivity: Optional[float] = None
    insulation_thickness: Optional[float] = None
    insulation_conductivity: Optional[float] = None
    gravity_pressure_gradient_mult: Optional[float] = None
    friction_pressure_gradient_mult: Optional[float] = None
    acceleration_pressure_gradient_mult: Optional[float] = None

    def __init__(self, properties_dict: dict[str, None | int | str | float]) -> None:
        """Initialises the NexusNodeConnection class.

        Args:
            properties_dict (dict): A dictionary of properties to set on the node.
        """
        # call the init of the DataObjectMixin
        super(NodeConnection, self).__init__({})
        for key, prop in properties_dict.items():
            self.__setattr__(key, prop)

    @staticmethod
    def get_keyword_mapping() -> dict[str, tuple[str, type]]:
        """Gets the mapping of nexus keywords to attribute definitions."""
        nexus_mapping = {
            'NAME': ('name', str),
            'NODEIN': ('node_in', str),
            'NODEOUT': ('node_out', str),
            'TYPE': ('con_type', str),
            'METHOD': ('hyd_method', str),
            'IPVT': ('pvt_method', int),
            'IWAT': ('water_method', int),
            'IBAT': ('bat_method', int),
            'ELEVPR': ('elevation_profile', str),
            'MDIN': ('measured_depth_in', float),
            'MDOUT': ('measured_depth_out', float),
            'DIAM': ('diameter', float),
            'INNERDIAM': ('inner_diameter', float),
            'ROUGHNESS': ('roughness', float),
            'HTC': ('heat_transfer_coeff', float),
            'TEMPPR': ('temperature_profile', str),
            'LENGTH': ('length', float),
            'DDEPTH': ('delta_depth', float),
            'NUMBER': ('connection_number', int),
            'SEAWPR': ('seawater_profile', str),
            'RATEMULT': ('rate_mult', float),
            'POLYMER': ('polymer', str),
            'DPADD': ('dp_add', float),
            'DTADD': ('dt_add', float),
            'TEMPIN': ('temperature_in', float),
            'TEMPOUT': ('temperature_out', float),
            'TRACERS': ('tracer', str),
            'HCOND': ('heat_conductivity', float),
            'INSTHN': ('insulation_thickness', float),
            'INSK': ('insulation_conductivity', float),
            'GRPGCR': ('gravity_pressure_gradient_mult', float),
            'FRPGCR': ('friction_pressure_gradient_mult', float),
            'ACPGCR': ('acceleration_pressure_gradient_mult', float),
        }
        return nexus_mapping
