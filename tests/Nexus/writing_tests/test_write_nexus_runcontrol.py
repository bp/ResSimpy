import pandas as pd
import pytest

from ResSimpy import NexusSimulator
from ResSimpy.Enums.TimeSteppingMethodEnum import TimeSteppingMethod
from ResSimpy.Nexus.DataModels.NexusSolverParameter import NexusSolverParameter
from ResSimpy.Nexus.DataModels.nexus_grid_to_proc import GridToProc
from ResSimpy.Nexus.NexusSolverParameters import NexusSolverParameters
from ResSimpy.Nexus.runcontrol_operations import SimControls


@pytest.mark.parametrize('test_grid_to_proc, expected_value', [
    (
            GridToProc(grid_to_proc_table=pd.DataFrame({
                'GRID': [1, 2, 3, 4],
                'PROCESS': [1, 2, 3, 4],
                'PORTYPE': ['MATRIX', 'MATRIX', 'FRACTURE', 'FRACTURE']
            }), auto_distribute=None),
            """GRIDTOPROC
             GRID  PROCESS PORTYPE 
            1     1          MATRIX
            2     2          MATRIX
            3     3        FRACTURE
            4     4        FRACTURE
            ENDGRIDTOPROC
            """
    ),
    (
            GridToProc(grid_to_proc_table=None, auto_distribute='GRIDBLOCKS'),
            "GRIDTOPROC\nAUTO GRIDBLOCKS\nENDGRIDTOPROC\n"
    )
])
def test_grid_to_proc_to_string(test_grid_to_proc, expected_value):
    # Arrange

    # Act
    result = test_grid_to_proc.to_string()

    # Assert
    assert result == expected_value


def test_sim_controls_to_string():
    # Arrange
    model = NexusSimulator(origin='test_sim.fcs', assume_loaded=True)
    sim_controls = SimControls(model=model)
    grid_to_proc = GridToProc(grid_to_proc_table=pd.DataFrame({
        'GRID': [1, 2, 3, 4],
        'PROCESS': [1, 2, 3, 4],
        'PORTYPE': ['MATRIX', 'MATRIX', 'FRACTURE', 'FRACTURE']
    }), auto_distribute=None)

    sim_controls.set_grid_to_proc(grid_to_proc)
    solver_param_list = [NexusSolverParameter(date='01/01/2020',
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
     ]
    solver_params = NexusSolverParameters('', )
