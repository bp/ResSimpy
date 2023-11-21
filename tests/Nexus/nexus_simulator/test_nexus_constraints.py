import uuid
from unittest.mock import Mock
import pandas as pd
import pytest
from ResSimpy.Nexus.DataModels.Network.NexusConstraint import NexusConstraint
from ResSimpy.Nexus.DataModels.Network.NexusConstraints import NexusConstraints
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.NexusSimulator import NexusSimulator
from tests.multifile_mocker import mock_multiple_files
from tests.utility_for_tests import get_fake_nexus_simulator

@pytest.mark.parametrize("file_contents, expected_content",[
    #'basic_test'
    (''' CONSTRAINTS
    well1	 QLIQSMAX 	3884.0  QWSMAX 	0
    well2	 QWSMAX 	0.0  QLIQSMAX- 10000.0 QLIQSMAX 15.5
    ENDCONSTRAINTS
    ''',
    ({'date': '01/01/2019', 'name': 'well1', 'max_surface_liquid_rate': 3884.0, 'max_surface_water_rate': 0,
    'unit_system': UnitSystem.ENGLISH},
     {'date': '01/01/2019', 'name': 'well2', 'max_surface_water_rate': 0.0, 'max_reverse_surface_liquid_rate': 10000.0,
      'max_surface_liquid_rate': 15.5, 'unit_system': UnitSystem.ENGLISH})),

    #'Change in Time'
    ('''CONSTRAINTS
    well1	 QLIQSMAX 	3884.0  QWSMAX 	0
    well2	 QWSMAX 	0.0  QLIQSMAX- 10000.0 QLIQSMAX 15.5
    ENDCONSTRAINTS
    TIME 01/01/2020
    CONSTRAINTS
    well1	 QLIQSMAX 	5000
    well2	 QWSMAX 	0.0  QLIQSMAX 20.5
    ENDCONSTRAINTS''',
    ({'date': '01/01/2019', 'name': 'well1', 'max_surface_liquid_rate': 3884.0, 'max_surface_water_rate': 0,'unit_system': UnitSystem.ENGLISH},
     {'date': '01/01/2019', 'name': 'well2', 'max_surface_water_rate': 0.0, 'max_reverse_surface_liquid_rate': 10000.0,
      'max_surface_liquid_rate': 15.5, 'unit_system': UnitSystem.ENGLISH},
     {'date': '01/01/2020', 'name': 'well1', 'max_surface_liquid_rate': 5000.0, 'unit_system': UnitSystem.ENGLISH},
   {'date': '01/01/2020', 'name': 'well2', 'max_surface_water_rate': 0.0, 'max_surface_liquid_rate': 20.5,
    'unit_system': UnitSystem.ENGLISH}
     )),
    #'more Keywords'
     ('''CONSTRAINTS
    well1	 QHCMAX- 	3884.0  PMIN 	0
    well2	 PMAX 	0.0  QLIQMIN 10000.0 QLIQMIN- 15.5 WORPLUGPLUS 85 CWLIM 155554
    ENDCONSTRAINTS''',
    ({'date': '01/01/2019', 'name': 'well1', 'max_reverse_reservoir_hc_rate': 3884.0, 'min_pressure': 0,
    'unit_system': UnitSystem.ENGLISH},
    {'date': '01/01/2019', 'name': 'well2', 'max_pressure': 0, 'min_reservoir_liquid_rate': 10000.0,
    'min_reverse_reservoir_liquid_rate': 15.5, 'max_wor_plug_plus': 85, 'max_cum_water_prod': 155554,
    'unit_system': UnitSystem.ENGLISH})),

    #'constraint table'
    ('''CONSTRAINT
    NAME    QLIQSMAX    QWSMAX 
    well1	  	3884.0   	0
    well2   0.0         10000
    ENDCONSTRAINT
    TIME 01/12/2023
    CONSTRAINTS
    well1	 QLIQSMAX 	1000.0
    ENDCONSTRAINTS
    ''', ({'date': '01/01/2019', 'name': 'well1', 'max_surface_liquid_rate': 3884.0, 'max_surface_water_rate': 0.0,
    'unit_system': UnitSystem.ENGLISH},
    {'date': '01/01/2019', 'name': 'well2', 'max_surface_liquid_rate': 0.0, 'max_surface_water_rate': 10000,
    'unit_system': UnitSystem.ENGLISH},
    {'date': '01/12/2023', 'name': 'well1', 'max_surface_liquid_rate': 1000.0, 'unit_system': UnitSystem.ENGLISH},
    )),

    #'multiple constraints on same well'
    ('''CONSTRAINTS
    well1	 QLIQSMAX 	1000.0
    well1   pmin    1700
    well1   thp     2000    ! comment
    ENDCONSTRAINTS''',
    ({'date': '01/01/2019', 'name': 'well1', 'max_surface_liquid_rate': 1000.0, 'min_pressure': 1700.0,
    'tubing_head_pressure': 2000.0, 'unit_system': UnitSystem.ENGLISH},)
    ),

    #'inline before table'
('''
    CONSTRAINTS
    well1	 QLIQSMAX 	1000.0    WORMAX 95
    ENDCONSTRAINTS
    TIME 01/12/2023
    CONSTRAINT
    NAME    QLIQSMAX    QWSMAX 
    well1	  	3884.0   	0
    well2   0.0         10000
    ENDCONSTRAINT
    
    ''', ({'date': '01/01/2019', 'name': 'well1', 'max_surface_liquid_rate': 1000.0,
            'unit_system': UnitSystem.ENGLISH, 'max_wor': 95.0},
    {'date': '01/12/2023', 'name': 'well1', 'max_surface_liquid_rate': 3884.0, 'max_surface_water_rate': 0.0,
    'unit_system': UnitSystem.ENGLISH},
    {'date': '01/12/2023', 'name': 'well2', 'max_surface_liquid_rate': 0.0, 'max_surface_water_rate': 10000,
    'unit_system': UnitSystem.ENGLISH},
    )),

    #'QMULT'
(''' CONSTRAINTS
    well1	 QLIQSMAX 	MULT  QOSMAX 	MULT
    well2	 QALLRMAX 	0
    well3   QALLRMAX        MULT 
    ENDCONSTRAINTS
    QMULT
    WELL QOIL QGAS QWATER
    well1 121.0 53.6 2.5
    well2 211.0 102.4 35.7
    well3  10.2 123   203
    ENDQMULT
    ''',
    ({'date': '01/01/2019', 'name': 'well1', 'use_qmult_qoilqwat_surface_rate': True, 'use_qmult_qoil_surface_rate': True,
    'unit_system': UnitSystem.ENGLISH, 'qmult_oil_rate': 121.0, 'qmult_gas_rate': 53.6, 'qmult_water_rate': 2.5, 'well_name':'well1'},
     {'date': '01/01/2019', 'name': 'well2', 'max_qmult_total_reservoir_rate': 0.0, 'unit_system': UnitSystem.ENGLISH,
     'qmult_oil_rate': 211.0, 'qmult_gas_rate': 102.4, 'qmult_water_rate': 35.7, 'well_name':'well2'},
    {'date': '01/01/2019', 'name': 'well3', 'convert_qmult_to_reservoir_barrels': True,
    'unit_system': UnitSystem.ENGLISH, 'qmult_oil_rate': 10.2, 'qmult_gas_rate': 123, 'qmult_water_rate': 203, 'well_name':'well3'},
      )),

    #'Clearing Constraints'
      ('''
    CONSTRAINTS
    well1	 QLIQSMAX 	1000.0    WORMAX 95
    well2  QLIQSMAX 1.8 PMAX    10000.2 QOSMAX MULT
    ENDCONSTRAINTS
    
    TIME 01/12/2023
    CONSTRAINTS
    well1 CLEARQ
    well2 CLEAR
    ENDCONSTRAINTS
    
    TIME 01/01/2024
    CONSTRAINTS
    well1  QOSMAX 1.8
    ENDCONSTRAINTS
    
    ''', ({'date': '01/01/2019', 'name': 'well1', 'max_surface_liquid_rate': 1000.0,
            'unit_system': UnitSystem.ENGLISH, 'max_wor': 95.0},
    {'date': '01/01/2019', 'name': 'well2', 'max_surface_liquid_rate': 1.8, 'max_pressure': 10000.2,
        'unit_system': UnitSystem.ENGLISH, 'use_qmult_qoil_surface_rate': True,},
    {'date': '01/12/2023', 'name': 'well1', 'unit_system': UnitSystem.ENGLISH, 'clear_q': True},
    {'date': '01/12/2023', 'name': 'well2', 'unit_system': UnitSystem.ENGLISH, 'clear_all': True},
    {'date': '01/01/2024', 'name': 'well1', 'max_surface_oil_rate': 1.8,
        'unit_system': UnitSystem.ENGLISH},
    )),

    #'activate keyword'
    (''' 
        CONSTRAINTS
    well1	 QLIQSMAX 	3884.0  ACTIVATE
    well2	 QWSMAX 	0.0  DEACTIVATE QLIQSMAX 15.5
    ENDCONSTRAINTS
    CONSTRAINTS
    ENDCONSTRAINTS
    WELLLIST RFTWELL
    CONSTRAINTS 
    well1 QLIQSMAX 0 DEACTIVATE
    ENDCONSTRAINTS
    ''',
    ({'date': '01/01/2019', 'name': 'well1', 'max_surface_liquid_rate': 0.0, 'active_node': False,
    'unit_system': UnitSystem.ENGLISH},
     {'date': '01/01/2019', 'name': 'well2', 'max_surface_water_rate': 0.0, 'active_node': False,
      'max_surface_liquid_rate': 15.5, 'unit_system': UnitSystem.ENGLISH},
      )),

    #'GORLIM_drawdowncards'
    (''' 
          CONSTRAINTS
      well1	 DPBHAVG 1024.2  DPBHMX OFF  GORLIM NONE EXPONENT 9999
      ENDCONSTRAINTS
      ''',
      ({'date': '01/01/2019', 'name': 'well1', 'max_avg_comp_dp': 1024.2, 'gor_limit_exponent': 9999.0, 'unit_system': UnitSystem.ENGLISH},
        )),
    # MULT keyword with a number after it
    ('''
CONSTRAINTS
well1 QOSMAX MULT      9999
ENDCONSTRAINTS

QMULT
WELL       QOIL        QGAS        QWATER
well1      0           0.0         0
ENDQMULT ''',
         ({'date': '01/01/2019', 'name': 'well1', 'use_qmult_qoil_surface_rate': True,
    'unit_system': UnitSystem.ENGLISH, 'qmult_oil_rate': 0.0, 'qmult_gas_rate': 0.0, 'qmult_water_rate': 0.0, 'well_name':'well1'},
          )
     ),
    ], ids=['basic_test', 'Change in Time', 'more Keywords', 'constraint table', 'multiple constraints on same well',
    'inline before table', 'QMULT', 'Clearing Constraints', 'activate keyword', 'GORLIM_drawdowncards', 'MULT keyword with a number after it'])
