import pytest

from ResSimpy.Nexus.DataModels.Network.NexusConstraint import NexusConstraint
from ResSimpy.Nexus.DataModels.Network.NexusNode import NexusNode
from ResSimpy.Nexus.DataModels.Network.NexusWellConnection import NexusWellConnection
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.DataModelBaseClasses.OperationsMixin import NetworkOperationsMixIn


def test_resolve_carried_over_attributes():
    # Arrange
    existing_objects = [
        NexusWellConnection(dict(name='well1', polymer='polymer'),
                            date='01/01/2022', date_format=DateFormat.DD_MM_YYYY),
        NexusWellConnection(dict(name='well1', bhdepth=1000.2, datum_depth=100.3, ), 
                            date='01/01/2020', date_format=DateFormat.DD_MM_YYYY),
        NexusWellConnection(dict(name='well1', d_factor=0.0001, heat_transfer_coeff=0.2, datum_depth=10),
                            date='01/01/2021', date_format=DateFormat.DD_MM_YYYY),
    ]

    expected_result = [
        NexusWellConnection(dict(name='well1', bhdepth=1000.2, datum_depth=100.3, ),
                            date='01/01/2020', date_format=DateFormat.DD_MM_YYYY),
        NexusWellConnection(dict(name='well1', bhdepth=1000.2,
                                 d_factor=0.0001, heat_transfer_coeff=0.2, datum_depth=10),
                            date='01/01/2021', date_format=DateFormat.DD_MM_YYYY),
        NexusWellConnection(dict(name='well1', polymer='polymer', bhdepth=1000.2,
                                 d_factor=0.0001, heat_transfer_coeff=0.2, datum_depth=10),
                            date='01/01/2022', date_format=DateFormat.DD_MM_YYYY),
    ]
    
    # Act
    result = NetworkOperationsMixIn.resolve_carried_over_attributes(existing_objects)
    
    # Assert
    assert result == expected_result


def test_resolve_carried_over_attributes_multiple_names():
    # Arrange
    existing_objects = [
        NexusWellConnection(dict(name='well1', bhdepth=1000.2, datum_depth=100.3, ),
                            date='01/01/2020', date_format=DateFormat.DD_MM_YYYY),
        NexusWellConnection(dict(name='well1', d_factor=0.0001, heat_transfer_coeff=0.2, datum_depth=10),
                            date='01/01/2021', date_format=DateFormat.DD_MM_YYYY),
        NexusWellConnection(dict(name='well2', bhdepth=1000.2, datum_depth=100.3, ),
                            date='01/01/2020', date_format=DateFormat.DD_MM_YYYY),
        NexusWellConnection(dict(name='well2', d_factor=0.0001, heat_transfer_coeff=0.2, datum_depth=10),
                            date='01/01/2021', date_format=DateFormat.DD_MM_YYYY)
    ]

    expected_result = [
        NexusWellConnection(dict(name='well1', bhdepth=1000.2, datum_depth=100.3, ),
                            date='01/01/2020', date_format=DateFormat.DD_MM_YYYY),
        NexusWellConnection(dict(name='well1', bhdepth=1000.2,
                                 d_factor=0.0001, heat_transfer_coeff=0.2, datum_depth=10),
                            date='01/01/2021', date_format=DateFormat.DD_MM_YYYY),
        NexusWellConnection(dict(name='well2', bhdepth=1000.2, datum_depth=100.3, ),
                            date='01/01/2020', date_format=DateFormat.DD_MM_YYYY),
        NexusWellConnection(dict(name='well2', bhdepth=1000.2,
                                 d_factor=0.0001, heat_transfer_coeff=0.2, datum_depth=10),
                            date='01/01/2021', date_format=DateFormat.DD_MM_YYYY),
    ]

    # Act
    result = NetworkOperationsMixIn.resolve_carried_over_attributes(existing_objects)
    result.sort(key=lambda x: (x.name, x.iso_date))
    # Assert
    assert result == expected_result


def test_resolve_carried_over_fails_with_multiple_types():
    # Arrange
    existing_objects = [
        NexusWellConnection(dict(name='well1', bhdepth=1000.2, datum_depth=100.3, ),
                            date='01/01/2020', date_format=DateFormat.DD_MM_YYYY),
        NexusNode(dict(name='well1', type='WELLHEAD', station='station1'), date='01/01/2021', 
                  date_format=DateFormat.DD_MM_YYYY)
        ]

    # Act and Assert
    with pytest.raises(ValueError) as e_info:
        NetworkOperationsMixIn.resolve_carried_over_attributes(existing_objects)
    assert str(e_info.value) == 'Objects to resolve must be of the same type.'


