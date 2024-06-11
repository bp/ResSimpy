from typing import Mapping
from ResSimpy.Enums.UnitsEnum import UnitSystem

from ResSimpy.Units.AttributeMappings.BaseUnitMapping import BaseUnitMapping
from ResSimpy.Units.Units import (HeatCapacity, UnitDimension, Viscosity, Density, GasLiquidRatio, LiquidGasRatio,
                                  SolutionOilGasRatio, DeltaPressure, Temperature, ReservoirVolumeOverPressure,
                                  FormationVolumeFactorGas, FormationVolumeFactorLiquid, SolutionGasOilRatio,
                                  Dimensionless, Pressure, CriticalPressure, CriticalTemperature, CriticalVolume,
                                  Compressibility, Length, InverseTime, Permeability, ReservoirProductivityIndex,
                                  ReservoirVolume, SurfaceRatesLiquid, SurfaceRatesGas, GravityGradient,
                                  ValveCoefficient, Roughness, Diameter, InterfacialTension
                                  )


class WaterUnits(BaseUnitMapping):
    """Unit types for the attributes of water methods."""

    def __init__(self, unit_system: None | UnitSystem) -> None:
        """Initialises the WaterUnits class.

        Args:
            unit_system (None | UnitSystem): The unit system to use for the unit mapping.
        """
        super().__init__(unit_system=unit_system)

    attribute_map: Mapping[str, UnitDimension] = {
        'temperature': Temperature(),
        'reference_pressure': Pressure(),
        'water_density': Density(),
        'water_compressibility': Compressibility(),
        'water_formation_volume_factor': FormationVolumeFactorLiquid(),
        'water_viscosity': Viscosity(),
        'water_viscosity_compressibility': Compressibility()
    }

    @property
    def temperature(self) -> str:
        """Returns the unit for temperature."""
        return self.get_unit_for_attribute('temperature')

    @property
    def reference_pressure(self) -> str:
        """Returns the unit for reference_pressure."""
        return self.get_unit_for_attribute('reference_pressure')

    @property
    def water_density(self) -> str:
        """Returns the unit for water_density."""
        return self.get_unit_for_attribute('water_density')

    @property
    def water_compressibility(self) -> str:
        """Returns the unit for water_compressibility."""
        return self.get_unit_for_attribute('water_compressibility')

    @property
    def water_formation_volume_factor(self) -> str:
        """Returns the unit for water_formation_volume_factor."""
        return self.get_unit_for_attribute('water_formation_volume_factor')

    @property
    def water_viscosity(self) -> str:
        """Returns the unit for water_viscosity."""
        return self.get_unit_for_attribute('water_viscosity')

    @property
    def water_viscosity_compressibility(self) -> str:
        """Returns the unit for water_viscosity_compressibility."""
        return self.get_unit_for_attribute('water_viscosity_compressibility')


class SeparatorUnits(BaseUnitMapping):
    """Unit types for the attributes of separator methods."""

    def __init__(self, unit_system: None | UnitSystem) -> None:
        """Initialises the SeparatorUnits class.

        Args:
            unit_system (None | UnitSystem): unit system to get the unit from.
        """
        super().__init__(unit_system=unit_system)

    attribute_map: Mapping[str, UnitDimension] = {
        'temperature': Temperature(),
        'pressure': Pressure(),
        'standard_temperature': Temperature(),
        'standard_pressure': Pressure(),
    }

    @property
    def temperature(self) -> str:
        """Returns the unit for temperature."""
        return self.get_unit_for_attribute('temperature')

    @property
    def pressure(self) -> str:
        """Returns the unit for pressure."""
        return self.get_unit_for_attribute('pressure')

    @property
    def standard_temperature(self) -> str:
        """Returns the unit for standard_temperature."""
        return self.get_unit_for_attribute('standard_temperature')

    @property
    def standard_pressure(self) -> str:
        """Returns the unit for standard_pressure."""
        return self.get_unit_for_attribute('standard_pressure')