def test_load_constraints(mocker, file_contents, expected_content):
    # Arrange
    start_date = '01/01/2019'
    surface_file = NexusFile(location='surface.dat', file_content_as_list=file_contents.splitlines())
    expected_constraints = {}
    for constraint in expected_content:
        well_name = constraint['name']
        if expected_constraints.get(well_name, None) is not None:
            expected_constraints[well_name].append(NexusConstraint(constraint))
        else:
            expected_constraints[well_name] = [NexusConstraint(constraint)]
    expected_date_filtered_constraints = {}
    for constraint in expected_content:
        if constraint['date'] == '01/01/2019':
            well_name = constraint['name']
            if expected_date_filtered_constraints.get(well_name, None) is not None:
                expected_date_filtered_constraints[well_name].append(NexusConstraint(constraint))
            else:
                expected_date_filtered_constraints[well_name] = [NexusConstraint(constraint)]
    expected_single_name_constraint = {'well1': expected_constraints['well1']}
    mock_nexus_network = mocker.MagicMock()
    mocker.patch('ResSimpy.Nexus.NexusNetwork.NexusNetwork', mock_nexus_network)
    expected_df = pd.DataFrame(expected_content)

    mock_nexus_sim = get_fake_nexus_simulator(mocker)

    # Act
    constraints = NexusConstraints(mock_nexus_network, mock_nexus_sim)
    constraints.load(surface_file, start_date, UnitSystem.ENGLISH)
    result = constraints.get_all()
    result_single = constraints.get_all(object_name='well1')
    result_df = constraints.get_df()
    result_date_filtered = constraints.get_all(date='01/01/2019')
    # sort the dates for comparing dataframes (order normally wouldn't matter)
    result_df['date'] = pd.to_datetime(result_df['date'])
    result_df = result_df.sort_values('date').reset_index(drop=True)

    expected_df['date'] = pd.to_datetime(expected_df['date'])
    expected_df = expected_df.sort_values('date').reset_index(drop=True)
    # Assert
    assert result == expected_constraints
    assert result_single == expected_single_name_constraint
    pd.testing.assert_frame_equal(result_df, expected_df, check_like=True)
    assert result_date_filtered == expected_date_filtered_constraints


