"""Unit types for the attributes of a well connection, wellhead, wellbore, etc."""
from typing import Mapping

from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Units.AttributeMappings.BaseUnitMapping import BaseUnitMapping
from ResSimpy.Units.Units import (UnitDimension, Length, Temperature, Diameter, Roughness,
                                  Dimensionless, HeatTransfer, Time, DeltaPressure, ProductivityIndex,
                                  NonDarcySkin, ThermalConductivity)


class NetworkUnits(BaseUnitMapping):
    """Unit types for the attributes of a well connection, wellhead, wellbore, etc."""

    def __init__(self, unit_system: None | UnitSystem) -> None:
        """Initialises the NetworkUnits class.

        Args:
            unit_system (None | UnitSystem): The unit system to use for the unit mapping.
        """
        super().__init__(unit_system=unit_system)
        self.attribute_map: Mapping[str, UnitDimension] = {
            'bhdepth': Length(),
            'depth': Length(),
            'datum_depth': Length(),
            'x_pos': Length(),
            'y_pos': Length(),
            'length': Length(),
            'temperature': Temperature(),
            'diameter': Diameter(),
            'roughness': Roughness(),
            'inner_diameter': Diameter(),
            'productivity_index': ProductivityIndex(),
            'rate_mult': Dimensionless(),
            'dp_add': DeltaPressure(),
            'dt_add': Temperature(),
            'well_index_mult': Dimensionless(),
            'vip_productivity_index': ProductivityIndex(),
            'd_factor': NonDarcySkin(),
            'gas_mobility': Dimensionless(),
            'drill_order_benefit': Dimensionless(),
            'heat_transfer_coeff': HeatTransfer(),
            'non_darcy_flow_model': Dimensionless(),
            'non_darcy_flow_method': Dimensionless(),
            'capillary_number_model': Dimensionless(),
            'on_time': Dimensionless(),
            'crossflow': Dimensionless(),
            'crossshut': Dimensionless(),
            'inj_mobility': Dimensionless(),
            'temperature_profile': Dimensionless(),
            'elevation_profile': Dimensionless(),
            'measured_depth_in': Length(),
            'measured_depth_out': Length(),
            'delta_depth': Length(),
            'temp': Temperature(),
            'hyd_method': Dimensionless(),
            'pvt_method': Dimensionless(),
            'water_method': Dimensionless(),
            'bat_method': Dimensionless(),
            'number': Dimensionless(),
            'gradient_calc': Dimensionless(),
            'add_tubing': Dimensionless(),
            'tracer': Dimensionless(),
            'con_type': Dimensionless(),
            'bore_type': Dimensionless(),

            # Units from Target class
            'control_quantity': Dimensionless(),
            'control_type': Dimensionless(),
            'control_condition': Dimensionless(),
            'control_method': Dimensionless(),
            'control_connections': Dimensionless(),
            'calculation_method': Dimensionless(),
            'calculation_conditions': Dimensionless(),
            'calculation_connections': Dimensionless(),
            'value': Dimensionless(),
            'add_value': Dimensionless(),
            'region': Dimensionless(),
            'priority': Dimensionless(),
            'minimum_rate': Dimensionless(),
            'minimum_rate_no_shut': Dimensionless(),
            'guide_rate': Dimensionless(),
            'max_change_pressure': DeltaPressure(),
            'rank_dt': Time(),
            'calculation_type': Dimensionless(),
            'temperature_in': Temperature(),
            'temperature_out': Temperature(),
            'heat_conductivity': ThermalConductivity(),
            'insulation_thickness': Diameter(),  # Same units as diameter but is annular
            'insulation_conductivity': ThermalConductivity(),
            'gravity_pressure_gradient_mult': Dimensionless(),
            'friction_pressure_gradient_mult': Dimensionless(),
            'acceleration_pressure_gradient_mult': Dimensionless(),
        }

    @property
    def bhdepth(self) -> str:
        """Returns the unit for bhdepth."""
        return self.get_unit_for_attribute('bhdepth')

    @property
    def depth(self) -> str:
        """Returns the unit for depth."""
        return self.get_unit_for_attribute('depth')

    @property
    def datum_depth(self) -> str:
        """Returns the unit for datum_depth."""
        return self.get_unit_for_attribute('datum_depth')

    @property
    def x_pos(self) -> str:
        """Returns the unit for x_pos."""
        return self.get_unit_for_attribute('x_pos')

    @property
    def y_pos(self) -> str:
        """Returns the unit for y_pos."""
        return self.get_unit_for_attribute('y_pos')

    @property
    def length(self) -> str:
        """Returns the unit for length."""
        return self.get_unit_for_attribute('length')

    @property
    def temperature(self) -> str:
        """Returns the unit for temperature."""
        return self.get_unit_for_attribute('temperature')

    @property
    def diameter(self) -> str:
        """Returns the unit for diameter."""
        return self.get_unit_for_attribute('diameter')

    @property
    def roughness(self) -> str:
        """Returns the unit for roughness."""
        return self.get_unit_for_attribute('roughness')

    @property
    def inner_diameter(self) -> str:
        """Returns the unit for inner_diameter."""
        return self.get_unit_for_attribute('inner_diameter')

    @property
    def productivity_index(self) -> str:
        """Returns the unit for productivity_index."""
        return self.get_unit_for_attribute('productivity_index')

    @property
    def rate_mult(self) -> str:
        """Returns the unit for rate_mult."""
        return self.get_unit_for_attribute('rate_mult')

    @property
    def dp_add(self) -> str:
        """Returns the unit for dp_add."""
        return self.get_unit_for_attribute('dp_add')

    @property
    def dt_add(self) -> str:
        """Returns the unit for dt_add."""
        return self.get_unit_for_attribute('dt_add')

    @property
    def well_index_mult(self) -> str:
        """Returns the unit for well_index_mult."""
        return self.get_unit_for_attribute('well_index_mult')

    @property
    def vip_productivity_index(self) -> str:
        """Returns the unit for vip_productivity_index."""
        return self.get_unit_for_attribute('vip_productivity_index')

    @property
    def d_factor(self) -> str:
        """Returns the unit for d_factor."""
        return self.get_unit_for_attribute('d_factor')

    @property
    def gas_mobility(self) -> str:
        """Returns the unit for gas_mobility."""
        return self.get_unit_for_attribute('gas_mobility')

    @property
    def drill_order_benefit(self) -> str:
        """Returns the unit for drill_order_benefit."""
        return self.get_unit_for_attribute('drill_order_benefit')

    @property
    def heat_transfer_coeff(self) -> str:
        """Returns the unit for heat_transfer_coeff."""
        return self.get_unit_for_attribute('heat_transfer_coeff')

    @property
    def non_darcy_flow_model(self) -> str:
        """Returns the unit for non_darcy_flow_model."""
        return self.get_unit_for_attribute('non_darcy_flow_model')

    @property
    def non_darcy_flow_method(self) -> str:
        """Returns the unit for non_darcy_flow_method."""
        return self.get_unit_for_attribute('non_darcy_flow_method')

    @property
    def capillary_number_model(self) -> str:
        """Returns the unit for capillary_number_model."""
        return self.get_unit_for_attribute('capillary_number_model')

    @property
    def on_time(self) -> str:
        """Returns the unit for on_time."""
        return self.get_unit_for_attribute('on_time')

    @property
    def crossflow(self) -> str:
        """Returns the unit for crossflow."""
        return self.get_unit_for_attribute('crossflow')

    @property
    def crossshut(self) -> str:
        """Returns the unit for crossshut."""
        return self.get_unit_for_attribute('crossshut')

    @property
    def inj_mobility(self) -> str:
        """Returns the unit for inj_mobility."""
        return self.get_unit_for_attribute('inj_mobility')

    @property
    def temperature_profile(self) -> str:
        """Returns the unit for temperature_profile."""
        return self.get_unit_for_attribute('temperature_profile')

    @property
    def elevation_profile(self) -> str:
        """Returns the unit for elevation_profile."""
        return self.get_unit_for_attribute('elevation_profile')

    @property
    def measured_depth_in(self) -> str:
        """Returns the unit for measured_depth_in."""
        return self.get_unit_for_attribute('measured_depth_in')

    @property
    def measured_depth_out(self) -> str:
        """Returns the unit for measured_depth_out."""
        return self.get_unit_for_attribute('measured_depth_out')

    @property
    def delta_depth(self) -> str:
        """Returns the unit for delta_depth."""
        return self.get_unit_for_attribute('delta_depth')

    @property
    def temp(self) -> str:
        """Returns the unit for temp."""
        return self.get_unit_for_attribute('temp')

    @property
    def hyd_method(self) -> str:
        """Returns the unit for hyd_method."""
        return self.get_unit_for_attribute('hyd_method')

    @property
    def pvt_method(self) -> str:
        """Returns the unit for pvt_method."""
        return self.get_unit_for_attribute('pvt_method')

    @property
    def water_method(self) -> str:
        """Returns the unit for water_method."""
        return self.get_unit_for_attribute('water_method')

    @property
    def bat_method(self) -> str:
        """Returns the unit for bat_method."""
        return self.get_unit_for_attribute('bat_method')

    @property
    def number(self) -> str:
        """Returns the unit for number."""
        return self.get_unit_for_attribute('number')

    @property
    def gradient_calc(self) -> str:
        """Returns the unit for gradient_calc."""
        return self.get_unit_for_attribute('gradient_calc')

    @property
    def add_tubing(self) -> str:
        """Returns the unit for add_tubing."""
        return self.get_unit_for_attribute('add_tubing')

    @property
    def tracer(self) -> str:
        """Returns the unit for tracer."""
        return self.get_unit_for_attribute('tracer')

    @property
    def con_type(self) -> str:
        """Returns the unit for con_type."""
        return self.get_unit_for_attribute('con_type')

    @property
    def bore_type(self) -> str:
        """Returns the unit for bore_type."""
        return self.get_unit_for_attribute('bore_type')

    @property
    def control_quantity(self) -> str:
        """Returns the unit for control_quantity."""
        return self.get_unit_for_attribute('control_quantity')

    @property
    def control_type(self) -> str:
        """Returns the unit for control_type."""
        return self.get_unit_for_attribute('control_type')

    @property
    def control_condition(self) -> str:
        """Returns the unit for control_condition."""
        return self.get_unit_for_attribute('control_condition')

    @property
    def control_method(self) -> str:
        """Returns the unit for control_method."""
        return self.get_unit_for_attribute('control_method')

    @property
    def control_connections(self) -> str:
        """Returns the unit for control_connections."""
        return self.get_unit_for_attribute('control_connections')

    @property
    def calculation_method(self) -> str:
        """Returns the unit for calculation_method."""
        return self.get_unit_for_attribute('calculation_method')

    @property
    def calculation_conditions(self) -> str:
        """Returns the unit for calculation_conditions."""
        return self.get_unit_for_attribute('calculation_conditions')

    @property
    def calculation_connections(self) -> str:
        """Returns the unit for calculation_connections."""
        return self.get_unit_for_attribute('calculation_connections')

    @property
    def value(self) -> str:
        """Returns the unit for value."""
        return self.get_unit_for_attribute('value')

    @property
    def add_value(self) -> str:
        """Returns the unit for add_value."""
        return self.get_unit_for_attribute('add_value')

    @property
    def region(self) -> str:
        """Returns the unit for region."""
        return self.get_unit_for_attribute('region')

    @property
    def priority(self) -> str:
        """Returns the unit for priority."""
        return self.get_unit_for_attribute('priority')

    @property
    def minimum_rate(self) -> str:
        """Returns the unit for minimum_rate."""
        return self.get_unit_for_attribute('minimum_rate')

    @property
    def minimum_rate_no_shut(self) -> str:
        """Returns the unit for minimum_rate_no_shut."""
        return self.get_unit_for_attribute('minimum_rate_no_shut')

    @property
    def guide_rate(self) -> str:
        """Returns the unit for guide_rate."""
        return self.get_unit_for_attribute('guide_rate')

    @property
    def max_change_pressure(self) -> str:
        """Returns the unit for max_change_pressure."""
        return self.get_unit_for_attribute('max_change_pressure')

    @property
    def rank_dt(self) -> str:
        """Returns the unit for rank_dt."""
        return self.get_unit_for_attribute('rank_dt')

    @property
    def calculation_type(self) -> str:
        """Returns the unit for calculation_type."""
        return self.get_unit_for_attribute('calculation_type')

    @property
    def temperature_in(self) -> str:
        """Returns the unit for temperature_in."""
        return self.get_unit_for_attribute('temperature_in')

    @property
    def temperature_out(self) -> str:
        """Returns the unit for temperature_out."""
        return self.get_unit_for_attribute('temperature_out')

    @property
    def heat_conductivity(self) -> str:
        """Returns the unit for heat_conductivity."""
        return self.get_unit_for_attribute('heat_conductivity')

    @property
    def insulation_thickness(self) -> str:
        """Returns the unit for insulation_thickness."""
        return self.get_unit_for_attribute('insulation_thickness')

    @property
    def insulation_conductivity(self) -> str:
        """Returns the unit for insulation_conductivity."""
        return self.get_unit_for_attribute('insulation_conductivity')

    @property
    def gravity_pressure_gradient_mult(self) -> str:
        """Returns the unit for gravity_pressure_gradient_mult."""
        return self.get_unit_for_attribute('gravity_pressure_gradient_mult')

    @property
    def friction_pressure_gradient_mult(self) -> str:
        """Returns the unit for friction_pressure_gradient_mult."""
        return self.get_unit_for_attribute('friction_pressure_gradient_mult')

    @property
    def acceleration_pressure_gradient_mult(self) -> str:
        """Returns the unit for acceleration_pressure_gradient_mult."""
        return self.get_unit_for_attribute('acceleration_pressure_gradient_mult')