class RockUnits(BaseUnitMapping):
    """Unit types for the attributes of rock methods."""

    def __init__(self, unit_system: None | UnitSystem) -> None:
        """Initialises the RockUnits class.

        Args:
            unit_system (None | UnitSystem): unit system to get the unit from.
        """
        super().__init__(unit_system=unit_system)

    attribute_map: Mapping[str, UnitDimension] = {
        'rock_compressibility': Compressibility(),
        'rock_permeability_compressibility': Compressibility(),
        'reference_pressure': Pressure(),
        'pressure': Pressure(),
        'delta_pressure': DeltaPressure()
    }

    @property
    def rock_compressibility(self) -> str:
        """Returns the unit for rock_compressibility."""
        return self.get_unit_for_attribute('rock_compressibility')

    @property
    def rock_permeability_compressibility(self) -> str:
        """Returns the unit for rock_permeability_compressibility."""
        return self.get_unit_for_attribute('rock_permeability_compressibility')

    @property
    def reference_pressure(self) -> str:
        """Returns the unit for reference_pressure."""
        return self.get_unit_for_attribute('reference_pressure')

    @property
    def pressure(self) -> str:
        """Returns the unit for pressure."""
        return self.get_unit_for_attribute('pressure')

    @property
    def delta_pressure(self) -> str:
        """Returns the unit for delta_pressure."""
        return self.get_unit_for_attribute('delta_pressure')


class RelPermUnits(BaseUnitMapping):
    """Unit types for the attributes of relative permeability and capillary pressure methods."""

    def __init__(self, unit_system: None | UnitSystem) -> None:
        """Initialises the RelPermUnits class.

        Args:
            unit_system (None | UnitSystem): unit system to get the unit from.
        """
        super().__init__(unit_system=unit_system)

    attribute_map: Mapping[str, UnitDimension] = {
        'water_oil_capillary_pressure': Pressure(),
        'gas_oil_capillary_pressure': Pressure(),
        'gas_water_capillary_pressure': Pressure(),
        'interfacial_tension_threshold_for_relperm_adjustment': InterfacialTension(),
        'reference_interfacial_tension_for_capillary_pressure_adjustment': InterfacialTension()
    }

    @property
    def water_oil_capillary_pressure(self) -> str:
        """Returns the unit for water_oil_capillary_pressure."""
        return self.get_unit_for_attribute('water_oil_capillary_pressure')

    @property
    def gas_oil_capillary_pressure(self) -> str:
        """Returns the unit for gas_oil_capillary_pressure."""
        return self.get_unit_for_attribute('gas_oil_capillary_pressure')

    @property
    def gas_water_capillary_pressure(self) -> str:
        """Returns the unit for gas_water_capillary_pressure."""
        return self.get_unit_for_attribute('gas_water_capillary_pressure')

    @property
    def interfacial_tension_threshold_for_relperm_adjustment(self) -> str:
        """Returns the unit for interfacial_tension_threshold_for_relperm_adjustment."""
        return self.get_unit_for_attribute('interfacial_tension_threshold_for_relperm_adjustment')

    @property
    def reference_interfacial_tension_for_capillary_pressure_adjustment(self) -> str:
        """Returns the unit for reference_interfacial_tension_for_capillary_pressure_adjustment."""
        return self.get_unit_for_attribute('reference_interfacial_tension_for_capillary_pressure_adjustment')


