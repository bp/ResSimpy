from typing import Mapping

from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Units.AttributeMappings.AttributeMappingBase import AttributeMapBase
from ResSimpy.Units.Units import (UnitDimension, Length, Temperature, Diameter, Roughness,
                                  Dimensionless, Pressure, HeatTransfer, Time, DeltaPressure, ProductivityIndex)


class NetworkUnits(AttributeMapBase):
    """Unit types for the attributes of a well connection, wellhead, wellbore, etc."""
    attribute_map: Mapping[str, UnitDimension] = {
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
        'water_inj_mult': Dimensionless(),
        'vip_productivity_index': ProductivityIndex(),
        'd_factor': Dimensionless(),
        'gas_mobility': Dimensionless(),
        'drill_order_benefit': Dimensionless(),
        'heat_transfer_coeff': HeatTransfer(),
        'non_darcy_flow_model': Dimensionless(),
        'non_darcy_flow_method': Dimensionless(),
        'capillary_number_model': Dimensionless(),
        'on_time': Dimensionless(),
        'crossflow': Dimensionless(),
        'crossshut_method': Dimensionless(),
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
        'max_change_pressure': Pressure(),
        'rank_dt': Time(),
        'calculation_type': Dimensionless(),
    }

    def __init__(self, unit_system: None | UnitSystem) -> None:
        super().__init__(unit_system=unit_system)

    @property
    def bhdepth(self) -> str:
        """Returns the unit variable for the given unit system."""
        return Length().unit_system_enum_to_variable(self.unit_system)

    @property
    def depth(self) -> str:
        """Returns the unit variable for the given unit system."""
        return Length().unit_system_enum_to_variable(self.unit_system)

    @property
    def datum_depth(self) -> str:
        """Returns the unit variable for the given unit system."""
        return Length().unit_system_enum_to_variable(self.unit_system)

    @property
    def x_pos(self) -> str:
        """Returns the unit variable for the given unit system."""
        return Length().unit_system_enum_to_variable(self.unit_system)

    @property
    def y_pos(self) -> str:
        """Returns the unit variable for the given unit system."""
        return Length().unit_system_enum_to_variable(self.unit_system)

    @property
    def length(self) -> str:
        """Returns the unit variable for the given unit system."""
        return Length().unit_system_enum_to_variable(self.unit_system)

    @property
    def temperature(self) -> str:
        """Returns the unit variable for the given unit system."""
        return Temperature().unit_system_enum_to_variable(self.unit_system)

    @property
    def diameter(self) -> str:
        """Returns the unit variable for the given unit system."""
        return Diameter().unit_system_enum_to_variable(self.unit_system)

    @property
    def roughness(self) -> str:
        """Returns the unit variable for the given unit system."""
        return Roughness().unit_system_enum_to_variable(self.unit_system)

    @property
    def inner_diameter(self) -> str:
        """Returns the unit variable for the given unit system."""
        return Diameter().unit_system_enum_to_variable(self.unit_system)

    @property
    def productivity_index(self) -> str:
        """Returns the unit variable for the given unit system."""
        return ProductivityIndex().unit_system_enum_to_variable(self.unit_system)

    @property
    def rate_mult(self) -> str:
        """Returns the unit variable for the given unit system."""
        return Dimensionless().unit_system_enum_to_variable(self.unit_system)

    @property
    def dp_add(self) -> str:
        """Returns the unit variable for the given unit system."""
        return DeltaPressure().unit_system_enum_to_variable(self.unit_system)