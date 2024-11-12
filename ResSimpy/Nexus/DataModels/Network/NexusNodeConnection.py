"""Used to represent a connection between two nodes in a Nexus network."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.DataModelBaseClasses.NodeConnection import NodeConnection


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

    bat_method: Optional[int] = None
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

    def __init__(self, properties_dict: dict[str, None | int | str | float], date: Optional[str] = None,
                 date_format: Optional[DateFormat] = None, start_date: Optional[str] = None, name: Optional[str] = None,
                 unit_system: Optional[UnitSystem] = None, bat_method: Optional[int] = None,
                 elevation_profile: Optional[str] = None, measured_depth_in: Optional[float] = None,
                 measured_depth_out: Optional[float] = None, diameter: Optional[float] = None,
                 inner_diameter: Optional[float] = None, roughness: Optional[float] = None,
                 heat_transfer_coeff: Optional[float] = None, temperature_profile: Optional[float] = None,
                 length: Optional[float] = None, delta_depth: Optional[float] = None,
                 connection_number: Optional[int] = None, seawater_profile: Optional[str] = None,
                 rate_mult: Optional[float] = None, polymer: Optional[str] = None, dp_add: Optional[float] = None,
                 dt_add: Optional[float] = None, temperature_in: Optional[float] = None,
                 temperature_out: Optional[float] = None, tracer: Optional[str] = None,
                 heat_conductivity: Optional[float] = None, insulation_thickness: Optional[float] = None,
                 insulation_conductivity: Optional[float] = None,
                 gravity_pressure_gradient_mult: Optional[float] = None,
                 friction_pressure_gradient_mult: Optional[float] = None,
                 acceleration_pressure_gradient_mult: Optional[float] = None,
                 node_in: Optional[str] = None, node_out: Optional[str] = None, con_type: Optional[str] = None,
                 hyd_method: Optional[str | int] = None, pvt_method: Optional[int] = None,
                 water_method: Optional[int] = None) -> None:
        """Initialises the NexusNodeConnection class.

        Args:
            properties_dict (dict): dict of the properties to set on the object.
            date (Optional[str]): The date of the object.
            date_format (Optional[DateFormat]): The date format that the object uses.
            start_date (Optional[str]): The start date of the model. Required if the object uses a decimal TIME.
            unit_system (Optional[UnitSystem]): The unit system of the object e.g. ENGLISH, METRIC.
            name (Optional[str]): The name of the object.
            bat_method (Optional[float]): Bat method (IBAT).
            elevation_profile (Optional[str]): Elevation profile identifier (ELEVPR).
            measured_depth_in (Optional[float]): Measured depth of the input node (MDIN)
            measured_depth_out (Optional[float]): Measured depth of the output node (MDOUT).
            diameter (Optional[float]): diameter of the connecting pipe (DIAMETER).
            inner_diameter (Optional[float]): Outer diameter of the pipe (INNERDIAM).
            roughness (Optional[float]): Roughness of the pipe (ROUGHNESS)
            heat_transfer_coeff (Optional[float]): The heat transfer coefficient of the pipe (HTC).
            temperature_profile (Optional[float]): Temperature profile used for the connection (TEMPPR).
            length (Optional[float]): Length of the connection (LENGTH).
            delta_depth (Optional[float]): Change in depth between node_in and node_out (DDEPTH).
            connection_number (Optional[int]): Used in place of name as a numbered connection (NUMBER).
            seawater_profile (Optional[str]): Seawater profile used (SEAWPR).
            rate_mult (Optional[float]): Multiplier to the rate (RATEMULT).
            polymer (Optional[str]): Whether polymer is a stream here (POLYMER).
            dp_add (Optional[float]): Additional delta pressure (DPADD).
            dt_add (Optional[float]):  Additional temperature change (DTADD).
            temperature_in (Optional[float]): Temperature at nodein.
            temperature_out (Optional[float]): Temperature at node-out.
            tracer (Optional[str]): Specifies tracer concentrations.
            heat_conductivity (Optional[float]): Defines heat conductivity (HCOND).
            insulation_thickness (Optional[float]): Defines insulation thickness (INSTHN).
            insulation_conductivity (Optional[float]): Defines insulation conductivity (INSK).
            gravity_pressure_gradient_mult (Optional[float]): Correction Factor for the gravity pressure gradient for
            pressure drop correlations (GRPGCR).
            friction_pressure_gradient_mult (Optional[float]):  Correction Factor for the friction pressure gradient for
            pressure drop correlations (FRPGCR).
            acceleration_pressure_gradient_mult (Optional[float]): Correction Factor for the acceleration pressure
            gradient for pressure drop correlations (ACPGCR).
            con_type (Optional[str]): Connection type.
            hyd_method (optional[str | int]): Hydraulic method (METHOD)
            node_in (Optional[str]): Inflow node name.
            node_out (Optional[str]): Outflow node name.
            pvt_method (Optional[int]): PVT method (IPVT)
            water_method (Optional[int]): Water method (IWAT)
        """

        self.bat_method = bat_method
        self.elevation_profile = elevation_profile
        self.measured_depth_in = measured_depth_in
        self.measured_depth_out = measured_depth_out
        self.diameter = diameter
        self.inner_diameter = inner_diameter
        self.roughness = roughness
        self.heat_transfer_coeff = heat_transfer_coeff
        self.temperature_profile = temperature_profile
        self.length = length
        self.delta_depth = delta_depth
        self.connection_number = connection_number
        self.seawater_profile = seawater_profile
        self.rate_mult = rate_mult
        self.polymer = polymer
        self.dp_add = dp_add
        self.dt_add = dt_add
        self.temperature_in = temperature_in
        self.temperature_out = temperature_out
        self.tracer = tracer
        self.heat_conductivity = heat_conductivity
        self.insulation_thickness = insulation_thickness
        self.insulation_conductivity = insulation_conductivity
        self.gravity_pressure_gradient_mult = gravity_pressure_gradient_mult
        self.friction_pressure_gradient_mult = friction_pressure_gradient_mult
        self.acceleration_pressure_gradient_mult = acceleration_pressure_gradient_mult

        super().__init__(date_format=date_format, start_date=start_date, unit_system=unit_system, name=name, date=date,
                         properties_dict=properties_dict, node_in=node_in, node_out=node_out, con_type=con_type,
                         hyd_method=hyd_method, pvt_method=pvt_method, water_method=water_method)

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