class HydraulicsUnits(BaseUnitMapping):
    """Unit types for the attributes of hydraulics, gaslift, valve, etc. methods."""

    def __init__(self, unit_system: None | UnitSystem, ratio_thousands: bool = True) -> None:
        """Initialises the HydraulicsUnits class.

        Args:
            unit_system (None | UnitSystem): unit system to get the unit from.
            ratio_thousands (bool): ??
        """
        self.ratio_thousands = ratio_thousands
        super().__init__(unit_system=unit_system)

    attribute_map: Mapping[str, UnitDimension] = {
        'surface_oil_rate': SurfaceRatesLiquid(),  # For use in hyd & gaslift methods
        'surface_liquid_rate': SurfaceRatesLiquid(),
        'surface_water_rate': SurfaceRatesLiquid(),
        'surface_gas_rate': SurfaceRatesGas(),
        'surface_wet_gas_rate': SurfaceRatesGas(),
        'mean_molecular_weight': Dimensionless(),
        'watercut': Dimensionless(),
        'oilcut': Dimensionless(),
        'pressure': Pressure(),
        'inlet_pressure': Pressure(),
        'outlet_pressure': Pressure(),
        'bottomhole_pressure': Pressure(),
        'tubinghead_pressure': Pressure(),
        'gas_liquid_ratio': GasLiquidRatio(),  # Note extra complexity in Nexus for VIP compatibility
        'gas_oil_ratio': SolutionGasOilRatio(),  # Note extra complexity in Nexus for VIP compatibility
        'oil_gas_ratio': LiquidGasRatio(),  # Note extra complexity in Nexus for VIP compatibility
        'water_gas_ratio': LiquidGasRatio(),  # Note extra complexity in Nexus for VIP compatibility
        'gas_water_ratio': GasLiquidRatio(),  # Note extra complexity in Nexus for VIP compatibility
        'water_wet_gas_ratio': LiquidGasRatio(),  # Note extra complexity in Nexus for VIP compatibility
        'length': Length(),
        'datum_depth': Length(),
        'depth_change': Length(),
        'hydraulic_table_vertical_distance': Length(),
        'injected_fluid_pressure_gradient': GravityGradient(),
        'viscosity': Viscosity(),
        'diameter': Diameter(),
        'roughness': Roughness(),
        'valve_coefficient': ValveCoefficient()  # For use in Valve method
    }

    @property
    def surface_oil_rate(self) -> str:
        """Returns the unit for surface_oil_rate."""
        return self.get_unit_for_attribute('surface_oil_rate')

    @property
    def surface_liquid_rate(self) -> str:
        """Returns the unit for surface_liquid_rate."""
        return self.get_unit_for_attribute('surface_liquid_rate')

    @property
    def surface_water_rate(self) -> str:
        """Returns the unit for surface_water_rate."""
        return self.get_unit_for_attribute('surface_water_rate')

    @property
    def surface_gas_rate(self) -> str:
        """Returns the unit for surface_gas_rate."""
        return self.get_unit_for_attribute('surface_gas_rate')

    @property
    def surface_wet_gas_rate(self) -> str:
        """Returns the unit for surface_wet_gas_rate."""
        return self.get_unit_for_attribute('surface_wet_gas_rate')

    @property
    def mean_molecular_weight(self) -> str:
        """Returns the unit for mean_molecular_weight."""
        return self.get_unit_for_attribute('mean_molecular_weight')

    @property
    def watercut(self) -> str:
        """Returns the unit for watercut."""
        return self.get_unit_for_attribute('watercut')

    @property
    def oilcut(self) -> str:
        """Returns the unit for oilcut."""
        return self.get_unit_for_attribute('oilcut')

    @property
    def pressure(self) -> str:
        """Returns the unit for pressure."""
        return self.get_unit_for_attribute('pressure')

    @property
    def inlet_pressure(self) -> str:
        """Returns the unit for inlet_pressure."""
        return self.get_unit_for_attribute('inlet_pressure')

    @property
    def outlet_pressure(self) -> str:
        """Returns the unit for outlet_pressure."""
        return self.get_unit_for_attribute('outlet_pressure')

    @property
    def bottomhole_pressure(self) -> str:
        """Returns the unit for bottomhole_pressure."""
        return self.get_unit_for_attribute('bottomhole_pressure')

    @property
    def tubinghead_pressure(self) -> str:
        """Returns the unit for tubinghead_pressure."""
        return self.get_unit_for_attribute('tubinghead_pressure')

    @property
    def gas_liquid_ratio(self) -> str:
        """Returns the unit for gas_liquid_ratio."""
        unit = self.get_unit_for_attribute('gas_liquid_ratio')
        if not self.ratio_thousands:
            unit = unit.replace('mscf', 'scf')
        return unit

    @property
    def gas_oil_ratio(self) -> str:
        """Returns the unit for gas_oil_ratio."""
        unit = self.get_unit_for_attribute('gas_oil_ratio')
        if not self.ratio_thousands:
            unit = unit.replace('mscf', 'scf')
        return unit

    @property
    def oil_gas_ratio(self) -> str:
        """Returns the unit for oil_gas_ratio."""
        unit = self.get_unit_for_attribute('oil_gas_ratio')
        if not self.ratio_thousands:
            unit = unit.replace('mscf', 'mmscf')
        return unit

    @property
    def water_gas_ratio(self) -> str:
        """Returns the unit for water_gas_ratio."""
        unit = self.get_unit_for_attribute('water_gas_ratio')
        if not self.ratio_thousands:
            unit = unit.replace('mscf', 'mmscf')
        return unit

    @property
    def gas_water_ratio(self) -> str:
        """Returns the unit for gas_water_ratio."""
        unit = self.get_unit_for_attribute('gas_water_ratio')
        if not self.ratio_thousands:
            unit = unit.replace('mscf', 'scf')
        return unit

    @property
    def water_wet_gas_ratio(self) -> str:
        """Returns the unit for water_wet_gas_ratio."""
        unit = self.get_unit_for_attribute('water_wet_gas_ratio')
        if not self.ratio_thousands:
            unit = unit.replace('mscf', 'mmscf')
        return unit

    @property
    def length(self) -> str:
        """Returns the unit for length."""
        return self.get_unit_for_attribute('length')

    @property
    def datum_depth(self) -> str:
        """Returns the unit for datum_depth."""
        return self.get_unit_for_attribute('datum_depth')

    @property
    def depth_change(self) -> str:
        """Returns the unit for depth_change."""
        return self.get_unit_for_attribute('depth_change')

    @property
    def hydraulic_table_vertical_distance(self) -> str:
        """Returns the unit for hydraulic_table_vertical_distance."""
        return self.get_unit_for_attribute('hydraulic_table_vertical_distance')

    @property
    def injected_fluid_pressure_gradient(self) -> str:
        """Returns the unit for injected_fluid_pressure_gradient."""
        return self.get_unit_for_attribute('injected_fluid_pressure_gradient')

    @property
    def viscosity(self) -> str:
        """Returns the unit for viscosity."""
        return self.get_unit_for_attribute('viscosity')

    @property
    def diameter(self) -> str:
        """Returns the unit for diameter."""
        return self.get_unit_for_attribute('diameter')

    @property
    def roughness(self) -> str:
        """Returns the unit for roughness."""
        return self.get_unit_for_attribute('roughness')

    @property
    def valve_coefficient(self) -> str:
        """Returns the unit for valve_coefficient."""
        return self.get_unit_for_attribute('valve_coefficient')


