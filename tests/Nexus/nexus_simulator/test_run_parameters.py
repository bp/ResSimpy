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

                                 # more DT keywords
                                    ('''START 01/01/2020
                                    !     Timestep controls
                                    DT CON 0.1
                                    VIPTS 0.2
                                    QMAXPROD 0.3
                                    CONNOPEN 0.4
                                    MAXINCAFCUT 0.5
                                    ADJUSTTOTIME 0.6
                                    REDUCEAFCUT 0.7
                                    WCYCLE 0.8
                                    GCYCLE 0.9
                                    VIP_MAXINCREASE 1.0
                                    VIP_MAXINCAFCUT 1.1
                                    NEGMASSAQU
                                    
                                    ''',
                                     [NexusSolverParameter(date='01/01/2020',
                                                           dt_con=0.1,
                                                              dt_vipts=0.2,
                                                                dt_qmaxprod=0.3,
                                                                dt_connopen=0.4,
                                                                dt_maxincafcut=0.5,
                                                                dt_adjusttotime=0.6,
                                                                dt_reduceafcut=0.7,
                                                                dt_wcycle=0.8,
                                                                dt_gcycle=0.9,
                                                                dt_vip_maxincrease=1.0,
                                                                dt_vip_maxincafcut=1.1,
                                                                ),
                                        ]),
                                ],
                             ids=['basic_test' ,'more_DT_keywords'])
    def test_load_run_parameters(self, mocker, file_content, expected_result):
        # Arrange

        solver_params = NexusSolverParameters(start_date=self.start_date,
                                              runcontrol_file=file_content.splitlines(keepends=True))
        # Act
        result = solver_params.solver_parameters

        # Assert
        assert result == expected_result
