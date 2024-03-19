"""Unit types for the attributes of a well completion."""
from typing import Mapping

from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Units.AttributeMappings.BaseUnitMapping import BaseUnitMapping
from ResSimpy.Units.Units import UnitDimension, Length, Temperature, Dimensionless, \
    Angle, PermeabilityThickness, Permeability, NonDarcySkin


class CompletionUnits(BaseUnitMapping):
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
        'dfactor': NonDarcySkin(),
        'rel_perm_method': Dimensionless(),
        'status': Dimensionless(),
        'measured_depth': Length(),
        'well_indices': Dimensionless(),
        'partial_perf': Dimensionless(),
        'cell_number': Dimensionless(),
        'peaceman_well_block_radius': Length(),
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

    def __init__(self, unit_system: None | UnitSystem) -> None:
        """Initialises the CompletionUnits class.

        Args:
            unit_system (None | UnitSystem): The unit system to use for the unit mapping.
        """
        super().__init__(unit_system=unit_system)

    @property
    def i(self) -> str:
        """Returns the unit for i."""
        return self.get_unit_for_attribute('i')

    @property
    def j(self) -> str:
        """Returns the unit for j."""
        return self.get_unit_for_attribute('j')

    @property
    def k(self) -> str:
        """Returns the unit for k."""
        return self.get_unit_for_attribute('k')

    @property
    def x(self) -> str:
        """Returns the unit for x."""
        return self.get_unit_for_attribute('x')

    @property
    def y(self) -> str:
        """Returns the unit for y."""
        return self.get_unit_for_attribute('y')

    @property
    def depth(self) -> str:
        """Returns the unit for depth."""
        return self.get_unit_for_attribute('depth')

    @property
    def depth_to_top(self) -> str:
        """Returns the unit for depth_to_top."""
        return self.get_unit_for_attribute('depth_to_top')

    @property
    def depth_to_bottom(self) -> str:
        """Returns the unit for depth_to_bottom."""
        return self.get_unit_for_attribute('depth_to_bottom')

    @property
    def well_radius(self) -> str:
        """Returns the unit for well_radius."""
        return self.get_unit_for_attribute('well_radius')

    @property
    def skin(self) -> str:
        """Returns the unit for skin."""
        return self.get_unit_for_attribute('skin')

    @property
    def angle_a(self) -> str:
        """Returns the unit for angle_a."""
        return self.get_unit_for_attribute('angle_a')

    @property
    def angle_v(self) -> str:
        """Returns the unit for angle_v."""
        return self.get_unit_for_attribute('angle_v')

    @property
    def grid(self) -> str:
        """Returns the unit for grid."""
        return self.get_unit_for_attribute('grid')

    @property
    def perm_thickness_ovr(self) -> str:
        """Returns the unit for perm_thickness_ovr."""
        return self.get_unit_for_attribute('perm_thickness_ovr')

    @property
    def dfactor(self) -> str:
        """Returns the unit for dfactor."""
        return self.get_unit_for_attribute('dfactor')

    @property
    def rel_perm_method(self) -> str:
        """Returns the unit for rel_perm_method."""
        return self.get_unit_for_attribute('rel_perm_method')

    @property
    def status(self) -> str:
        """Returns the unit for status."""
        return self.get_unit_for_attribute('status')

    @property
    def measured_depth(self) -> str:
        """Returns the unit for measured_depth."""
        return self.get_unit_for_attribute('measured_depth')

    @property
    def well_indices(self) -> str:
        """Returns the unit for well_indices."""
        return self.get_unit_for_attribute('well_indices')

    @property
    def partial_perf(self) -> str:
        """Returns the unit for partial_perf."""
        return self.get_unit_for_attribute('partial_perf')

    @property
    def cell_number(self) -> str:
        """Returns the unit for cell_number."""
        return self.get_unit_for_attribute('cell_number')

    @property
    def peaceman_well_block_radius(self) -> str:
        """Returns the unit for peaceman_well_block_radius."""
        return self.get_unit_for_attribute('peaceman_well_block_radius')

    @property
    def portype(self) -> str:
        """Returns the unit for portype."""
        return self.get_unit_for_attribute('portype')

    @property
    def facture_mult(self) -> str:
        """Returns the unit for facture_mult."""
        return self.get_unit_for_attribute('facture_mult')

    @property
    def sector(self) -> str:
        """Returns the unit for sector."""
        return self.get_unit_for_attribute('sector')

    @property
    def well_group(self) -> str:
        """Returns the unit for well_group."""
        return self.get_unit_for_attribute('well_group')

    @property
    def zone(self) -> str:
        """Returns the unit for zone."""
        return self.get_unit_for_attribute('zone')

    @property
    def angle_open_flow(self) -> str:
        """Returns the unit for angle_open_flow."""
        return self.get_unit_for_attribute('angle_open_flow')

    @property
    def temperature(self) -> str:
        """Returns the unit for temperature."""
        return self.get_unit_for_attribute('temperature')

    @property
    def flowsector(self) -> str:
        """Returns the unit for flowsector."""
        return self.get_unit_for_attribute('flowsector')

    @property
    def parent_node(self) -> str:
        """Returns the unit for parent_node."""
        return self.get_unit_for_attribute('parent_node')

    @property
    def mdcon(self) -> str:
        """Returns the unit for mdcon."""
        return self.get_unit_for_attribute('mdcon')

    @property
    def pressure_avg_pattern(self) -> str:
        """Returns the unit for pressure_avg_pattern."""
        return self.get_unit_for_attribute('pressure_avg_pattern')

    @property
    def length(self) -> str:
        """Returns the unit for length."""
        return self.get_unit_for_attribute('length')

    @property
    def permeability(self) -> str:
        """Returns the unit for permeability."""
        return self.get_unit_for_attribute('permeability')

    @property
    def non_darcy_model(self) -> str:
        """Returns the unit for non_darcy_model."""
        return self.get_unit_for_attribute('non_darcy_model')

    @property
    def comp_dz(self) -> str:
        """Returns the unit for comp_dz."""
        return self.get_unit_for_attribute('comp_dz')

    @property
    def layer_assignment(self) -> str:
        """Returns the unit for layer_assignment."""
        return self.get_unit_for_attribute('layer_assignment')

    @property
    def polymer_block_radius(self) -> str:
        """Returns the unit for polymer_block_radius."""
        return self.get_unit_for_attribute('polymer_block_radius')

    @property
    def polymer_well_radius(self) -> str:
        """Returns the unit for polymer_well_radius."""
        return self.get_unit_for_attribute('polymer_well_radius')

    @property
    def rel_perm_end_point(self) -> str:
        """Returns the unit for rel_perm_end_point."""
        return self.get_unit_for_attribute('rel_perm_end_point')

    @property
    def kh_mult(self) -> str:
        """Returns the unit for kh_mult."""
        return self.get_unit_for_attribute('kh_mult')
