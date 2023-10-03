from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
import pytest

from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.DataModels.Network.NexusConstraint import NexusConstraint
from ResSimpy.Nexus.DataModels.Network.NexusNode import NexusNode
from ResSimpy.Nexus.DataModels.Network.NexusNodeConnection import NexusNodeConnection
from ResSimpy.Nexus.DataModels.Network.NexusTarget import NexusTarget
from ResSimpy.Nexus.DataModels.Network.NexusWellConnection import NexusWellConnection
from ResSimpy.Nexus.DataModels.Network.NexusWellbore import NexusWellbore
from ResSimpy.Nexus.DataModels.Network.NexusWellhead import NexusWellhead
from ResSimpy.Nexus.DataModels.NexusCompletion import NexusCompletion
from ResSimpy.Units.Units import Area
from ResSimpy.Units.AttributeMappings.ConstraintUnitMapping import ConstraintUnits
from ResSimpy.ISODateTime import ISODateTime


@pytest.mark.parametrize('unit_system, expected_result', [
    (UnitSystem.ENGLISH, 'ft2'),
    (UnitSystem.LAB, 'cm2'),
    (UnitSystem.METRIC, 'm2'),
    (UnitSystem.METKGCM2, 'm2'),
    (UnitSystem.METBAR, 'm2'),
    (UnitSystem.METRIC_ATM, 'm2'),
]
    , ids=['ENGLISH', 'LAB', 'METRIC', 'METKGCM2', 'METBAR', 'METRIC_ATM'])
def test_unit_system_enum_to_variable(unit_system, expected_result):
    """Tests the unit_system_enum_to_variable method."""
    # Arrange
    unit_dimension = Area()
    # Act
    result = unit_dimension.unit_system_enum_to_variable(unit_system=unit_system)
    # Assert
    assert result == expected_result


@pytest.mark.parametrize('attribute, unit_system, expected_result', [
    ('max_surface_water_rate', UnitSystem.ENGLISH, 'STB/day'),
    ('max_lgr_perfplus', UnitSystem.METRIC, 'STM3/SM3'),
    ('min_reverse_reservoir_water_rate', UnitSystem.LAB, 'cc/hour'),
    ('max_surface_oil_rate', UnitSystem.METRIC_ATM, 'STM3/day'),
    ('max_surface_gas_rate', UnitSystem.METBAR, 'SM3/day'),
    ('max_surface_liquid_rate', UnitSystem.METKGCM2, 'STM3/day'),
    ('max_reservoir_oil_rate', UnitSystem.METRIC, 'm3/day'),
    ('max_reservoir_gas_rate', UnitSystem.METRIC, 'm3/day'),
    ('min_pressure', UnitSystem.METRIC, 'kPa'),
    ('max_pressure', UnitSystem.METRIC_ATM, 'atm'),
    ('max_pressure', UnitSystem.METKGCM2, 'kg/cm2'),
    ('min_temperature', UnitSystem.ENGLISH, 'degrees F'),
])
def test_get_unit(attribute, unit_system, expected_result):
    """Tests the get_unit method."""
    # Arrange
    unit_dimension = ConstraintUnits(unit_system=unit_system)

    # Act
    result = unit_dimension.get_unit_from_attribute(attribute_name=attribute)
    # Assert
    assert result == expected_result


def test_get_unit_upper():
    """Tests the get_unit method."""
    # Arrange
    unit_dimension = ConstraintUnits(unit_system=UnitSystem.ENGLISH)

    # Act
    result = unit_dimension.get_unit_from_attribute(attribute_name='max_surface_water_rate', uppercase=True)
    # Assert
    assert result == 'STB/DAY'


def test_get_unit_error():
    """Tests the get_unit method."""
    # Arrange
    unit_dimension = ConstraintUnits(unit_system=UnitSystem.ENGLISH)

    # Act
    with pytest.raises(AttributeError) as ae:
        unit_dimension.get_unit_from_attribute(attribute_name='not_an_attribute')
    assert str(ae.value) == 'Attribute not_an_attribute not recognised and does not have a unit definition'


@pytest.mark.parametrize('data_object, attribute, expected_result, upper', [
    (NexusConstraint, 'max_surface_water_rate', 'STB/day', False),
    (NexusNode, 'depth', 'ft', False),
    (NexusNodeConnection, 'diameter', 'in', False),
    (NexusWellbore, 'measured_depth_in', 'ft', False),
    (NexusCompletion, 'angle_a', 'degrees', False),
    (NexusCompletion, 'angle_a', 'DEGREES', True),
    (NexusTarget, 'calculation_method', '', True),
    (NexusWellhead, 'dp_add', 'psi', False),
    (NexusWellConnection, 'dt_add', 'DEGREES F', True),
])
def test_get_unit_for_attribute(mocker, data_object, attribute, expected_result, upper):
    """Write a test to check that the DataObjectMixin.get_unit_for_attribute method works as expected."""
    # Arrange
    # patch out convert_to_iso from the ISODateTime module as it is not needed for this test
    mocker.patch.object(ISODateTime, 'convert_to_iso', return_value=ISODateTime(2021, 1, 1))
    dataobj = data_object({})
    # Act
    result = dataobj.get_unit_for_attribute(attribute_name=attribute, unit_system=UnitSystem.ENGLISH, uppercase=upper)
    # Assert
    assert result == expected_result


