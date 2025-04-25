import pytest

from ResSimpy.Nexus.DataModels.Network.NexusConstraint import NexusConstraint
from ResSimpy.Nexus.DataModels.Network.NexusNode import NexusNode
from ResSimpy.Nexus.DataModels.Network.NexusWellConnection import NexusWellConnection
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.DataModelBaseClasses.OperationsMixin import NetworkOperationsMixIn
from tests.multifile_mocker import mock_multiple_files
from tests.utility_for_tests import get_fake_nexus_simulator


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
        NexusWellConnection(dict(name='well1', polymer='polymer', bhdepth=1000.2, datum_depth=100.3, ),
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
                        max_surface_gas_rate=12.3, max_surface_liquid_rate=123.4, ),
        NexusConstraint(max_reservoir_oil_rate=120, name='well1', date='01/03/2020', date_format=DateFormat.DD_MM_YYYY,
                        max_surface_gas_rate=12.3, max_surface_liquid_rate=123.4, ),
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


def test_apply_clears_from_read(mocker):
    # Arrange 
    file_contents = """
        CONSTRAINTS
           well1	 QGSMAX 	1234.0 PMAX 3000
           well2 QLIQSMAX 	5678.0 PMIN 1200
           ENDCONSTRAINTS

        TIME 05/04/2025
        CONSTRAINTS
           well1  CLEARQ QOSMAX 100
           well2 QLIQSMAX 	20.02
           ENDCONSTRAINTS

           """
    fcs_contents = """RECURRENT_FILES 
            SURFACE Network 1 data/surface.dat"""
    mocker.patch('ResSimpy.DataModelBaseClasses.DataObjectMixin.uuid4', return_value='uuid_1')

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            'fcs_file.fcs': fcs_contents,
            'data/surface.dat': file_contents,
        }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    model = get_fake_nexus_simulator(mocker=mocker, fcs_file_path='fcs_file.fcs', mock_open=False,
                                     )
    model._start_date = '02/04/2024'
    constraints = model.network.constraints.get_all()
    resolved_constraints = {}
    # act
    for well_name, named_constraints in constraints.items():
        resolved_constraints[well_name] = (
            NetworkOperationsMixIn.resolve_same_named_objects_constraints(named_constraints))
    # assert
    assert resolved_constraints['well1'][0].max_surface_gas_rate == 1234.0
    assert resolved_constraints['well1'][0].max_pressure == 3000
    assert resolved_constraints['well1'][1].clear_q is True
    assert resolved_constraints['well1'][1].max_surface_gas_rate is None
    assert resolved_constraints['well1'][1].max_surface_oil_rate == 100

    assert resolved_constraints['well2'][0].min_pressure == 1200
    assert resolved_constraints['well2'][0].max_surface_liquid_rate == 5678.0
    assert resolved_constraints['well2'][1].max_surface_liquid_rate == 20.02
    assert resolved_constraints['well2'][1].min_pressure == 1200

@pytest.mark.parametrize('constraints_for_well, expected_result',[
    ([
        NexusConstraint(
            qmult_oil_rate=12.3, qmult_water_rate=123.4, qmult_gas_rate=5.5, name='well1', max_pressure=100,
            date='01/01/2020', date_format=DateFormat.DD_MM_YYYY, convert_qmult_to_reservoir_barrels=True),
        NexusConstraint(
            qmult_oil_rate=10.3, qmult_water_rate=24, qmult_gas_rate=0, name='well1', date='01/02/2020',
            date_format=DateFormat.DD_MM_YYYY),
        NexusConstraint(
            max_pressure=200.5, name='well1', date='01/03/2020', date_format=DateFormat.DD_MM_YYYY),
        NexusConstraint(
            max_surface_oil_rate=2.34567, name='well1', date='01/04/2020', date_format=DateFormat.DD_MM_YYYY),
    ],
                         [
        NexusConstraint(
            qmult_oil_rate=12.3, qmult_water_rate=123.4, qmult_gas_rate=5.5, name='well1', max_pressure=100,
            date='01/01/2020', date_format=DateFormat.DD_MM_YYYY, convert_qmult_to_reservoir_barrels=True
        ),
        NexusConstraint(
            qmult_oil_rate=10.3, qmult_water_rate=24, qmult_gas_rate=0, max_pressure=100,
            name='well1', date='01/02/2020', date_format=DateFormat.DD_MM_YYYY, convert_qmult_to_reservoir_barrels=True,
        ),
        NexusConstraint(
            qmult_oil_rate=10.3, qmult_water_rate=24, qmult_gas_rate=0, max_pressure=200.5,
            name='well1', date='01/03/2020', date_format=DateFormat.DD_MM_YYYY, convert_qmult_to_reservoir_barrels=True,
        ),
        NexusConstraint(
            name='well1', date='01/04/2020', date_format=DateFormat.DD_MM_YYYY,
            max_surface_oil_rate=2.34567, max_pressure=200.5,
        ),
]),
    ([
        NexusConstraint(
            qmult_oil_rate=12.3, qmult_water_rate=123.4, qmult_gas_rate=5.5, name='well1', max_pressure=100,
            date='01/01/2020', date_format=DateFormat.DD_MM_YYYY, convert_qmult_to_reservoir_barrels=True),
        NexusConstraint(
            qmult_oil_rate=10.3, qmult_water_rate=24, qmult_gas_rate=0, name='well1', date='01/02/2020',
            date_format=DateFormat.DD_MM_YYYY),
        NexusConstraint(
            max_pressure=200.5, name='well1', date='01/03/2020', date_format=DateFormat.DD_MM_YYYY, clear_q=True),
        NexusConstraint(
            max_surface_oil_rate=2.34567, name='well1', date='01/04/2020', date_format=DateFormat.DD_MM_YYYY),
    ],
                         [
        NexusConstraint(
            qmult_oil_rate=12.3, qmult_water_rate=123.4, qmult_gas_rate=5.5, name='well1', max_pressure=100,
            date='01/01/2020', date_format=DateFormat.DD_MM_YYYY, convert_qmult_to_reservoir_barrels=True
        ),
        NexusConstraint(
            qmult_oil_rate=10.3, qmult_water_rate=24, qmult_gas_rate=0, max_pressure=100,
            name='well1', date='01/02/2020', date_format=DateFormat.DD_MM_YYYY, convert_qmult_to_reservoir_barrels=True,
        ),
        NexusConstraint(
            max_pressure=200.5, name='well1', date='01/03/2020', date_format=DateFormat.DD_MM_YYYY, 
            convert_qmult_to_reservoir_barrels=None, clear_q=True,
        ),
        NexusConstraint(
            name='well1', date='01/04/2020', date_format=DateFormat.DD_MM_YYYY,
            max_surface_oil_rate=2.34567, max_pressure=200.5,
        ),
])
], ids=['overide_qmult_to_reservoir_barrels', 'with clear'])
def test_override_qallrmax(constraints_for_well, expected_result):
    # Act
    result = NetworkOperationsMixIn.resolve_same_named_objects_constraints(constraints_for_well)

    # Assert
    assert result == expected_result
