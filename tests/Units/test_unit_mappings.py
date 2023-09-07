import pytest

from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.DataModels.Network.NexusConstraint import NexusConstraint
from ResSimpy.Nexus.DataModels.Network.NexusNode import NexusNode
from ResSimpy.Nexus.DataModels.Network.NexusNodeConnection import NexusNodeConnection
from ResSimpy.Units.Units import Area
from ResSimpy.Units.AttributeMapping import ConstraintUnits


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
    unit_dimension = ConstraintUnits()

    # Act
    result = unit_dimension.get_unit_from_attribute(unit_system=unit_system, attribute_name=attribute)
    # Assert
    assert result == expected_result


def test_get_unit_error():
    """Tests the get_unit method."""
    # Arrange
    unit_dimension = ConstraintUnits()

    # Act
    with pytest.raises(AttributeError):
        unit_dimension.get_unit_from_attribute(unit_system=UnitSystem.ENGLISH, attribute_name='not_an_attribute')


@pytest.mark.parametrize('data_object, attribute, expected_result', [
    (NexusConstraint, 'max_surface_water_rate', 'STB/day'),
    (NexusNode, 'depth', 'ft'),
    (NexusNodeConnection, 'diameter', 'in'),
])
def test_get_unit_for_attribute(data_object, attribute, expected_result):
    """Write a test to check that the DataObjectMixin.get_unit_for_attribute method works as expected."""
    # Arrange
    constraint = data_object({})
    # Act
    result = constraint.get_unit_for_attribute(attribute_name=attribute, unit_system=UnitSystem.ENGLISH)
    # Assert
    assert result == expected_result