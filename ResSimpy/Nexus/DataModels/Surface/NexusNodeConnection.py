from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from ResSimpy.Nexus.NexusEnums.UnitsEnum import UnitSystem
from ResSimpy.NodeConnection import NodeConnection


@dataclass
class NexusNodeConnection(NodeConnection):
    # TODO make list below comprehensive
    """
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

    def __init__(self, properties_dict: dict[str, None | int | str | float]):
        super().__init__()
        for key, prop in properties_dict.items():
            self.__setattr__(key, prop)

    @staticmethod
    def get_nexus_mapping() -> dict[str, tuple[str, type]]:
        """gets the mapping of nexus keywords to attribute definitions"""
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
        }
        return nexus_mapping

    def to_dict(self, keys_in_nexus_style: bool = False) -> dict[str, None | str | int | float]:
        """Returns a dictionary of the key properties of a connection"""
        # TODO turn this into a generic method
        mapping_dict = self.get_nexus_mapping()
        if keys_in_nexus_style:
            result_dict = {x: self.__getattribute__(y[0]) for x, y in mapping_dict.items()}

        else:
            result_dict = {y[0]: self.__getattribute__(y[0]) for y in mapping_dict.values()}
        extra_attributes = {'date': self.date, }
        if self.unit_system is not None:
            extra_attributes.update({'unit_system': self.unit_system.value})
        result_dict.update(extra_attributes)
        return result_dict
