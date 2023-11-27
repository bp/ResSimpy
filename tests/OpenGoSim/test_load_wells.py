from pytest_mock import MockerFixture

from ResSimpy.Enums.PenetrationDirectionEnum import PenetrationDirectionEnum
from ResSimpy.Enums.WellTypeEnum import WellType
from ResSimpy.OpenGoSim.DataModels.OpenGoSimCompletion import OpenGoSimCompletion
from ResSimpy.OpenGoSim.DataModels.OpenGoSimWell import OpenGoSimWell
from ResSimpy.OpenGoSim.Enums.SimulationTypeEnum import SimulationType
from ResSimpy.OpenGoSim.OpenGoSimSimulator import OpenGoSimSimulator
from ResSimpy.OpenGoSim.OpenGoSimWells import OpenGoSimWells


# Initial tests assuming well information is in the base .in file for the OpenGoSim model
def test_load_basic_well(mocker: MockerFixture):
    # Arrange
    in_file_contents = """
! Initial comment describing the model
SIMULATION
    SIMULATION_TYPE SUBSURFACE
END

TIME
  START_DATE 1 DEC 2025
END

#======== Wells =========

WELL_DATA well_1
   WELL_TYPE GAS_INJECTOR
 DATE 1 JAN 2047
 CIJK_D	1 2 3   4 Z
END    
"""

    open_mock = mocker.mock_open(read_data=in_file_contents)
    mocker.patch("builtins.open", open_mock)
    expected_completion_1 = OpenGoSimCompletion(i=1, j=2, k=3, penetration_direction=PenetrationDirectionEnum.Z,
                                                date='1 JAN 2047', )
    expected_completion_2 = OpenGoSimCompletion(i=1, j=2, k=4, penetration_direction=PenetrationDirectionEnum.Z,
                                                date='1 JAN 2047')
    expected_completions = [expected_completion_1, expected_completion_2]
    expected_well_1 = OpenGoSimWell(well_type=WellType.GAS_INJECTOR, well_name='well_1', completions=expected_completions)

    expected_wells_object = OpenGoSimWells(_wells=[expected_well_1])
    expected_wells_object._wells_loaded = True

    expected_sim_object = OpenGoSimSimulator(origin='/my/test/path')
    expected_sim_object.__simulation_type = SimulationType.SUBSURFACE
    expected_sim_object._wells = expected_wells_object
    expected_sim_object._start_date = '1 DEC 2025'

    # Act
    model = OpenGoSimSimulator(origin='/my/test/path')

    # Assert
    assert model.simulation_type == SimulationType.SUBSURFACE
    assert model.wells.wells[0].well_name == 'well_1'
    assert model.wells.wells[0].well_type == WellType.GAS_INJECTOR
    assert model.wells.wells[0].completions[0] == expected_completion_1
    assert model.wells.wells[0] == expected_well_1
    assert model.wells == expected_wells_object
    assert model == expected_sim_object


# TODO: Add tests that test loading wells via include files etc