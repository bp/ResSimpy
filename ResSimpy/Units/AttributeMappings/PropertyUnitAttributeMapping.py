from typing import Mapping

from ResSimpy.Units.AttributeMappings.AttributeMappingBase import AttributeMapBase
from ResSimpy.Units.Units import UnitDimension, Viscosity


class PropertyUnits(AttributeMapBase):
    attribute_map: Mapping[str, UnitDimension] = {
        'vo': Viscosity(),
        'vg': Viscosity(),
        'vw': Viscosity(),

    }