@pytest.mark.parametrize('attribute, expected_unit', [
    ('depth', 'ft'),
    ('bhdepth', 'ft'),
    ('diameter', 'in'),
    ('datum_depth', 'ft'),
    ('x_pos', 'ft'),
    ('y_pos', 'ft'),
    ('length', 'ft'),
    ('temp', 'degrees F'),
    ('roughness', 'in'),
    ('inner_diameter', 'in'),
    ('productivity_index', 'STB/day/psi'),
    ('rate_mult', ''),
    ('dp_add', 'psi'),
    ('dt_add', 'degrees F'),
    ('well_index_mult', ''),
    ('vip_productivity_index', 'STB/day/psi'),
    ('d_factor', 'day/MSCF'),
    ('gas_mobility', ''),
    ('drill_order_benefit', ''),
    ('heat_transfer_coeff', 'BTU/(hr*ft2*F)'),
    ('non_darcy_flow_model', ''),
    ('non_darcy_flow_method', ''),
    ('capillary_number_model', ''),
    ('on_time', ''),
    ('crossflow', ''),
    ('crossshut', ''),
    ('inj_mobility', ''),
    ('temperature_profile', ''),
    ('elevation_profile', ''),
    ('measured_depth_in', 'ft'),
    ('measured_depth_out', 'ft'),
    ('delta_depth', 'ft'),
    ('temp', 'degrees F'),
    ('hyd_method', ''),
    ('pvt_method', ''),
    ('water_method', ''),
    ('bat_method', ''),
    ('number', ''),
    ('gradient_calc', ''),
    ('add_tubing', ''),
    ('tracer', ''),
    ('con_type', ''),
    ('bore_type', ''),
    ('control_quantity', ''),
    ('control_type', ''),
    ('control_condition', ''),
    ('control_method', ''),
    ('control_connections', ''),
    ('calculation_method', ''),
    ('calculation_conditions', ''),
    ('calculation_connections', ''),
    ('value', ''),
    ('add_value', ''),
    ('region', ''),
    ('priority', ''),
    ('minimum_rate', ''),
    ('minimum_rate_no_shut', ''),
    ('guide_rate', ''),
    ('max_change_pressure', 'psi'),
    ('rank_dt', 'days'),
    ('calculation_type', ''),
    ('temperature', 'degrees F'),
])
def test_network_unit_properties(attribute, expected_unit):
    # Arrange
    test_object = NexusNode(dict(date='01/01/2001', unit_system=UnitSystem.ENGLISH))
    # Act
    result = getattr(test_object.units, attribute)
    # Assert
    assert result == expected_unit


def test_object_attribute_property_completion():
    # Arrange
    test_object = NexusCompletion(date='01/01/2001', unit_system=UnitSystem.ENGLISH, date_format=DateFormat.DD_MM_YYYY)
    units = test_object.units
    # Act
    result_expected = [(units.depth, 'ft'),
                       (units.j, ''),
                       (units.k, ''),
                       (units.x, 'ft'),
                       (units.i, ''),
                       (units.y, 'ft'),
                       (units.depth_to_top, 'ft'),
                       (units.depth_to_bottom, 'ft'),
                       (units.well_radius, 'ft'),
                       (units.skin, ''),
                       (units.angle_a, 'degrees'),
                       (units.angle_v, 'degrees'),
                       (units.perm_thickness_ovr, 'md*ft'),
                       (units.dfactor, 'day/MSCF'),
                       (units.rel_perm_method, ''),
                       (units.status, ''),
                       (units.grid, ''),
                       (units.measured_depth, 'ft'),
                       (units.well_indices, ''),
                       (units.partial_perf, ''),
                       (units.cell_number, ''),
                       (units.bore_radius, 'ft'),
                       (units.portype, ''),
                       (units.facture_mult, ''),
                       (units.sector, ''),
                       (units.well_group, ''),
                       (units.zone, ''),
                       (units.angle_open_flow, 'degrees'),
                       (units.temperature, 'degrees F'),
                       (units.flowsector, ''),
                       (units.parent_node, ''),
                       (units.mdcon, ''),
                       (units.pressure_avg_pattern, ''),
                       (units.length, 'ft'),
                       (units.permeability, 'md'),
                       (units.non_darcy_model, ''),
                       (units.comp_dz, 'ft'),
                       (units.layer_assignment, ''),
                       (units.polymer_block_radius, 'ft'),
                       (units.polymer_well_radius, 'ft'),
                       (units.rel_perm_end_point, ''),
                       (units.kh_mult, ''),
                       ]
    # Assert
    for result, expected in result_expected:
        assert result == expected


