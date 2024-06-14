from ResSimpy.Nexus.DataModels.Network.NexusWellConnection import NexusWellConnection
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.OperationsMixin import NetworkOperationsMixIn


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

    # Assert
    assert result == expected_result