class EquilUnits(BaseUnitMapping):
    """Unit types for the attributes of equilibration methods."""

    def __init__(self, unit_system: None | UnitSystem) -> None:
        """Initialises the EquilUnits class.

        Args:
            unit_system (None | UnitSystem): unit system to get the unit from.
        """
        super().__init__(unit_system=unit_system)

    attribute_map: Mapping[str, UnitDimension] = {
        'initial_pressure': Pressure(),
        'datum_depth': Length(),
        'depth': Length(),
        'x': Length(),
        'y': Length(),
        'temperature': Temperature(),
        'initial_temperature': Temperature(),
        'gas_oil_contact_depth': Length(),
        'water_oil_contact_depth': Length(),
        'gas_water_contact_depth': Length(),
        'gas_oil_capillary_pressure_at_gas_oil_contact': Pressure(),
        'water_oil_capillary_pressure_at_water_oil_contact': Pressure(),
        'gas_water_capillary_pressure_at_gas_water_contact': Pressure(),
        'saturation_pressure': Pressure(),
        'oil_api_gravity': Dimensionless()
    }

    @property
    def initial_pressure(self) -> str:
        """Returns the unit for initial_pressure."""
        return self.get_unit_for_attribute('initial_pressure')

    @property
    def datum_depth(self) -> str:
        """Returns the unit for datum_depth."""
        return self.get_unit_for_attribute('datum_depth')

    @property
    def depth(self) -> str:
        """Returns the unit for depth."""
        return self.get_unit_for_attribute('depth')

    @property
    def x(self) -> str:
        """Returns the unit for x-coordinate."""
        return self.get_unit_for_attribute('x')

    @property
    def y(self) -> str:
        """Returns the unit for y-coordinate."""
        return self.get_unit_for_attribute('y')

    @property
    def temperature(self) -> str:
        """Returns the unit for temperature."""
        return self.get_unit_for_attribute('temperature')

    @property
    def initial_temperature(self) -> str:
        """Returns the unit for initial_temperature."""
        return self.get_unit_for_attribute('initial_temperature')

    @property
    def gas_oil_contact_depth(self) -> str:
        """Returns the unit for gas_oil_contact_depth."""
        return self.get_unit_for_attribute('gas_oil_contact_depth')

    @property
    def water_oil_contact_depth(self) -> str:
        """Returns the unit for water_oil_contact_depth."""
        return self.get_unit_for_attribute('water_oil_contact_depth')

    @property
    def gas_water_contact_depth(self) -> str:
        """Returns the unit for gas_water_contact_depth."""
        return self.get_unit_for_attribute('gas_water_contact_depth')

    @property
    def gas_oil_capillary_pressure_at_gas_oil_contact(self) -> str:
        """Returns the unit for gas_oil_capillary_pressure_at_gas_oil_contact."""
        return self.get_unit_for_attribute('gas_oil_capillary_pressure_at_gas_oil_contact')

    @property
    def water_oil_capillary_pressure_at_water_oil_contact(self) -> str:
        """Returns the unit for water_oil_capillary_pressure_at_water_oil_contact."""
        return self.get_unit_for_attribute('water_oil_capillary_pressure_at_water_oil_contact')

    @property
    def gas_water_capillary_pressure_at_gas_water_contact(self) -> str:
        """Returns the unit for gas_water_capillary_pressure_at_gas_water_contact."""
        return self.get_unit_for_attribute('gas_water_capillary_pressure_at_gas_water_contact')

    @property
    def saturation_pressure(self) -> str:
        """Returns the unit for saturation_pressure."""
        return self.get_unit_for_attribute('saturation_pressure')

    @property
    def oil_api_gravity(self) -> str:
        """Returns the unit for oil_api_gravity."""
        return self.get_unit_for_attribute('oil_api_gravity')


