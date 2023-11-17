from typing import Mapping
from ResSimpy.Enums.UnitsEnum import UnitSystem

from ResSimpy.Units.AttributeMappings.BaseUnitMapping import BaseUnitMapping
from ResSimpy.Units.Units import (HeatCapacity, UnitDimension, Viscosity, Density, GasLiquidRatio, LiquidGasRatio,
                                  SolutionOilGasRatio, DeltaPressure, Temperature, ReservoirVolumeOverPressure,
                                  FormationVolumeFactorGas, FormationVolumeFactorOil, SolutionGasOilRatio,
                                  Dimensionless, Pressure, CriticalPressure, CriticalTemperature, CriticalVolume,
                                  Compressibility, Length, InverseTime, Permeability, ReservoirProductivityIndex,
                                  ReservoirVolume
                                  )


class AquiferUnits(BaseUnitMapping):
    """Unit types for the attributes of Aquifer methods."""

    def __init__(self, unit_system: None | UnitSystem) -> None:
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
        'oil_formation_volume_factor': FormationVolumeFactorOil(),
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
