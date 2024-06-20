from ResSimpy.Nexus.DataModels.Network.NexusWellConnection import NexusWellConnection
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.Units.convert_units import convert_object_units
from ResSimpy.Enums.UnitsEnum import UnitSystem


def test_unit_object_conversion(mocker):
    # Arrange

    test_obj = NexusWellConnection(
        properties_dict=dict(diameter=100.1),
        unit_system=UnitSystem.ENGLISH, date='01/01/2020', date_format=DateFormat.DD_MM_YYYY
    )

    to_unit = UnitSystem.METBAR

    # Act
    result = convert_object_units(test_obj, to_unit)

    # Assert
    assert result.diameter == 100.1 * 2.54
    assert result.units.unit_system == to_unit