class AquiferUnits(BaseUnitMapping):
    """Unit types for the attributes of Aquifer methods."""

    def __init__(self, unit_system: None | UnitSystem) -> None:
        """Initialises the AquiferUnits class.

        Args:
            unit_system (None | UnitSystem): unit system to get the unit from.
        """
        super().__init__(unit_system=unit_system)

    attribute_map: Mapping[str, UnitDimension] = {
        'carter_tracy_constant': ReservoirVolumeOverPressure(),
        'total_compressibility': Compressibility(),
        'porosity': Dimensionless(),
        'thickness': Length(),
        'radius_to_inner_perimeter': Length(),
        'radius_to_exterior_perimeter': Length(),
        'fraction_of_circular_boundary': Dimensionless(),
        'linear_aquifer_width': Length(),
        'linear_aquifer_length': Length(),
        'time_conversion_factor': InverseTime(),
        'viscosity': Viscosity(),
        'permeability': Permeability(),
        'initial_aquifer_pressure': Pressure(),
        'datum_depth': Length(),
        'productivity_index': ReservoirProductivityIndex(),
        'initial_encroachable_water_volume': ReservoirVolume(),
        'initial_aquifer_volume': ReservoirVolume()
    }

    @property
    def carter_tracy_constant(self) -> str:
        """Returns the unit for carter_tracy_constant."""
        return self.get_unit_for_attribute('carter_tracy_constant')

    @property
    def total_compressibility(self) -> str:
        """Returns the unit for total_compressibility."""
        return self.get_unit_for_attribute('total_compressibility')

    @property
    def porosity(self) -> str:
        """Returns the unit for porosity."""
        return self.get_unit_for_attribute('porosity')

    @property
    def thickness(self) -> str:
        """Returns the unit for thickness."""
        return self.get_unit_for_attribute('thickness')

    @property
    def radius_to_inner_perimeter(self) -> str:
        """Returns the unit for radius_to_inner_perimeter."""
        return self.get_unit_for_attribute('radius_to_inner_perimeter')

    @property
    def radius_to_exterior_perimeter(self) -> str:
        """Returns the unit for radius_to_exterior_perimeter."""
        return self.get_unit_for_attribute('radius_to_exterior_perimeter')

    @property
    def fraction_of_circular_boundary(self) -> str:
        """Returns the unit for fraction_of_circular_boundary."""
        return self.get_unit_for_attribute('fraction_of_circular_boundary')

    @property
    def linear_aquifer_width(self) -> str:
        """Returns the unit for linear_aquifer_width."""
        return self.get_unit_for_attribute('linear_aquifer_width')

    @property
    def linear_aquifer_length(self) -> str:
        """Returns the unit for linear_aquifer_length."""
        return self.get_unit_for_attribute('linear_aquifer_length')

    @property
    def time_conversion_factor(self) -> str:
        """Returns the unit for time_conversion_factor."""
        return self.get_unit_for_attribute('time_conversion_factor')

    @property
    def viscosity(self) -> str:
        """Returns the unit for viscosity."""
        return self.get_unit_for_attribute('viscosity')

    @property
    def permeability(self) -> str:
        """Returns the unit for permeability."""
        return self.get_unit_for_attribute('permeability')

    @property
    def initial_aquifer_pressure(self) -> str:
        """Returns the unit for initial_aquifer_pressure."""
        return self.get_unit_for_attribute('initial_aquifer_pressure')

    @property
    def datum_depth(self) -> str:
        """Returns the unit for datum_depth."""
        return self.get_unit_for_attribute('datum_depth')

    @property
    def productivity_index(self) -> str:
        """Returns the unit for productivity_index."""
        return self.get_unit_for_attribute('productivity_index')

    @property
    def initial_encroachable_water_volume(self) -> str:
        """Returns the unit for initial_encroachable_water_volume."""
        return self.get_unit_for_attribute('initial_encroachable_water_volume')

    @property
    def initial_aquifer_volume(self) -> str:
        """Returns the unit for initial_aquifer_volume."""
        return self.get_unit_for_attribute('initial_aquifer_volume')


