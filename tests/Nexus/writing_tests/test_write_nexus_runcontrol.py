from ResSimpy import NexusSimulator
from ResSimpy.Enums.TimeSteppingMethodEnum import TimeSteppingMethod
from ResSimpy.Nexus.DataModels.NexusSolverParameter import NexusSolverParameter
from ResSimpy.Nexus.NexusSolverParameters import NexusSolverParameters
from ResSimpy.Nexus.runcontrol_operations import SimControls


def test_sim_controls_to_string():
    # Arrange
    model = NexusSimulator(start_date='01/01/2019', origin='test_sim.fcs', assume_loaded=True)
    sim_controls = SimControls(model=model)

    solver_param_list = [
        NexusSolverParameter(date='01/01/2020',
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
    solver_params = NexusSolverParameters(model)
    solver_params.set_solver_parameters(solver_param_list)

    sim_controls.set_solver_parameters(solver_params)

    model.set_sim_controls(sim_controls)
    expected_output = """START 01/01/2019
    
TIME 01/01/2020"""
