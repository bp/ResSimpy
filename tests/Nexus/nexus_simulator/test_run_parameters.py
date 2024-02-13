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

                                 # TIME dependent runcontrols
                                 ('''
                                 START 01/01/2020
                                 !     Timestep controls
                                 DT AUTO 0.1
                                    MIN 0.001
                                    MAX 60.
                                    MAXINCREASE 8.
                                    !     Timestepping method
                                    METHOD IMPLICIT
                                    TIME 01/05/2020
                                    DT MIN 10
                                    MAXINCREASE 21
                                    TIME 01/06/2020
                                    TIME 01/07/2020
                                    DT MAX 101''',
                                  [NexusSolverParameter(date='01/01/2020',
                                                        dt_auto=0.1,
                                                        dt_min=0.001,
                                                        dt_max=60.0,
                                                        dt_max_increase=8.0,
                                                        timestepping_method=TimeSteppingMethod.implicit,
                                                        ),
                                   NexusSolverParameter(date='01/05/2020',
                                                        dt_min=10.0,
                                                        dt_max_increase=21.0,
                                                        timestepping_method=TimeSteppingMethod.implicit,
                                                        ),
                                   NexusSolverParameter(date='01/07/2020',
                                                        dt_max=101.0,
                                                        timestepping_method=TimeSteppingMethod.implicit,
                                                        ),
                                   ]),

                                 # Solver keywords
                                 ('''START 01/01/2020
                                 SOLVER RESERVOIR CYCLELength 10
                                                  MAXCYCLES 100
                                                  GLOBALTOL 0.0001
                                        ALL       ITERATIVE
                                        
                                        NOCUT
                                        PRECON_ILU DROPTOL 0.1
                                        
                                        FACILITIES NOGRID
                                        KSUB_METHOD OrTHoMIN    
                                    
                                 ''',
                                  [NexusSolverParameter(date='01/01/2020',
                                                        solver_reservoir_cycle_length=10.0,
                                                        solver_reservoir_max_cycles=100.0,
                                                        solver_reservoir_globaltol=0.0001,
                                                        solver_reservoir_equation_solver='',
                                                        solver_timestep_cut=False,
                                                        solver_precon='PRECON_ILU DROPTOL 0.1',   ## TODO THINK ABOUT THIS
                                                        solver_facilities='NOGRID',
                                                        solver_ksub_method='OrTHoMIN',
                                                        ),
                                   ]),
                             ],
                             ids=['basic_test', 'more_DT_keywords', 'TIME_dependent_runcontrols'])
    def test_load_run_parameters(self, mocker, file_content, expected_result):
        # Arrange

        solver_params = NexusSolverParameters(start_date=self.start_date,
                                              runcontrol_file=file_content.splitlines(keepends=True))
        # Act
        result = solver_params.solver_parameters

        # Assert
        assert result == expected_result