class PVTUnits(BaseUnitMapping):
    """Unit types for the attributes of PVT methods."""

    def __init__(self, unit_system: None | UnitSystem) -> None:
        """Initialises the PVTUnits class.

        Args:
            unit_system (None | UnitSystem): unit system to get the unit from.
        """
        super().__init__(unit_system=unit_system)

    attribute_map: Mapping[str, UnitDimension] = {
        'pressure': Pressure(),
        'temperature': Temperature(),
        'delta_pressure': DeltaPressure(),
        'oil_density': Density(),
        'gas_density': Density(),
        'oil_api_gravity': Dimensionless(),
        'gas_specific_gravity': Dimensionless(),
        'molecular_weight_of_residual_oil': Dimensionless(),
        'oil_viscosity': Viscosity(),
        'gas_viscosity': Viscosity(),
        'oil_formation_volume_factor': FormationVolumeFactorLiquid(),
        'gas_formation_volume_factor': FormationVolumeFactorGas(),
        'solution_gas_oil_ratio': SolutionGasOilRatio(),
        'solution_oil_gas_ratio': SolutionOilGasRatio(),
        'saturation_pressure': Pressure(),
        'gas_oil_ratio': GasLiquidRatio(),
        'oil_gas_ratio': LiquidGasRatio(),
        'gas_heat_capacity_at_constant_volume': HeatCapacity(),
        'gas_heat_capacity_at_constant_pressure': HeatCapacity(),
        'oil_fvf_over_oil_fvf_at_saturation_pressure': Dimensionless(),
        'oil_viscosity_over_oil_viscosity_at_saturation_pressure': Dimensionless(),
        'gas_fvf_over_gas_fvf_at_saturation_pressure': Dimensionless(),
        'gas_viscosity_over_gas_viscosity_at_saturation_pressure': Dimensionless(),
        'gas_heat_capacity_at_constant_volume_over_cv_at_saturation_pressure': Dimensionless(),
        'gas_heat_capacity_at_constant_pressure_over_cp_at_saturation_pressure': Dimensionless(),
        'critical_pressure': CriticalPressure(),
        'critical_temperature': CriticalTemperature(),
        'critical_volume': CriticalVolume()
    }

    @property
    def pressure(self) -> str:
        """Returns the unit for pressure."""
        return self.get_unit_for_attribute('pressure')

    @property
    def temperature(self) -> str:
        """Returns the unit for temperature."""
        return self.get_unit_for_attribute('temperature')

    @property
    def delta_pressure(self) -> str:
        """Returns the unit for delta_pressure."""
        return self.get_unit_for_attribute('delta_pressure')

    @property
    def oil_density(self) -> str:
        """Returns the unit for oil_density."""
        return self.get_unit_for_attribute('oil_density')

    @property
    def gas_density(self) -> str:
        """Returns the unit for gas_density."""
        return self.get_unit_for_attribute('gas_density')

    @property
    def oil_api_gravity(self) -> str:
        """Returns the unit for oil_api_gravity."""
        return self.get_unit_for_attribute('oil_api_gravity')

    @property
    def gas_specific_gravity(self) -> str:
        """Returns the unit for gas_specific_gravity."""
        return self.get_unit_for_attribute('gas_specific_gravity')

    @property
    def molecular_weight_of_residual_oil(self) -> str:
        """Returns the unit for molecular_weight_of_residual_oil."""
        return self.get_unit_for_attribute('molecular_weight_of_residual_oil')

    @property
    def oil_viscosity(self) -> str:
        """Returns the unit for oil_viscosity."""
        return self.get_unit_for_attribute('oil_viscosity')

    @property
    def gas_viscosity(self) -> str:
        """Returns the unit for gas_viscosity."""
        return self.get_unit_for_attribute('gas_viscosity')

    @property
    def oil_formation_volume_factor(self) -> str:
        """Returns the unit for oil_formation_volume_factor."""
        return self.get_unit_for_attribute('oil_formation_volume_factor')

    @property
    def gas_formation_volume_factor(self) -> str:
        """Returns the unit for gas_formation_volume_factor."""
        return self.get_unit_for_attribute('gas_formation_volume_factor')

    @property
    def solution_gas_oil_ratio(self) -> str:
        """Returns the unit for solution_gas_oil_ratio."""
        return self.get_unit_for_attribute('solution_gas_oil_ratio')

    @property
    def solution_oil_gas_ratio(self) -> str:
        """Returns the unit for solution_oil_gas_ratio."""
        return self.get_unit_for_attribute('solution_oil_gas_ratio')

    @property
    def saturation_pressure(self) -> str:
        """Returns the unit for saturation_pressure."""
        return self.get_unit_for_attribute('saturation_pressure')

    @property
    def gas_oil_ratio(self) -> str:
        """Returns the unit for gas_oil_ratio."""
        return self.get_unit_for_attribute('gas_oil_ratio')

    @property
    def oil_gas_ratio(self) -> str:
        """Returns the unit for oil_gas_ratio."""
        return self.get_unit_for_attribute('oil_gas_ratio')

    @property
    def gas_heat_capacity_at_constant_volume(self) -> str:
        """Returns the unit for gas_heat_capacity_at_constant_volume."""
        return self.get_unit_for_attribute('gas_heat_capacity_at_constant_volume')

    @property
    def gas_heat_capacity_at_constant_pressure(self) -> str:
        """Returns the unit for gas_heat_capacity_at_constant_pressure."""
        return self.get_unit_for_attribute('gas_heat_capacity_at_constant_pressure')

    @property
    def oil_fvf_over_oil_fvf_at_saturation_pressure(self) -> str:
        """Returns the unit for oil_fvf_over_oil_fvf_at_saturation_pressure."""
        return self.get_unit_for_attribute('oil_fvf_over_oil_fvf_at_saturation_pressure')

    @property
    def oil_viscosity_over_oil_viscosity_at_saturation_pressure(self) -> str:
        """Returns the unit for oil_viscosity_over_oil_viscosity_at_saturation_pressure."""
        return self.get_unit_for_attribute('oil_viscosity_over_oil_viscosity_at_saturation_pressure')

    @property
    def gas_fvf_over_gas_fvf_at_saturation_pressure(self) -> str:
        """Returns the unit for gas_fvf_over_gas_fvf_at_saturation_pressure."""
        return self.get_unit_for_attribute('gas_fvf_over_gas_fvf_at_saturation_pressure')

    @property
    def gas_viscosity_over_gas_viscosity_at_saturation_pressure(self) -> str:
        """Returns the unit for gas_viscosity_over_gas_viscosity_at_saturation_pressure."""
        return self.get_unit_for_attribute('gas_viscosity_over_gas_viscosity_at_saturation_pressure')

    @property
    def gas_heat_capacity_at_constant_volume_over_cv_at_saturation_pressure(self) -> str:
        """Returns the unit for gas_heat_capacity_at_constant_volume_over_cv_at_saturation_pressure."""
        return self.get_unit_for_attribute('gas_heat_capacity_at_constant_volume_over_cv_at_saturation_pressure')

    @property
    def gas_heat_capacity_at_constant_pressure_over_cp_at_saturation_pressure(self) -> str:
        """Returns the unit for gas_heat_capacity_at_constant_pressure_over_cp_at_saturation_pressure."""
        return self.get_unit_for_attribute('gas_heat_capacity_at_constant_pressure_over_cp_at_saturation_pressure')

    @property
    def critical_pressure(self) -> str:
        """Returns the unit for critical_pressure."""
        return self.get_unit_for_attribute('critical_pressure')

    @property
    def critical_temperature(self) -> str:
        """Returns the unit for critical_temperature."""
        return self.get_unit_for_attribute('critical_temperature')

    @property
    def critical_volume(self) -> str:
        """Returns the unit for critical_volume."""
        return self.get_unit_for_attribute('critical_volume')


class OptionsUnits(BaseUnitMapping):
    """Unit types for the attributes of simulator options."""

    def __init__(self, unit_system: None | UnitSystem) -> None:
        """Initialises the OptionsUnits class.

        Args:
            unit_system (None | UnitSystem): unit system to get the unit from.
        """
        super().__init__(unit_system=unit_system)

    attribute_map: Mapping[str, UnitDimension] = {
        'standard_pressure': Pressure(),
        'standard_temperature': Temperature(),
        'reservoir_temperature': Temperature()
    }

    @property
    def standard_pressure(self) -> str:
        """Returns the unit for standard pressure."""
        return self.get_unit_for_attribute('standard_pressure')

    @property
    def standard_temperature(self) -> str:
        """Returns the unit for standard temperature."""
        return self.get_unit_for_attribute('standard_temperature')

    @property
    def reservoir_temperature(self) -> str:
        """Returns the unit for reservoir temperature."""
        return self.get_unit_for_attribute('reservoir_temperature')
