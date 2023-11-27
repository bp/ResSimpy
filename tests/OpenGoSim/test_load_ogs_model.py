import pytest
from pytest_mock import MockerFixture

from ResSimpy.OpenGoSim.Enums.SimulationTypeEnum import SimulationType
from ResSimpy.OpenGoSim.OpenGoSimSimulator import OpenGoSimSimulator


def test_load_simulation_type(mocker: MockerFixture):
    # Arrange
    in_file_contents = """
! Initial comment describing the model
SIMULATION
  SIMULATION_TYPE SUBSURFACE
  PROCESS_MODELS
    SUBSURFACE_FLOW Flow
      MODE GAS_WATER
      OPTIONS
        ! ISOTHERMAL
        RESERVOIR_DEFAULTS
        HYSTERESIS
        STRAND
      	LDT
      /
    / ! end of subsurface_flow
  / ! end of process models
END  !! end simulation block
"""

    open_mock = mocker.mock_open(read_data=in_file_contents)
    mocker.patch("builtins.open", open_mock)

    # Act
    model = OpenGoSimSimulator(origin='/my/test/path')

    # Assert
    assert model.simulation_type == SimulationType.SUBSURFACE

@pytest.mark.skip("Not implemented yet")
def test_load_other_simulation_properties(mocker: MockerFixture):
    # Arrange
    in_file_contents = """
! Initial comment describing the model
SIMULATION
  SIMULATION_TYPE SUBSURFACE
  PROCESS_MODELS
    SUBSURFACE_FLOW Flow
      MODE GAS_WATER
      OPTIONS
        ! ISOTHERMAL
        RESERVOIR_DEFAULTS
        HYSTERESIS
        STRAND
      	LDT
      /
    / ! end of subsurface_flow
  / ! end of process models
END  !! end simulation block
"""

    open_mock = mocker.mock_open(read_data=in_file_contents)
    mocker.patch("builtins.open", open_mock)

    # Act
    model = OpenGoSimSimulator(origin='/my/test/path')

    # Assert
    assert model.simulation_type == SimulationType.SUBSURFACE
    # assert model.mode ==

def test_load_time_information(mocker: MockerFixture):
    # Arrange
    in_file_contents = """
    ! Initial comment describing the model
    SIMULATION
      SIMULATION_TYPE SUBSURFACE
      PROCESS_MODELS
        SUBSURFACE_FLOW Flow
          MODE GAS_WATER
          OPTIONS
            ! ISOTHERMAL
            RESERVOIR_DEFAULTS
            HYSTERESIS
            STRAND
          	LDT
          /
        /
      /
    END
    
TIME
  START_DATE 1 DEC 2023
  FINAL_DATE 1 JAN 2126  ! Test Comment
  INITIAL_TIMESTEP_SIZE 0.1 d
  MAXIMUM_TIMESTEP_SIZE 10 d at 0 d
  MAXIMUM_TIMESTEP_SIZE 50 d at 1 y
  MAXIMUM_TIMESTEP_SIZE 365 d at 25 y
END    
    
    """

    open_mock = mocker.mock_open(read_data=in_file_contents)
    mocker.patch("builtins.open", open_mock)

    # Act
    model = OpenGoSimSimulator(origin='/my/test/path')

    # Assert
    assert model.simulation_type == SimulationType.SUBSURFACE
    assert model.start_date == '1 DEC 2023'
    assert model.final_date == '1 JAN 2126'