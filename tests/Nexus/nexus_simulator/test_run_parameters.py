import pytest

from ResSimpy.Enums.TimeSteppingMethodEnum import TimeSteppingMethod
from ResSimpy.Nexus.DataModels.NexusSolverParameter import NexusSolverParameter
from ResSimpy.Nexus.NexusSolverParameters import NexusSolverParameters
from tests.utility_for_tests import get_fake_nexus_simulator

class TestNexusSolverParameters:
    start_date = '01/01/2020'

    @pytest.mark.parametrize('file_content, expected_result',
                             [
                                 # basic_test
                                 ('''START 01/01/2020
                                 !     Timestep controls
                                 DT AUTO 0.1
                                    MIN 0.001
                                    MAX 60.
                                    MAXINCREASE 8.
                                    !     Timestepping method
                                    METHOD IMPLICIT
                                    ''',
                                  [NexusSolverParameter(date='01/01/2020',
                                                        dt_auto=0.1,
                                                        dt_min=0.001,
                                                        dt_max=60.0,
                                                        dt_max_increase=8.0,
                                                        timestepping_method=TimeSteppingMethod.implicit,
                                                        ),
                                   ]),
                                ],
                             ids=['basic_test'])
    def test_load_run_parameters(self, mocker, file_content, expected_result):
        # Arrange

        solver_params = NexusSolverParameters(start_date=self.start_date,
                                              runcontrol_file=file_content.splitlines(keepends=True))
        # Act
        result = solver_params.solver_parameters

        # Assert
        assert result == expected_result
