from unittest.mock import MagicMock

import pytest

from ResSimpy import NexusSimulator
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.DataModels.Network.NexusConstraint import NexusConstraint
from ResSimpy.Nexus.DataModels.Network.NexusConstraints import NexusConstraints
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat


class TestWriteNetwork:
    start_date = '01/01/2019'
    constraint_1 = NexusConstraint(dict(name='well1', max_surface_oil_rate=100.2, max_surface_water_rate=3.14),
                                   date='01/01/2020', date_format=DateFormat.DD_MM_YYYY,
                                   unit_system=UnitSystem.ENGLISH, start_date=start_date)
    constraint_2 = NexusConstraint(dict(name='well1', max_surface_oil_rate=200, max_surface_water_rate=100),
                                   date='01/01/2021', date_format=DateFormat.DD_MM_YYYY,
                                   unit_system=UnitSystem.ENGLISH, start_date=start_date)
    existing_constraints = {'well1': [constraint_1, constraint_2]}

    # mock out simulator and parent network
    parent_network = MagicMock()
    mock_model = MagicMock()

    constraints = NexusConstraints(parent_network, mock_model)

    constraints._constraints = existing_constraints
    
    def test_write_out_constraints_for_date(self):
        # Arrange
        expected_result = '''CONSTRAINTS
well1 QOSMAX 200 QWSMAX 100
ENDCONSTRAINTS

'''
        # Act
        result = self.constraints.write_out_constraints_for_date(date='01/01/2021')
        
        # Assert
        assert result == expected_result
    
    def test_write_out_constraints_for_multiple_wells(self):