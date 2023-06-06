import datetime

from ResSimpy.Nexus.DataModels.NexusCompletion import NexusCompletion



def test_usa_date_format():
    # Arrange
    completion = NexusCompletion(date='01/14/2022')
    expected_iso_date_str = '2022-01-14T00:00:00'
    expected_iso_date = datetime.datetime(2022, 1, 14, 0, 0, 0)

    # Act
    result_date = completion.date_ISO
    
    # Assert
    assert result_date ==  expected_iso_date
    assert str(result_date) == expected_iso_date_str
    
