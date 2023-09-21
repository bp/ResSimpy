from typing import Mapping

from ResSimpy.Units.AttributeMappings.AttributeMappingBase import AttributeMapBase
from ResSimpy.Units.Units import (UnitDimension, Viscosity, Density,
                                  FormationVolumeFactorGas, FormationVolumeFactorOil, SolutionGasOilRatio,
                                  Dimensionless, Pressure)


class PVTUnits(AttributeMapBase):
    """Unit types for the attributes of PVT methods."""
    attribute_map: Mapping[str, UnitDimension] = {
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
