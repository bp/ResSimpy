from unittest.mock import Mock

import pytest

from ResSimpy.Enums.TimeSteppingMethodEnum import TimeSteppingMethod
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.NexusSolverParameter import NexusSolverParameter
from ResSimpy.Nexus.NexusSimulator import NexusSimulator
from ResSimpy.Nexus.NexusSolverParameters import NexusSolverParameters
from tests.multifile_mocker import mock_multiple_files
from tests.utility_for_tests import get_fake_nexus_simulator


class TestNexusSolverParameters:
    start_date = '01/01/2020'
    basic_data = '''START 01/01/2020
                                 !     Timestep controls
                                 DT AUTO 0.1
                                    MIN 0.001
                                    MAX 60.
                                    MAXINCREASE 8.
                                    !     Timestepping method
                                    METHOD IMPLICIT
                                    '''
    # mock fcs file and runcontrol file
    fcs_file_path = '/path/fcs_file.fcs'
    runcontrol_path = '/runcontrol_file.dat'
    fcs_content = f'''DESC reservoir1
    RUN_UNITS ENGLISH
    DATEFORMAT DD/MM/YYYY
    RUNCONTROL {runcontrol_path}
    '''
    @pytest.mark.parametrize(
        'file_content, expected_result',
        [
            # basic_test
            (basic_data,
             [NexusSolverParameter(date='01/01/2020',
                                   dt_auto=0.1,
                                   dt_min=0.001,
                                   dt_max=60.0,
                                   dt_max_increase=8.0,
                                   timestepping_method=TimeSteppingMethod.IMPLICIT,
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
            NEGMASSAQU 2
            
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
                                   negmassaqu=2.0,
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
                                   timestepping_method=TimeSteppingMethod.IMPLICIT,
                                   ),
              NexusSolverParameter(date='01/05/2020',
                                   dt_min=10.0,
                                   dt_max_increase=21.0,
                                   ),
              NexusSolverParameter(date='01/07/2020',
                                   dt_max=101.0,
                                   ),
              ]),

            # Solver keywords
            ('''START 01/01/2020
             SOLVER RESERVOIR CYCLELength 10
                              MAXcycLES 100
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
                                   solver_reservoir_equation_solver=None,
                                   solver_all_equation_solver='ITERATIVE',
                                   solver_timestep_cut=False,
                                   solver_precon='PRECON_ILU',
                                   solver_precon_setting='DROPTOL',
                                   solver_precon_value=0.1,
                                   solver_facilities='NOGRID',
                                   solver_ksub_method='OrTHoMIN',
                                   ),
              ]),
            # Combined solver and dt
            ('''START 01/01/2020
                SOLVER RESERVOIR CYCLELength 10
                              MAXcycLES 100
                              GLOBALTOL 0.0001
                    GLOBAL       DIRECT
                    
                    NOCUT
                    PRECON_ILU DROPTOL 0.1
                    
                    FACILITIES NOGRID
                    KSUB_METHOD OrTHoMIN    
                    
                    DT AUTO 0.1
                    MIN 0.001
                    MAX 60.
                    MAXINCREASE 8.
                    !     Timestepping method
                    METHOD IMPLICIT
                TIME 01/05/2020
                DT MIN 10
                SOLVER RESERVOIR CYCLELength 11
                                    ''',
             [NexusSolverParameter(date='01/01/2020',
                                   solver_reservoir_cycle_length=10.0,
                                   solver_reservoir_max_cycles=100.0,
                                   solver_reservoir_globaltol=0.0001,
                                   solver_reservoir_equation_solver=None,
                                   solver_global_equation_solver='DIRECT',
                                   solver_timestep_cut=False,
                                   solver_precon='PRECON_ILU',
                                   solver_precon_setting='DROPTOL',
                                   solver_precon_value=0.1,
                                   solver_facilities='NOGRID',
                                   solver_ksub_method='OrTHoMIN',
                                   dt_auto=0.1,
                                   dt_min=0.001,
                                   dt_max=60.0,
                                   dt_max_increase=8.0,
                                   timestepping_method=TimeSteppingMethod.IMPLICIT,
                                   ),
              NexusSolverParameter(date='01/05/2020',
                                   dt_min=10.0,
                                   solver_reservoir_cycle_length=11.0,
                                   ),
              ]),

            # Duplicate keywords in a given timestep
            ('''
                                 START 01/01/2020
                                 !     Timestep controls
                                 DT MIN 0.002
                                    MIN 0.2''',
             [NexusSolverParameter(date='01/01/2020',
                                   dt_min=0.2,
                                   ),
              ]),

            # All solver keywords
            ('''START 01/01/2020
            SOLVER GLOBAL CYCLELENGTH 10
            MAXCYCLES 100
            DUAL_SOLVER OFF
            
            PSEUDO_SLACK ON
            MUMPS_SOLVER ON
            PRESSURE_COUPLING GEA
            PRECON_AMG_RS
            ''',
             [NexusSolverParameter(date='01/01/2020',
                                   solver_global_cycle_length=10.0,
                                   solver_global_max_cycles=100.0,
                                   solver_dual_solver=False,
                                   solver_pressure_coupling='GEA',
                                   solver_precon='PRECON_AMG_RS',
                                   solver_pseudo_slack=True,
                                   solver_mumps_solver='ON',

                                   ),
              ]),

            # Implicit Mbal keywords
            ('''START 01/01/2020
            IMPLICITMBAL NEGMASS''',
             [NexusSolverParameter(date='01/01/2020',
                                   implicit_mbal='NEGMASS',
                                   ),
              ]),
            # Impstab keywords
            ('''START 01/01/2020
            IMPSTAB OFF
            COATS
            
            SKIPMASSCFL
            TARGETCFL 0.2
            LIMITCFL 0.3
            SKIPBLOCKDCMAX 20''',
             [NexusSolverParameter(date='01/01/2020',
                                   impstab_on=False,
                                   impstab_criteria='COATS',
                                   impstab_skip_mass_cfl=True,
                                   impstab_target_cfl=0.2,
                                   impstab_limit_cfl=0.3,
                                   impstab_skip_block_dcmax=20,
                                   ),
              ]),

            # GRIDSOLVER keywords
            ('''START 01/01/2020
            GRIDSOLVER IMPLICIT_COUPLING OFF
            IMPES_COUPLING ON
            CPR_PRESSURE_EQUATION OFF
            PRESS_RED 0.1
            GRID_RED 0.2
            IMPLICIT_RED 0.3
            
            PERFREV ALLOW
            ''',
             [NexusSolverParameter(date='01/01/2020',
                                   gridsolver_implicit_coupling_setting='OFF',
                                   gridsolver_impes_coupling_setting='ON',
                                   gridsolver_cpr_pressure_equation='OFF',
                                   gridsolver_press_reduction=0.1,
                                   gridsolver_grid_reduction=0.2,
                                   gridsolver_implicit_reduction=0.3,
                                   perfrev='ALLOW',
                                   ),
              ]),
            # SOLO_KEYWORDS
            ('''START 01/01/2020
            MAXNEWTONS 100
            MAXBADNETS 200
            CUTFACTOR 0.1
            NEGMASSCUT 0.2
            DVOLLIM 0.3
            DZLIM 0.4
            DSLIM 0.5
            DPLIM 0.6
            DMOBLIM 0.7
            DSGLIM 0.8
            NEGFLOWLIM 0.9
            NEGMASSAQU 1.0
            KRDAMP 1.1
            VOLERR_PREV 1.2
            SGCTOL 1.3
            EGSGTOL 1.4
            SGCPERFTOL 1.5
            LINE_SEARCH 1.6
            PERFP_DAMP 1.7
            ''',
             [NexusSolverParameter(date='01/01/2020',
                                   maxnewtons=100,
                                   maxbadnets=200,
                                   cutfactor=0.1,
                                   negmasscut=0.2,
                                   dvollim=0.3,
                                   dzlim=0.4,
                                   dslim=0.5,
                                   dplim=0.6,
                                   dmoblim=0.7,
                                   dsglim=0.8,
                                   negflowlim=0.9,
                                   negmassaqu=1.0,
                                   krdamp=1.1,
                                   volerr_prev=1.2,
                                   sgctol=1.3,
                                   egsgtol=1.4,
                                   sgcperftol=1.5,
                                   line_search=1.6,
                                   perfp_damp=1.7,
                                   ),
              ]),
            # TODO:
            # TOLS keywords
            ('''START 01/01/2020
            TOLS VOLCON 0.1
            MASS 0.2
            TARGET 0.3
            WELLMBAL 0.4
            PERF 0.5
            ''',
             [NexusSolverParameter(date='01/01/2020',
                                   tols_volcon=0.1,
                                   tols_mass=0.2,
                                   tols_target=0.3,
                                   tols_wellmbal=0.4,
                                   tols_perf=0.5,
                                   ),
              ]),
            # DCMAX_KEYWORDS
            ('''START 01/01/2020
            DCMAX IMPES 0.1
                IMPLICIT 0.2
            VOLRPT ALL 0.3
            IMPEs 0.4
            
            ''',

             [NexusSolverParameter(date='01/01/2020',
                                   dcmax_impes=0.1,
                                   dcmax_implicit=0.2,
                                   volrpt_all=0.3,
                                   volrpt_impes=0.4,
                                   ),
              ]),

            # drsdt
            ('''START 01/01/2020
            DRSDT LIMIT 0.1''',
             [NexusSolverParameter(date='01/01/2020',
                                   drsdt_limit=0.1,
                                   ),
              ]),

            # drsdt_two_phases
            ('''START 01/01/2020
            DRSDT LIMIT 0.1 2PHASE''',
             [NexusSolverParameter(date='01/01/2020',
                                   drsdt_limit=0.1,
                                   drsdt_two_phases=True
                                   ),
              ]),
            # Keywords in a line

        ],
        ids=['basic_test', 'more_DT_keywords', 'TIME_dependent_runcontrols', 'Solver_keywords',
             'Combined_solver_and_dt', 'Duplicate_keywords_in_a_given_timestep', 'All_solver_keywords',
             'Implicit_Mbal_keywords', 'Impstab_keywords', 'GRIDSOLVER_keywords', 'Solo keywords',
             'TOLS_keywords', 'DCMAX_KEYWORDS', 'drsdt', 'drsdt_two_phases'])  # 'Keywords_in_a_line'])
    
    def test_load_run_parameters(self, mocker, file_content, expected_result):
        # Arrange
        def mock_open_wrapper(filename, mode):
            mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
                '/path/fcs_file.fcs': self.fcs_content,
                '/runcontrol_file.dat': file_content
            }).return_value
            return mock_open
        mocker.patch("builtins.open", mock_open_wrapper)

        mock_sim = get_fake_nexus_simulator(mocker, fcs_file_path='/path/fcs_file.fcs', mock_open=False)
        mock_sim.start_date = self.start_date

        solver_params = NexusSolverParameters(mock_sim)
        # Act
        result = solver_params.solver_parameters

        # Assert
        assert result == expected_result

    def test_load_run_parameters_from_sim(self, mocker):
        # Arrange

        def mock_open_wrapper(filename, mode):
            mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
                self.fcs_file_path: self.fcs_content,
                self.runcontrol_path: self.basic_data,
            }).return_value
            return mock_open

        mocker.patch("builtins.open", mock_open_wrapper)
        fcs_file_exists = Mock(side_effect=lambda x: True)
        mocker.patch('os.path.isfile', fcs_file_exists)

        nexus_sim = NexusSimulator(self.fcs_file_path)
        nexus_sim.start_date = self.start_date
        expected_result = [NexusSolverParameter(date='01/01/2020',
                                                dt_auto=0.1,
                                                dt_min=0.001,
                                                dt_max=60.0,
                                                dt_max_increase=8.0,
                                                timestepping_method=TimeSteppingMethod.IMPLICIT,
                                                )]
        # Act
        result = nexus_sim.sim_controls.solver_parameters
        # Assert
        assert result == expected_result
