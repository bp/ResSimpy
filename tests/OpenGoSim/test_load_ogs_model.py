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