@pytest.mark.parametrize('file_contents, object_locations', [
        ('''CONSTRAINTS
        ! comment
            well1	 QLIQSMAX 	3884.0  QWSMAX 	0

            well2	 QWSMAX 	0.0  QLIQSMAX- 10000.0 QLIQSMAX 15.5
    ENDCONSTRAINTS
        ''',
        {'uuid1': [2],
         'uuid2': [4]}
        ),

('''CONSTRAINTS
        ! comment
            well1	 QLIQSMAX 	3884.0  QWSMAX 	0

            well2	 QWSMAX 	0.0  QLIQSMAX- 10000.0 QLIQSMAX 15.5
    ENDCONSTRAINTS
    
    CONSTRAINTS
            ! comment
            well3	 QLIQSMAX 	3884.0  QWSMAX 	0

            well4	 QWSMAX 	0.0  QLIQSMAX- 10000.0
    ENDCONSTRAINTS
        ''',
        {'uuid1': [2],
         'uuid2': [4],
         'uuid3': [9],
         'uuid4': [11]}
        ),

('''CONSTRAINTS
        ! comment
            well1	 QLIQSMAX 	3884.0  QWSMAX 	0

            well1	 QWSMAX 	0.0  QLIQSMAX- 10000.0 QLIQSMAX 15.5
    ENDCONSTRAINTS

    CONSTRAINTS
            ! comment
            well1	 QOSMAX 	1234  QWSMAX 	0

            well1	 QWSMAX 	12334  QLIQSMAX- 10000.0
    ENDCONSTRAINTS
        ''',
        {'uuid1': [2, 4, 9, 11],
     }
            ),

            ('''CONSTRAINT
        NAME    QLIQSMAX    QWSMAX  QLIQSMAX-
        
        well1	3884.0   	0       NA
        
        
        well2   15.5        0       10000
        
        
        ENDCONSTRAINT
        ''',
    {'uuid1': [3],
    'uuid2': [6]
     }
    ),

    (''' TIME 01/01/2019
    CONSTRAINTS
    well1	 QLIQSMAX 	MULT  QOSMAX 	MULT
    well2	 QALLRMAX 	0
    ENDCONSTRAINTS
    QMULT
    WELL QOIL QGAS QWATER
    well1 121.0 53.6 2.5
    well2 211.0 102.4 35.7
    ENDQMULT''',
    {'uuid1': [2, 7],
     'uuid2': [3, 8]}
    ),
        ], ids=['basic_test', 'two tables', 'several constraints for one well', 'constraint_table', 'qmults'])
