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
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.NexusPVTMethod import NexusPVTMethod
from ResSimpy.Nexus.DataModels.NexusAquiferMethod import NexusAquiferMethod
from ResSimpy.Nexus.DataModels.NexusEquilMethod import NexusEquilMethod
from ResSimpy.Nexus.DataModels.NexusGasliftMethod import NexusGasliftMethod
from ResSimpy.Nexus.DataModels.NexusHydraulicsMethod import NexusHydraulicsMethod
from ResSimpy.Nexus.DataModels.NexusValveMethod import NexusValveMethod
from ResSimpy.Nexus.DataModels.NexusRelPermMethod import NexusRelPermMethod
from ResSimpy.Nexus.DataModels.NexusRockMethod import NexusRockMethod
from ResSimpy.Nexus.DataModels.NexusSeparatorMethod import NexusSeparatorMethod
from ResSimpy.Nexus.DataModels.NexusWaterMethod import NexusWaterMethod
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
], ids=['ENGLISH', 'LAB', 'METRIC', 'METKGCM2', 'METBAR', 'METRIC_ATM'])
def test_unit_system_enum_to_variable(unit_system, expected_result):
    """Tests the unit_system_enum_to_variable method."""
    # Arrange
    unit_dimension = Area()
    # Act
    result = unit_dimension.unit_system_enum_to_variable(unit_system=unit_system)
    # Assert
    assert result == expected_result


