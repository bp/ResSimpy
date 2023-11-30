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


def test_print_simulator_information(mocker: MockerFixture):
    # Arrange
    in_file_contents = """
    ! Initial comment describing the model
    SIMULATION
      SIMULATION_TYPE SUBSURFACE           
    END

TIME
  START_DATE 1 DEC 2023
  FINAL_DATE 1 JAN 2126
END    

WELL_DATA test_well_1
    WELL_TYPE GAS_INJECTOR
    CIJK_D	1 2     3 3
    DATE 1 OCT 2025
    CIJK_D	8    222     76  76
END

    """

    open_mock = mocker.mock_open(read_data=in_file_contents)
    mocker.patch("builtins.open", open_mock)

    expected_model_string = \
"""Simulation Type SUBSURFACE
Start Date: 1 DEC 2023
End Date: 1 JAN 2126

WELLS
-----

Well Name: test_well_1
Well Type: GAS_INJECTOR
Completions:
i: 1 j: 2 k: 3 | Opened on 1 DEC 2023
i: 8 j: 222 k: 76 | Opened on 1 OCT 2025

Dates well is Changed: 1 DEC 2023, 1 OCT 2025

"""

    # Act
    model = OpenGoSimSimulator(origin='/my/test/path')
    result = model.__repr__()

    # Assert
    assert result == expected_model_string