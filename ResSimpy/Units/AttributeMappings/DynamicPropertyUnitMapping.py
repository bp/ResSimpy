from typing import Mapping
from ResSimpy.Enums.UnitsEnum import UnitSystem

from ResSimpy.Units.AttributeMappings.BaseUnitMapping import BaseUnitMapping
from ResSimpy.Units.Units import (UnitDimension, Viscosity, Density,
                                  FormationVolumeFactorGas, FormationVolumeFactorOil, SolutionGasOilRatio,
                                  Dimensionless, Pressure)


class PVTUnits(BaseUnitMapping):
    """Unit types for the attributes of PVT methods."""

    def __init__(self, unit_system: None | UnitSystem) -> None:
        super().__init__(unit_system=unit_system)
        self.attribute_map: Mapping[str, UnitDimension] = {
            'pressure': Pressure(),
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
            'saturation_pressure': Pressure(),
        }

    @property
    def pressure(self) -> str:
        """Returns the unit for pressure."""
        return self.get_unit_from_attribute('pressure')