@pytest.mark.parametrize('attribute, unit_system, expected_result', [
    ('max_surface_water_rate', UnitSystem.ENGLISH, 'stb/day'),
    ('max_lgr_perfplus', UnitSystem.METRIC, 'stm3/stm3'),
    ('min_reverse_reservoir_water_rate', UnitSystem.LAB, 'cc/hour'),
    ('max_surface_oil_rate', UnitSystem.METRIC_ATM, 'stm3/day'),
    ('max_surface_gas_rate', UnitSystem.METBAR, 'stm3/day'),
    ('max_surface_liquid_rate', UnitSystem.METKGCM2, 'stm3/day'),
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
    result = unit_dimension.get_unit_for_attribute(attribute_name=attribute)
    # Assert
    assert result == expected_result


def test_get_unit_upper():
    """Tests the get_unit method."""
    # Arrange
    unit_dimension = ConstraintUnits(unit_system=UnitSystem.ENGLISH)

    # Act
    result = unit_dimension.get_unit_for_attribute(attribute_name='max_surface_water_rate', uppercase=True)
    # Assert
    assert result == 'STB/DAY'


def test_get_unit_error():
    """Tests the get_unit method."""
    # Arrange
    unit_dimension = ConstraintUnits(unit_system=UnitSystem.ENGLISH)

    # Act
    with pytest.raises(AttributeError) as ae:
        unit_dimension.get_unit_for_attribute(attribute_name='not_an_attribute')
    assert str(ae.value) == 'Attribute not_an_attribute not recognised and does not have a unit definition'


@pytest.mark.parametrize('data_object, attribute, expected_result, upper', [
    (NexusConstraint, 'max_surface_water_rate', 'stb/day', False),
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
    ('productivity_index', 'stb/day/psi'),
    ('rate_mult', ''),
    ('dp_add', 'psi'),
    ('dt_add', 'degrees F'),
    ('well_index_mult', ''),
    ('vip_productivity_index', 'stb/day/psi'),
    ('d_factor', 'day/mscf'),
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
    ('heat_conductivity', 'BTU/(hr*ft*F)'),
    ('insulation_thickness', 'in'),
    ('insulation_conductivity', 'BTU/(hr*ft*F)'),
    ('gravity_pressure_gradient_mult', ''),
    ('friction_pressure_gradient_mult', ''),
    ('acceleration_pressure_gradient_mult', ''),
    ('temperature_in', 'degrees F'),
    ('temperature_out', 'degrees F'),
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
                       (units.dfactor, 'day/mscf'),
                       (units.rel_perm_method, ''),
                       (units.status, ''),
                       (units.grid, ''),
                       (units.measured_depth, 'ft'),
                       (units.well_indices, ''),
                       (units.partial_perf, ''),
                       (units.cell_number, ''),
                       (units.peaceman_well_block_radius, 'ft'),
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
    ('max_gor', 'stm3/stm3'),
    ('max_gor_plug', 'stm3/stm3'),
    ('max_gor_plugplus', 'stm3/stm3'),
    ('max_gor_perf', 'stm3/stm3'),
    ('max_gor_perfplus', 'stm3/stm3'),
    ('max_lgr', 'stm3/stm3'),
    ('max_lgr_plug', 'stm3/stm3'),
    ('max_lgr_plugplus', 'stm3/stm3'),
    ('max_lgr_perf', 'stm3/stm3'),
    ('max_lgr_perfplus', 'stm3/stm3'),
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
    ('max_surface_gas_rate', 'stm3/day'),
    ('max_reverse_surface_gas_rate', 'stm3/day'),
    ('min_surface_gas_rate', 'stm3/day'),
    ('min_reverse_surface_gas_rate', 'stm3/day'),
    ('qmult_gas_rate', 'stm3/day'),
    ('max_surface_oil_rate', 'stm3/day'),
    ('max_surface_water_rate', 'stm3/day'),
    ('max_surface_liquid_rate', 'stm3/day'),
    ('max_reverse_surface_oil_rate', 'stm3/day'),
    ('max_reverse_surface_water_rate', 'stm3/day'),
    ('max_reverse_surface_liquid_rate', 'stm3/day'),
    ('min_surface_oil_rate', 'stm3/day'),
    ('min_surface_water_rate', 'stm3/day'),
    ('min_surface_liquid_rate', 'stm3/day'),
    ('min_reverse_surface_oil_rate', 'stm3/day'),
    ('min_reverse_surface_water_rate', 'stm3/day'),
    ('min_reverse_surface_liquid_rate', 'stm3/day'),
    ('qmult_oil_rate', 'stm3/day'),
    ('qmult_water_rate', 'stm3/day'),
    ('max_cum_gas_prod', 'k stm3'),
    ('max_cum_oil_prod', 'k stm3'),
    ('max_cum_water_prod', 'k stm3'),
    ('max_cum_liquid_prod', 'k stm3'),
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
    # Act and Assert
    with pytest.raises(AttributeError) as ae:
        _ = test_object.units.max_surface_oil_rate
    assert str(ae.value) == 'Unit system not defined'


@pytest.mark.parametrize('data_object, attribute, expected_result, upper, unitsystem', [
    (NexusPVTMethod, 'pressure', 'PSIA', True, UnitSystem.ENGLISH),
    (NexusPVTMethod, 'oil_density', 'kg/m3', False, UnitSystem.METRIC),
    (NexusPVTMethod, 'gas_heat_capacity_at_constant_volume', 'kJ/(kg*K)', False, UnitSystem.METBAR),
    (NexusAquiferMethod, 'initial_aquifer_pressure', 'PSIA', True, UnitSystem.ENGLISH),
    (NexusAquiferMethod, 'total_compressibility', 'kPa-1', False, UnitSystem.METRIC),
    (NexusAquiferMethod, 'time_conversion_factor', '1/days', False, UnitSystem.METBAR),
    (NexusEquilMethod, 'initial_pressure', 'PSIA', True, UnitSystem.ENGLISH),
    (NexusEquilMethod, 'datum_depth', 'm', False, UnitSystem.METRIC),
    (NexusEquilMethod, 'oil_api_gravity', '', False, UnitSystem.METBAR),
    (NexusGasliftMethod, 'gas_liquid_ratio', 'MSCF/STB', True, UnitSystem.ENGLISH),
    (NexusGasliftMethod, 'surface_oil_rate', 'stm3/day', False, UnitSystem.METRIC),
    (NexusGasliftMethod, 'pressure', 'bars', False, UnitSystem.METBAR),
    (NexusHydraulicsMethod, 'surface_wet_gas_rate', 'MSCF/DAY', True, UnitSystem.ENGLISH),
    (NexusHydraulicsMethod, 'oilcut', '', False, UnitSystem.METRIC),
    (NexusHydraulicsMethod, 'roughness', 'mm', False, UnitSystem.METBAR),
    (NexusValveMethod, 'valve_coefficient', 'kPa(kg/m3)/(kg/s)2', False, UnitSystem.METRIC),
    (NexusRelPermMethod, 'water_oil_capillary_pressure', 'PSIA', True, UnitSystem.ENGLISH),
    (NexusRelPermMethod, 'interfacial_tension_threshold_for_relperm_adjustment', 'dynes/cm', False, UnitSystem.METRIC),
    (NexusRockMethod, 'rock_compressibility', 'PSI-1', True, UnitSystem.ENGLISH),
    (NexusRockMethod, 'reference_pressure', 'bars', False, UnitSystem.METBAR),
    (NexusSeparatorMethod, 'temperature', 'DEGREES F', True, UnitSystem.ENGLISH),
    (NexusSeparatorMethod, 'pressure', 'bars', False, UnitSystem.METBAR),
    (NexusWaterMethod, 'water_compressibility', 'PSI-1', True, UnitSystem.ENGLISH),
    (NexusWaterMethod, 'reference_pressure', 'kPa', False, UnitSystem.METRIC),
    (NexusWaterMethod, 'water_density', 'kg/m3', False, UnitSystem.METBAR),
])
def test_get_unit_for_dynamic_property_attribute(data_object, attribute, expected_result, upper, unitsystem):
    """A test to check if DynamicProperty.get_unit_for_attribute method works as expected."""
    # Arrange
    prop_file = NexusFile(location='test/file/prop.dat')
    dataobj = data_object(file=prop_file, input_number=1, model_unit_system=unitsystem)
    # Act
    result = dataobj.units.get_unit_for_attribute(attribute_name=attribute, uppercase=upper)
    # Assert
    assert result == expected_result


@pytest.mark.parametrize('data_object, keyword, expected_result, upper, unitsystem', [
    (NexusPVTMethod, 'API', '', True, UnitSystem.ENGLISH),
    (NexusPVTMethod, 'BO', 'M3/STM3', True, UnitSystem.METBAR),
    (NexusPVTMethod, 'GOR', 'stcc/stcc', False, UnitSystem.LAB),
    (NexusAquiferMethod, 'BAQ', 'RB/PSIA', True, UnitSystem.ENGLISH),
    (NexusAquiferMethod, 'RO', 'M', True, UnitSystem.METBAR),
    (NexusAquiferMethod, 'VISC', 'cp', False, UnitSystem.LAB),
    (NexusEquilMethod, 'PINIT', 'PSIA', True, UnitSystem.ENGLISH),
    (NexusEquilMethod, 'GOC', 'M', True, UnitSystem.METBAR),
    (NexusEquilMethod, 'TINIT', 'degrees C', False, UnitSystem.LAB),
    (NexusGasliftMethod, 'QOIL', 'STB/DAY', True, UnitSystem.ENGLISH),
    (NexusGasliftMethod, 'PRESSURE', 'BARS', True, UnitSystem.METBAR),
    (NexusGasliftMethod, 'GOR', 'stcc/stcc', False, UnitSystem.LAB),
    (NexusHydraulicsMethod, 'LENGTH', 'FT', True, UnitSystem.ENGLISH),
    (NexusHydraulicsMethod, 'MMW', '', True, UnitSystem.METBAR),
    (NexusHydraulicsMethod, 'DATUM', 'cm', False, UnitSystem.LAB),
    (NexusValveMethod, 'VC', 'PSI(LB/FT3)/(LB/S)2', True, UnitSystem.ENGLISH),
    (NexusRelPermMethod, 'PCGO', 'PSIA', True, UnitSystem.ENGLISH),
    (NexusRelPermMethod, 'TENI', 'DYNES/CM', True, UnitSystem.METBAR),
    (NexusRockMethod, 'PREF', 'PSIA', True, UnitSystem.ENGLISH),
    (NexusRockMethod, 'CR', '(BARS)-1', True, UnitSystem.METBAR),
    (NexusSeparatorMethod, 'TEMP', 'DEGREES F', True, UnitSystem.ENGLISH),
    (NexusSeparatorMethod, 'PRES', 'BARS', True, UnitSystem.METBAR),
    (NexusWaterMethod, 'DENW', 'LB/FT3', True, UnitSystem.ENGLISH),
    (NexusWaterMethod, 'BW', 'M3/STM3', True, UnitSystem.METBAR),
    (NexusWaterMethod, 'VISW', 'cp', False, UnitSystem.LAB),
])
def test_get_unit_for_dynamic_property_keyword(data_object, keyword, expected_result, upper, unitsystem):
    """A test to check if DynamicProperty.get_unit_for_keyword method works as expected."""
    # Arrange
    prop_file = NexusFile(location='test/file/prop.dat')
    dataobj = data_object(file=prop_file, input_number=1, model_unit_system=unitsystem)
    # Act
    result = dataobj.units.get_unit_for_keyword(keyword=keyword, keyword_mapping=dataobj.get_keyword_mapping(),
                                                uppercase=upper)
    # Assert
    assert result == expected_result


def test_object_attribute_property_pvt():
    # Arrange
    prop_file = NexusFile(location='test/file/prop.dat')
    test_object = NexusPVTMethod(file=prop_file, input_number=1, properties={'UNIT_SYSTEM': UnitSystem.ENGLISH},
                                 model_unit_system=UnitSystem.METRIC)
    units = test_object.units
    # Act
    result_expected = [(units.pressure, 'psia'),
                       (units.temperature, 'degrees F'),
                       (units.delta_pressure, 'psi'),
                       (units.oil_density, 'lb/ft3'),
                       (units.gas_density, 'lb/ft3'),
                       (units.oil_api_gravity, ''),
                       (units.gas_specific_gravity, ''),
                       (units.molecular_weight_of_residual_oil, ''),
                       (units.oil_viscosity, 'cp'),
                       (units.gas_viscosity, 'cp'),
                       (units.oil_formation_volume_factor, 'rb/stb'),
                       (units.gas_formation_volume_factor, 'rb/mscf'),
                       (units.solution_gas_oil_ratio, 'mscf/stb'),
                       (units.solution_oil_gas_ratio, 'stb/mscf'),
                       (units.saturation_pressure, 'psia'),
                       (units.gas_oil_ratio, 'mscf/stb'),
                       (units.oil_gas_ratio, 'stb/mscf'),
                       (units.gas_heat_capacity_at_constant_volume, 'BTU/(lb*F)'),
                       (units.gas_heat_capacity_at_constant_pressure, 'BTU/(lb*F)'),
                       (units.oil_fvf_over_oil_fvf_at_saturation_pressure, ''),
                       (units.oil_viscosity_over_oil_viscosity_at_saturation_pressure, ''),
                       (units.gas_fvf_over_gas_fvf_at_saturation_pressure, ''),
                       (units.gas_viscosity_over_gas_viscosity_at_saturation_pressure, ''),
                       (units.gas_heat_capacity_at_constant_volume_over_cv_at_saturation_pressure, ''),
                       (units.gas_heat_capacity_at_constant_pressure_over_cp_at_saturation_pressure, ''),
                       (units.critical_pressure, 'psia'),
                       (units.critical_temperature, 'degrees F'),
                       (units.critical_volume, 'ft3/lbmole'),
                       ]
    # Assert
    for result, expected in result_expected:
        assert result == expected


def test_object_attribute_property_aquifer():
    # Arrange
    prop_file = NexusFile(location='test/file/prop.dat')
    test_object = NexusAquiferMethod(file=prop_file, input_number=1, properties={'UNIT_SYSTEM': UnitSystem.ENGLISH},
                                     model_unit_system=UnitSystem.METRIC)
    units = test_object.units
    # Act
    result_expected = [(units.carter_tracy_constant, 'rb/psia'),
                       (units.total_compressibility, 'psi-1'),
                       (units.porosity, ''),
                       (units.thickness, 'ft'),
                       (units.radius_to_inner_perimeter, 'ft'),
                       (units.radius_to_exterior_perimeter, 'ft'),
                       (units.fraction_of_circular_boundary, ''),
                       (units.linear_aquifer_width, 'ft'),
                       (units.linear_aquifer_length, 'ft'),
                       (units.time_conversion_factor, '1/days'),
                       (units.viscosity, 'cp'),
                       (units.permeability, 'md'),
                       (units.initial_aquifer_pressure, 'psia'),
                       (units.datum_depth, 'ft'),
                       (units.productivity_index, 'rb/day/psi'),
                       (units.initial_encroachable_water_volume, 'rb'),
                       (units.initial_aquifer_volume, 'rb'),
                       ]
    # Assert
    for result, expected in result_expected:
        assert result == expected


def test_object_attribute_property_equil():
    # Arrange
    prop_file = NexusFile(location='test/file/prop.dat')
    test_object = NexusEquilMethod(file=prop_file, input_number=1, properties={'UNIT_SYSTEM': UnitSystem.ENGLISH},
                                   model_unit_system=UnitSystem.METRIC)
    units = test_object.units
    # Act
    result_expected = [(units.initial_pressure, 'psia'),
                       (units.datum_depth, 'ft'),
                       (units.depth, 'ft'),
                       (units.x, 'ft'),
                       (units.y, 'ft'),
                       (units.temperature, 'degrees F'),
                       (units.initial_temperature, 'degrees F'),
                       (units.gas_oil_contact_depth, 'ft'),
                       (units.water_oil_contact_depth, 'ft'),
                       (units.gas_water_contact_depth, 'ft'),
                       (units.gas_oil_capillary_pressure_at_gas_oil_contact, 'psia'),
                       (units.water_oil_capillary_pressure_at_water_oil_contact, 'psia'),
                       (units.gas_water_capillary_pressure_at_gas_water_contact, 'psia'),
                       (units.saturation_pressure, 'psia'),
                       (units.oil_api_gravity, ''),
                       ]
    # Assert
    for result, expected in result_expected:
        assert result == expected


def test_object_attribute_property_gaslift():
    # Arrange
    prop_file = NexusFile(location='test/file/prop.dat')
    test_object = NexusGasliftMethod(file=prop_file, input_number=1, properties={'UNIT_SYSTEM': UnitSystem.ENGLISH},
                                     model_unit_system=UnitSystem.METRIC)
    units = test_object.units
    # Act
    result_expected = [(units.surface_oil_rate, 'stb/day'),
                       (units.surface_liquid_rate, 'stb/day'),
                       (units.pressure, 'psia'),
                       (units.watercut, ''),
                       (units.gas_liquid_ratio, 'mscf/stb'),
                       (units.gas_oil_ratio, 'mscf/stb'),
                       ]
    # Assert
    for result, expected in result_expected:
        assert result == expected


def test_object_attribute_property_valve():
    # Arrange
    prop_file = NexusFile(location='test/file/prop.dat')
    test_object = NexusValveMethod(file=prop_file, input_number=1, properties={'UNIT_SYSTEM': UnitSystem.ENGLISH},
                                   model_unit_system=UnitSystem.METRIC)
    units = test_object.units
    # Act
    result_expected = [(units.valve_coefficient, 'psi(lb/ft3)/(lb/s)2'),
                       ]
    # Assert
    for result, expected in result_expected:
        assert result == expected


def test_object_attribute_property_hydraulics():
    # Arrange
    prop_file = NexusFile(location='test/file/prop.dat')
    test_object = NexusHydraulicsMethod(file=prop_file, input_number=1, properties={'UNIT_SYSTEM': UnitSystem.ENGLISH},
                                        model_unit_system=UnitSystem.METRIC)
    units = test_object.units
    # Act
    result_expected = [(units.surface_oil_rate, 'stb/day'),
                       (units.surface_liquid_rate, 'stb/day'),
                       (units.surface_water_rate, 'stb/day'),
                       (units.surface_gas_rate, 'mscf/day'),
                       (units.surface_wet_gas_rate, 'mscf/day'),
                       (units.mean_molecular_weight, ''),
                       (units.watercut, ''),
                       (units.oilcut, ''),
                       (units.inlet_pressure, 'psia'),
                       (units.outlet_pressure, 'psia'),
                       (units.bottomhole_pressure, 'psia'),
                       (units.tubinghead_pressure, 'psia'),
                       (units.gas_liquid_ratio, 'mscf/stb'),
                       (units.gas_oil_ratio, 'mscf/stb'),
                       (units.oil_gas_ratio, 'stb/mscf'),
                       (units.water_gas_ratio, 'stb/mscf'),
                       (units.gas_water_ratio, 'mscf/stb'),
                       (units.water_wet_gas_ratio, 'stb/mscf'),
                       (units.length, 'ft'),
                       (units.datum_depth, 'ft'),
                       (units.depth_change, 'ft'),
                       (units.hydraulic_table_vertical_distance, 'ft'),
                       (units.injected_fluid_pressure_gradient, 'psi/ft'),
                       (units.viscosity, 'cp'),
                       (units.diameter, 'in'),
                       (units.roughness, 'in'),
                       ]
    # Assert
    for result, expected in result_expected:
        assert result == expected

    # === Test VIP-compatible form of ratio units
    test_object = NexusHydraulicsMethod(file=prop_file, input_number=1,
                                        model_unit_system=UnitSystem.ENGLISH,
                                        ratio_thousands=False
                                        )
    units = test_object.units
    # Act
    result_expected = [(units.surface_oil_rate, 'stb/day'),
                       (units.surface_liquid_rate, 'stb/day'),
                       (units.surface_water_rate, 'stb/day'),
                       (units.surface_gas_rate, 'mscf/day'),
                       (units.surface_wet_gas_rate, 'mscf/day'),
                       (units.mean_molecular_weight, ''),
                       (units.watercut, ''),
                       (units.oilcut, ''),
                       (units.inlet_pressure, 'psia'),
                       (units.outlet_pressure, 'psia'),
                       (units.bottomhole_pressure, 'psia'),
                       (units.tubinghead_pressure, 'psia'),
                       (units.gas_liquid_ratio, 'scf/stb'),
                       (units.gas_oil_ratio, 'scf/stb'),
                       (units.oil_gas_ratio, 'stb/mmscf'),
                       (units.water_gas_ratio, 'stb/mmscf'),
                       (units.gas_water_ratio, 'scf/stb'),
                       (units.water_wet_gas_ratio, 'stb/mmscf'),
                       (units.length, 'ft'),
                       (units.datum_depth, 'ft'),
                       (units.depth_change, 'ft'),
                       (units.hydraulic_table_vertical_distance, 'ft'),
                       (units.injected_fluid_pressure_gradient, 'psi/ft'),
                       (units.viscosity, 'cp'),
                       (units.diameter, 'in'),
                       (units.roughness, 'in'),
                       ]
    # Assert
    for result, expected in result_expected:
        assert result == expected


def test_object_attribute_property_relperm():
    # Arrange
    prop_file = NexusFile(location='test/file/prop.dat')
    test_object = NexusRelPermMethod(file=prop_file, input_number=1, properties={'UNIT_SYSTEM': UnitSystem.ENGLISH},
                                     model_unit_system=UnitSystem.METRIC)
    units = test_object.units
    # Act
    result_expected = [(units.water_oil_capillary_pressure, 'psia'),
                       (units.gas_oil_capillary_pressure, 'psia'),
                       (units.gas_water_capillary_pressure, 'psia'),
                       (units.interfacial_tension_threshold_for_relperm_adjustment, 'dynes/cm'),
                       (units.reference_interfacial_tension_for_capillary_pressure_adjustment, 'dynes/cm'),
                       ]
    # Assert
    for result, expected in result_expected:
        assert result == expected


def test_object_attribute_property_rock():
    # Arrange
    prop_file = NexusFile(location='test/file/prop.dat')
    test_object = NexusRockMethod(file=prop_file, input_number=1, properties={'UNIT_SYSTEM': UnitSystem.ENGLISH},
                                  model_unit_system=UnitSystem.METRIC)
    units = test_object.units
    # Act
    result_expected = [(units.pressure, 'psia'),
                       (units.rock_compressibility, 'psi-1'),
                       (units.delta_pressure, 'psi'),
                       (units.rock_permeability_compressibility, 'psi-1'),
                       (units.reference_pressure, 'psia'),
                       ]
    # Assert
    for result, expected in result_expected:
        assert result == expected


def test_object_attribute_property_separator():
    # Arrange
    prop_file = NexusFile(location='test/file/prop.dat')
    test_object = NexusSeparatorMethod(file=prop_file, input_number=1, properties={'UNIT_SYSTEM': UnitSystem.ENGLISH},
                                       model_unit_system=UnitSystem.METRIC)
    units = test_object.units
    # Act
    result_expected = [(units.pressure, 'psia'),
                       (units.temperature, 'degrees F'),
                       (units.standard_temperature, 'degrees F'),
                       (units.standard_pressure, 'psia'),
                       ]
    # Assert
    for result, expected in result_expected:
        assert result == expected


def test_object_attribute_property_water():
    # Arrange
    prop_file = NexusFile(location='test/file/prop.dat')
    test_object = NexusWaterMethod(file=prop_file, input_number=1, properties={'UNIT_SYSTEM': UnitSystem.ENGLISH},
                                   model_unit_system=UnitSystem.METRIC)
    units = test_object.units
    # Act
    result_expected = [(units.reference_pressure, 'psia'),
                       (units.temperature, 'degrees F'),
                       (units.water_density, 'lb/ft3'),
                       (units.water_compressibility, 'psi-1'),
                       (units.water_formation_volume_factor, 'rb/stb'),
                       (units.water_viscosity, 'cp'),
                       (units.water_viscosity_compressibility, 'psi-1'),
                       ]
    # Assert
    for result, expected in result_expected:
        assert result == expected