def test_resolve_carried_over_attributes_same_date():
    # Arrange
    existing_objects = [
        NexusWellConnection(dict(name='well1', polymer='polymer'),
                            date='01/01/2020', date_format=DateFormat.DD_MM_YYYY),
        NexusWellConnection(dict(name='well1', bhdepth=1000.2, datum_depth=100.3, ),
                            date='01/01/2020', date_format=DateFormat.DD_MM_YYYY),
        NexusWellConnection(dict(name='well1', d_factor=0.0001, heat_transfer_coeff=0.2, datum_depth=10),
                            date='01/01/2020', date_format=DateFormat.DD_MM_YYYY),
    ]

    expected_result = [
        NexusWellConnection(dict(name='well1', polymer='polymer'),
                            date='01/01/2020', date_format=DateFormat.DD_MM_YYYY),
        NexusWellConnection(dict(name='well1', polymer='polymer', bhdepth=1000.2, datum_depth=100.3,),
                            date='01/01/2020', date_format=DateFormat.DD_MM_YYYY),
        NexusWellConnection(dict(name='well1', polymer='polymer', bhdepth=1000.2,
                                 d_factor=0.0001, heat_transfer_coeff=0.2, datum_depth=10),
                            date='01/01/2020', date_format=DateFormat.DD_MM_YYYY),
    ]

    # Act
    result = NetworkOperationsMixIn.resolve_carried_over_attributes(existing_objects)

    # Assert
    assert result == expected_result


def test_apply_clears():
    # Arrange
    constraints_for_well = [
        NexusConstraint(max_surface_gas_rate=12.3, max_surface_liquid_rate=123.4, name='well1', max_pressure=100,
                        date='01/01/2020', date_format=DateFormat.DD_MM_YYYY),
        NexusConstraint(clear_q=True, name='well1', date='01/02/2020', date_format=DateFormat.DD_MM_YYYY),
        NexusConstraint(max_reservoir_oil_rate=120, name='well1', date='01/03/2020', date_format=DateFormat.DD_MM_YYYY),
    ]
    
    expected_result = [
        NexusConstraint(max_surface_gas_rate=12.3, max_surface_liquid_rate=123.4, name='well1', max_pressure=100,
                        date='01/01/2020', date_format=DateFormat.DD_MM_YYYY),
        NexusConstraint(clear_q=True, name='well1', date='01/02/2020', date_format=DateFormat.DD_MM_YYYY,
                        max_pressure=100),
        NexusConstraint(max_reservoir_oil_rate=120, name='well1', date='01/03/2020', date_format=DateFormat.DD_MM_YYYY,
                        max_pressure=100),
    ]
    
    # Act
    result = NetworkOperationsMixIn.resolve_same_named_objects_constraints(constraints_for_well)
    
    # Assert
    assert result == expected_result


def test_apply_clear_all():
    # Arrange
    constraints_for_well = [
        NexusConstraint(max_surface_gas_rate=12.3, max_surface_liquid_rate=123.4, name='well1', max_pressure=100,
                        date='01/01/2020', date_format=DateFormat.DD_MM_YYYY),
        NexusConstraint(clear_all=True, name='well1', date='01/02/2020', date_format=DateFormat.DD_MM_YYYY),
        NexusConstraint(max_reservoir_oil_rate=122, name='well1', date='01/03/2020', date_format=DateFormat.DD_MM_YYYY),
        NexusConstraint(max_surface_gas_rate=120, name='well1', date='01/04/2020', date_format=DateFormat.DD_MM_YYYY)
    ]

    expected_result = [
        NexusConstraint(max_surface_gas_rate=12.3, max_surface_liquid_rate=123.4, name='well1', max_pressure=100,
                        date='01/01/2020', date_format=DateFormat.DD_MM_YYYY),
        NexusConstraint(clear_all=True, name='well1', date='01/02/2020', date_format=DateFormat.DD_MM_YYYY),
        NexusConstraint(max_reservoir_oil_rate=122, name='well1', date='01/03/2020', date_format=DateFormat.DD_MM_YYYY,
                        ),
        NexusConstraint(max_reservoir_oil_rate=122, max_surface_gas_rate=120, name='well1', date='01/04/2020', 
                        date_format=DateFormat.DD_MM_YYYY)

    ]

    # Act
    result = NetworkOperationsMixIn.resolve_same_named_objects_constraints(constraints_for_well)

    # Assert
    assert result == expected_result

