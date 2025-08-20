from ResSimpy import NexusSimulator
from ResSimpy.Enums.FrequencyEnum import FrequencyEnum
from ResSimpy.Enums.OutputType import OutputType
from ResSimpy.Enums.TimeSteppingMethodEnum import TimeSteppingMethod
from ResSimpy.Nexus.DataModels.NexusReportingRequests import NexusOutputRequest, NexusOutputContents
from ResSimpy.Nexus.DataModels.NexusSolverParameter import NexusSolverParameter
from ResSimpy.Nexus.NexusReporting import NexusReporting
from ResSimpy.Nexus.NexusSolverParameters import NexusSolverParameters
from ResSimpy.Nexus.nexus_model_file_generator import NexusModelFileGenerator
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
                             dcmax_impes=0.52,
                             impstab_on=False,
                             timestepping_method=TimeSteppingMethod.IMPLICIT

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

    # Add reporting controls
    
    reporting = NexusReporting(model=model, assume_loaded=True)
    output_requests = [NexusOutputRequest(date='01/02/2020', output='RFT', output_type=OutputType.ARRAY,
                                          output_frequency=FrequencyEnum.TNEXT, output_frequency_number=None),
                       NexusOutputRequest(date='01/02/2020', output='WELLS', output_type=OutputType.ARRAY,
                                          output_frequency=FrequencyEnum.YEARLY, output_frequency_number=None),
                       NexusOutputRequest(output_type=OutputType.SPREADSHEET, date='01/02/2020', output='NETWORK',
                                          output_frequency=FrequencyEnum.FREQ, output_frequency_number=120),
                       NexusOutputRequest(output_type=OutputType.SPREADSHEET, date='01/05/2020', output='FIELD',
                                          output_frequency=FrequencyEnum.MONTHLY, output_frequency_number=None),
                       NexusOutputRequest(output_type=OutputType.SPREADSHEET, date='01/05/2020', output='REGIONS',
                                          output_frequency=FrequencyEnum.FREQ, output_frequency_number=21),
                       ]
    
    output_contents = [NexusOutputContents(output_type=OutputType.SPREADSHEET, output='WELLS', date='01/01/2019',
                            output_contents=['DATE', 'TSNUM', 'QOP', 'QWP', 'COP', 'CWP', 'QWI', 'CWI', 'WCUT',
                                             'WPAVE', 'CGP', 'QGP', 'QLP', 'GOR', 'BHP', 'SAL']),
                       NexusOutputContents(output_type=OutputType.SPREADSHEET, output='FIELD', date='01/01/2019',
                                           output_contents=['DATE', 'TSNUM', 'COP', 'CGP', 'CWP', 'CWI', 'QOP', 'QGP',
                                                            'QWP', 'QLP',
                                                            'QWI', 'WCUT', 'OREC', 'PAVT', 'PAVH']),
                       NexusOutputContents(output_type=OutputType.ARRAY, output='P', date='01/04/2020',
                                           output_contents=[]),
                       NexusOutputContents(output_type=OutputType.ARRAY, output='SAT', date='01/04/2020',
                                           output_contents=['OIL', 'GAS', 'WATER']),
                       NexusOutputContents(output_type=OutputType.ARRAY, output='KR', date='01/04/2020',
                                           output_contents=['OIL', 'WATER']),
                       ]
    
    for output_req in output_requests: 
        reporting.add_array_output_request(output_req, add_to_file=False)
    
    for output_content in output_contents:
        reporting.add_array_output_contents_to_memory(output_content)
    
    model.set_reporting_controls(reporting)
    
    model_file_generator = NexusModelFileGenerator(model=model, model_name='new_model')
    
    expected_result = """START 01/01/2019

SSOUT
    WELLS DATE TSNUM QOP QWP COP CWP QWI CWI WCUT WPAVE CGP QGP QLP GOR BHP SAL
    FIELD DATE TSNUM COP CGP CWP CWI QOP QGP QWP QLP QWI WCUT OREC PAVT PAVH
ENDSSOUT

TIME 01/01/2020
DT AUTO 0.1
DT MIN 0.001
DT MAX 60.0
DT MAXINCREASE 8.0
METHOD IMPLICIT
SOLVER RESERVOIR CYCLELENGTH 10.0
SOLVER RESERVOIR MAXCYCLES 100.0
SOLVER RESERVOIR GLOBALTOL 0.0001
SOLVER GLOBAL DIRECT
SOLVER NOCUT
SOLVER PRECON_ILU
SOLVER KSUB_METHOD OrTHoMIN
SOLVER FACILITIES NOGRID
IMPSTAB OFF
DCMAX IMPES 0.52


TIME 01/02/2020
SPREADSHEET
    NETWORK FREQ 120
ENDSPREADSHEET
OUTPUT
    RFT TNEXT
    WELLS YEARLY
ENDOUTPUT

TIME 01/04/2020
MAPOUT
    P 
    SAT OIL GAS WATER
    KR OIL WATER
ENDMAPOUT

TIME 01/05/2020
DT MIN 10.0
SOLVER RESERVOIR CYCLELENGTH 11.0

SPREADSHEET
    FIELD MONTHLY
    REGIONS FREQ 21
ENDSPREADSHEET
"""

    # Act
    result = model_file_generator.output_runcontrol_section()

    # Assert
    assert result == expected_result
