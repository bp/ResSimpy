from typing import Mapping

from ResSimpy.Units.AttributeMappings.AttributeMappingBase import AttributeMapBase
from ResSimpy.Units.Units import UnitDimension, Length, Temperature, Dimensionless, \
    Angle, PermeabilityThickness, Permeability


class CompletionUnits(AttributeMapBase):
    """Unit types for the attributes of a well completion."""
    attribute_map: Mapping[str, UnitDimension] = {
        'i': Dimensionless(),
        'j': Dimensionless(),
        'k': Dimensionless(),
        'x': Length(),
        'y': Length(),
        'depth': Length(),
        'depth_to_top': Length(),
        'depth_to_bottom': Length(),
        'well_radius': Length(),
        'skin': Dimensionless(),
        'angle_a': Angle(),
        'angle_v': Angle(),
        'grid': Dimensionless(),
        'perm_thickness_ovr': PermeabilityThickness(),
        'dfactor': Dimensionless(),
        'rel_perm_method': Dimensionless(),
        'status': Dimensionless(),
        'measured_depth': Length(),
        'well_indices': Dimensionless(),
        'partial_perf': Dimensionless(),
        'cell_number': Dimensionless(),
        'bore_radius': Length(),
        'portype': Dimensionless(),
        'facture_mult': Dimensionless(),
        'sector': Dimensionless(),
        'well_group': Dimensionless(),
        'zone': Dimensionless(),
        'angle_open_flow': Angle(),
        'temperature': Temperature(),
        'flowsector': Dimensionless(),
        'parent_node': Dimensionless(),
        'mdcon': Dimensionless(),
        'pressure_avg_pattern': Dimensionless(),
        'length': Length(),
        'permeability': Permeability(),
        'non_darcy_model': Dimensionless(),
        'comp_dz': Length(),
        'layer_assignment': Dimensionless(),
        'polymer_block_radius': Length(),
        'polymer_well_radius': Length(),
        'rel_perm_end_point': Dimensionless(),
        'kh_mult': Dimensionless(),
    }