def test_apply_clear_p():
    # Arrange
    constraints_for_well = [
        NexusConstraint(max_surface_gas_rate=12.3, max_surface_liquid_rate=123.4, name='well1', max_pressure=100,
                        date='01/01/2020', date_format=DateFormat.DD_MM_YYYY),
        NexusConstraint(clear_p=True, name='well1', date='01/02/2020', date_format=DateFormat.DD_MM_YYYY),
        NexusConstraint(max_reservoir_oil_rate=120, name='well1', date='01/03/2020', date_format=DateFormat.DD_MM_YYYY),
    ]

    expected_result = [
        NexusConstraint(max_surface_gas_rate=12.3, max_surface_liquid_rate=123.4, name='well1', max_pressure=100,
                        date='01/01/2020', date_format=DateFormat.DD_MM_YYYY),
        NexusConstraint(clear_p=True, name='well1', date='01/02/2020', date_format=DateFormat.DD_MM_YYYY,
                        max_surface_gas_rate=12.3, max_surface_liquid_rate=123.4,),
        NexusConstraint(max_reservoir_oil_rate=120, name='well1', date='01/03/2020', date_format=DateFormat.DD_MM_YYYY,
                        max_surface_gas_rate=12.3, max_surface_liquid_rate=123.4,),
    ]

    # Act
    result = NetworkOperationsMixIn.resolve_same_named_objects_constraints(constraints_for_well)

    # Assert
    assert result == expected_result

def test_apply_clear_limits():
    # Arrange
    constraints_for_well = [
        NexusConstraint(max_surface_gas_rate=12.3, max_surface_liquid_rate=123.4, name='well1', max_pressure=100,
                        date='01/01/2020', date_format=DateFormat.DD_MM_YYYY, max_wor=0.59),
        NexusConstraint(clear_limit=True, name='well1', date='01/02/2020', date_format=DateFormat.DD_MM_YYYY),
        NexusConstraint(max_reservoir_oil_rate=120, name='well1', date='01/03/2020', date_format=DateFormat.DD_MM_YYYY),
    ]

    expected_result = [
        NexusConstraint(max_surface_gas_rate=12.3, max_surface_liquid_rate=123.4, name='well1', max_pressure=100,
                        date='01/01/2020', date_format=DateFormat.DD_MM_YYYY, max_wor=0.59),
        NexusConstraint(clear_limit=True, name='well1', date='01/02/2020', date_format=DateFormat.DD_MM_YYYY,
                        max_surface_gas_rate=12.3, max_surface_liquid_rate=123.4, max_pressure=100),
        NexusConstraint(max_reservoir_oil_rate=120, name='well1', date='01/03/2020', date_format=DateFormat.DD_MM_YYYY,
                        max_surface_gas_rate=12.3, max_surface_liquid_rate=123.4, max_pressure=100),
    ]

    # Act
    result = NetworkOperationsMixIn.resolve_same_named_objects_constraints(constraints_for_well)

    # Assert
    assert result == expected_result

def test_apply_clear_alq():
    # Arrange
    constraints_for_well = [
        NexusConstraint(max_surface_gas_rate=12.3, max_surface_liquid_rate=123.4, name='well1', max_pressure=100,
                        date='01/01/2020', date_format=DateFormat.DD_MM_YYYY, pump_power=6500),
        NexusConstraint(clear_alq=True, name='well1', date='01/02/2020', date_format=DateFormat.DD_MM_YYYY),
        NexusConstraint(max_reservoir_oil_rate=120, name='well1', date='01/03/2020', date_format=DateFormat.DD_MM_YYYY),
    ]

    expected_result = [
        NexusConstraint(max_surface_gas_rate=12.3, max_surface_liquid_rate=123.4, name='well1', max_pressure=100,
                        date='01/01/2020', date_format=DateFormat.DD_MM_YYYY, pump_power=6500),
        NexusConstraint(clear_alq=True, name='well1', date='01/02/2020', date_format=DateFormat.DD_MM_YYYY,
                        max_surface_gas_rate=12.3, max_surface_liquid_rate=123.4, max_pressure=100),
        NexusConstraint(max_reservoir_oil_rate=120, name='well1', date='01/03/2020', date_format=DateFormat.DD_MM_YYYY,
                        max_surface_gas_rate=12.3, max_surface_liquid_rate=123.4, max_pressure=100),
    ]

    # Act
    result = NetworkOperationsMixIn.resolve_same_named_objects_constraints(constraints_for_well)

    # Assert
    assert result == expected_result