@pytest.mark.parametrize('attribute, expected_unit', [
    ('max_gor', 'SM3/STM3'),
    ('max_gor_plug', 'SM3/STM3'),
    ('max_gor_plugplus', 'SM3/STM3'),
    ('max_gor_perf', 'SM3/STM3'),
    ('max_gor_perfplus', 'SM3/STM3'),
    ('max_lgr', 'STM3/SM3'),
    ('max_lgr_plug', 'STM3/SM3'),
    ('max_lgr_plugplus', 'STM3/SM3'),
    ('max_lgr_perf', 'STM3/SM3'),
    ('max_lgr_perfplus', 'STM3/SM3'),
    ('max_hc_moles_rate', 'kg-moles/day'),
    ('max_reverse_hc_moles_rate', 'kg-moles/day'),
    ('min_hc_moles_rate', 'kg-moles/day'),
    ('min_reverse_hc_moles_rate', 'kg-moles/day'),
    ('min_pressure', 'kPa'),
    ('max_pressure', 'kPa'),
    ('max_wag_water_pressure', 'kPa'),
    ('max_wag_gas_pressure', 'kPa'),
    ('bottom_hole_pressure', 'kPa'),
    ('tube_head_pressure', 'kPa'),
    ('max_reservoir_oil_rate', 'm3/day'),
    ('max_reservoir_water_rate', 'm3/day'),
    ('max_reservoir_gas_rate', 'm3/day'),
    ('max_reservoir_liquid_rate', 'm3/day'),
    ('max_reverse_reservoir_oil_rate', 'm3/day'),
    ('max_reverse_reservoir_water_rate', 'm3/day'),
    ('max_reverse_reservoir_gas_rate', 'm3/day'),
    ('max_reverse_reservoir_liquid_rate', 'm3/day'),
    ('min_reservoir_oil_rate', 'm3/day'),
    ('min_reservoir_water_rate', 'm3/day'),
    ('min_reservoir_gas_rate', 'm3/day'),
    ('min_reservoir_liquid_rate', 'm3/day'),
    ('min_reverse_reservoir_oil_rate', 'm3/day'),
    ('min_reverse_reservoir_water_rate', 'm3/day'),
    ('min_reverse_reservoir_gas_rate', 'm3/day'),
    ('min_reverse_reservoir_liquid_rate', 'm3/day'),
    ('max_watercut', 'fraction'),
    ('max_watercut_plugplus', 'fraction'),
    ('max_watercut_perf', 'fraction'),
    ('max_watercut_perfplus', 'fraction'),
    ('max_wor', 'fraction'),
    ('max_wor_plug', 'fraction'),
    ('max_wor_plugplus', 'fraction'),
    ('max_watercut_plug', 'fraction'),
    ('max_wor_perf', 'fraction'),
    ('max_wor_perfplus', 'fraction'),
    ('max_surface_gas_rate', 'SM3/day'),
    ('max_reverse_surface_gas_rate', 'SM3/day'),
    ('min_surface_gas_rate', 'SM3/day'),
    ('min_reverse_surface_gas_rate', 'SM3/day'),
    ('qmult_gas_rate', 'SM3/day'),
    ('max_surface_oil_rate', 'STM3/day'),
    ('max_surface_water_rate', 'STM3/day'),
    ('max_surface_liquid_rate', 'STM3/day'),
    ('max_reverse_surface_oil_rate', 'STM3/day'),
    ('max_reverse_surface_water_rate', 'STM3/day'),
    ('max_reverse_surface_liquid_rate', 'STM3/day'),
    ('min_surface_oil_rate', 'STM3/day'),
    ('min_surface_water_rate', 'STM3/day'),
    ('min_surface_liquid_rate', 'STM3/day'),
    ('min_reverse_surface_oil_rate', 'STM3/day'),
    ('min_reverse_surface_water_rate', 'STM3/day'),
    ('min_reverse_surface_liquid_rate', 'STM3/day'),
    ('qmult_oil_rate', 'STM3/day'),
    ('qmult_water_rate', 'STM3/day'),
    ('max_cum_gas_prod', 'k STM3'),
    ('max_cum_oil_prod', 'k STM3'),
    ('max_cum_water_prod', 'k STM3'),
    ('max_cum_liquid_prod', 'k STM3'),
    ('min_temperature', 'degrees C'),
])
def test_object_attribute_property_constraint(attribute, expected_unit):
    # Arrange
    test_object = NexusConstraint(dict(date='01/01/2001', unit_system=UnitSystem.METRIC))
    # Act
    result = getattr(test_object.units, attribute)
    # Assert
    assert result == expected_unit


def test_object_no_unit_system():
    # Arrange
    test_object = NexusConstraint(dict(date='01/01/2001'))
    expected_unit = ['STB/day', 'psi', 'fraction']
    # Act and Assert
    with pytest.raises(AttributeError) as ae:
        unit = test_object.units.max_surface_oil_rate
    assert str(ae.value) == 'Unit system not defined'