def test_constraint_ids(mocker, file_contents, object_locations):
    # Arrange
    fcs_file_data = '''RUN_UNITS ENGLISH

    DATEFORMAT DD/MM/YYYY

    RECURRENT_FILES
    RUNCONTROL ref_runcontrol.dat
    SURFACE Network 1 surface.dat'''
    runcontrol_data = 'START 01/01/2020'

    def mock_open_wrapper(filename,  mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            'fcs_file.dat': fcs_file_data,
            'surface.dat': file_contents,
            'ref_runcontrol.dat': runcontrol_data,
        }).return_value
        return mock_open
    mocker.patch("builtins.open", mock_open_wrapper)

    ls_dir = Mock(side_effect=lambda x: [])
    mocker.patch('os.listdir', ls_dir)
    fcs_file_exists = Mock(side_effect=lambda x: True)
    mocker.patch('os.path.isfile', fcs_file_exists)

    model = NexusSimulator('fcs_file.dat')

    mocker.patch.object(uuid, 'uuid4', side_effect=['uuid1', 'uuid2', 'uuid3',
                                                    'uuid4', 'uuid5', 'uuid6', 'uuid7'])
    # Act
    model.network.constraints.get_all()

    result = model.model_files.surface_files[1].object_locations
    # Assert
    assert result == object_locations

def test_nexus_constraint_repr(mocker):
    # Arrange
    # patch the uuid
    mocker.patch('uuid.uuid4', return_value='uuid1')
    constraint = NexusConstraint({'date': '01/01/2019', 'name': 'well1', 'max_surface_liquid_rate': 3884.0,
                                  'max_surface_water_rate': 0})
    expected_repr = ("NexusConstraint(_DataObjectMixin__id='uuid1', date='01/01/2019', name='well1', max_surface_liquid_rate=3884.0, "
                     "max_surface_water_rate=0)")
    expected_str = ("NexusConstraint(date='01/01/2019', name='well1', max_surface_liquid_rate=3884.0, "
                     "max_surface_water_rate=0)")
    # Act
    repr_result = constraint.__repr__()
    str_result = constraint.__str__()

    # Assert
    assert repr_result == expected_repr
    assert str_result == expected_str