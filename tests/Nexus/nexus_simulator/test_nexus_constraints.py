from unittest.mock import Mock
import pandas as pd
import pytest
from pytest_mock import MockerFixture

from ResSimpy.DataModelBaseClasses.OperationsMixin import NetworkOperationsMixIn
from ResSimpy.Time.ISODateTime import ISODateTime
from ResSimpy.Nexus.DataModels.Network.NexusConstraint import NexusConstraint
from ResSimpy.Nexus.DataModels.Network.NexusConstraints import NexusConstraints
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.Nexus.NexusSimulator import NexusSimulator
from tests.multifile_mocker import mock_multiple_files
from tests.utility_for_tests import get_fake_nexus_simulator


@pytest.mark.parametrize("file_contents, expected_content", [
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
     ({'date': '01/01/2019', 'name': 'well1', 'max_surface_liquid_rate': 3884.0,
       'max_surface_water_rate': 0, 'unit_system': UnitSystem.ENGLISH},
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
     ({'date': '01/01/2019', 'name': 'well1', 'use_qmult_qoilqwat_surface_rate': True,
       'use_qmult_qoil_surface_rate': True,
       'unit_system': UnitSystem.ENGLISH, 'qmult_oil_rate': 121.0, 'qmult_gas_rate': 53.6, 'qmult_water_rate': 2.5,
       'well_name': 'well1'},
      {'date': '01/01/2019', 'name': 'well2', 'max_qmult_total_reservoir_rate': 0.0, 'unit_system': UnitSystem.ENGLISH,
       'qmult_oil_rate': 211.0, 'qmult_gas_rate': 102.4, 'qmult_water_rate': 35.7, 'well_name': 'well2'},
      {'date': '01/01/2019', 'name': 'well3', 'convert_qmult_to_reservoir_barrels': True,
       'unit_system': UnitSystem.ENGLISH, 'qmult_oil_rate': 10.2, 'qmult_gas_rate': 123, 'qmult_water_rate': 203,
       'well_name': 'well3'},
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
           'unit_system': UnitSystem.ENGLISH, 'use_qmult_qoil_surface_rate': True},
          {'date': '01/12/2023', 'name': 'well1', 'unit_system': UnitSystem.ENGLISH, 'clear_q': True},
          {'date': '01/12/2023', 'name': 'well2', 'unit_system': UnitSystem.ENGLISH, 'clear_all': True},
          {'date': '01/01/2024', 'name': 'well1', 'max_surface_oil_rate': 1.8,
           'unit_system': UnitSystem.ENGLISH}
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
     ({'date': '01/01/2019', 'name': 'well1', 'max_avg_comp_dp': 1024.2, 'gor_limit_exponent': 9999.0,
       'unit_system': UnitSystem.ENGLISH},
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
       'unit_system': UnitSystem.ENGLISH, 'qmult_oil_rate': 0.0, 'qmult_gas_rate': 0.0, 'qmult_water_rate': 0.0,
       'well_name': 'well1'},)
     ),

    # 'Change in Time, loading in pressure also'
    ('''CONSTRAINTS
 well1	 QLIQSMAX 	3884.0  QWSMAX 	0 PMAX 3000
 well2	 QWSMAX 	0.0  QLIQSMAX- 10000.0 QLIQSMAX 15.5 PMIN 1200
 ENDCONSTRAINTS
 TIME 01/01/2020
 CONSTRAINTS
 well1	 QLIQSMAX 	5000
 well2	 QWSMAX 	0.0  QLIQSMAX 20.5
 ENDCONSTRAINTS''',
     ({'date': '01/01/2019', 'name': 'well1', 'max_surface_liquid_rate': 3884.0,
       'max_surface_water_rate': 0, 'unit_system': UnitSystem.ENGLISH, 'max_pressure': 3000},
      {'date': '01/01/2019', 'name': 'well2', 'max_surface_water_rate': 0.0, 'max_reverse_surface_liquid_rate': 10000.0,
       'max_surface_liquid_rate': 15.5, 'unit_system': UnitSystem.ENGLISH, 'min_pressure': 1200},
      {'date': '01/01/2020', 'name': 'well1', 'max_surface_liquid_rate': 5000.0, 'unit_system': UnitSystem.ENGLISH},
      {'date': '01/01/2020', 'name': 'well2', 'max_surface_water_rate': 0.0, 'max_surface_liquid_rate': 20.5,
       'unit_system': UnitSystem.ENGLISH}
      )),

    # 'line continuation'
    (''' CONSTRAINTS
well1	 QLIQSMAX 	3884.0 >
  QWSMAX 	0
well2	 QWSMAX 	0.0 >
 QLIQSMAX- 10000.0 QLIQSMAX 15.5
ENDCONSTRAINTS
''',
     ({'date': '01/01/2019', 'name': 'well1', 'max_surface_liquid_rate': 3884.0, 'max_surface_water_rate': 0,
       'unit_system': UnitSystem.ENGLISH},
      {'date': '01/01/2019', 'name': 'well2', 'max_surface_water_rate': 0.0, 'max_reverse_surface_liquid_rate': 10000.0,
       'max_surface_liquid_rate': 15.5, 'unit_system': UnitSystem.ENGLISH})),

    # 'line continuation with whitespace'
    (''' CONSTRAINTS
well1	 QLIQSMAX 	3884.0 > \t
  QWSMAX 	0
well2	 QWSMAX 	0.0 >
 QLIQSMAX- 10000.0 QLIQSMAX 15.5
ENDCONSTRAINTS
''',
     ({'date': '01/01/2019', 'name': 'well1', 'max_surface_liquid_rate': 3884.0, 'max_surface_water_rate': 0,
       'unit_system': UnitSystem.ENGLISH},
      {'date': '01/01/2019', 'name': 'well2', 'max_surface_water_rate': 0.0, 'max_reverse_surface_liquid_rate': 10000.0,
       'max_surface_liquid_rate': 15.5, 'unit_system': UnitSystem.ENGLISH})),
   
    # QALLMAX None values
    (''' 
    CONSTRAINTS        
well1   PMIN    5.0
well1  QALLMAX 0.00
well1  QGSMAX  0.00
ENDCONSTRAINTS

    CONSTRAINTS
well1  ACTIVATE
well1 QALLMAX NONE QALLRMAX NONE QOSMIN 20 QOSMAX 2025.52
well1 QGSMAX 204015021.2
ENDCONSTRAINTS
''',
     ({'date': '01/01/2019', 'name': 'well1', 'min_surface_oil_rate': 20.0, 'max_surface_oil_rate': 2025.52,
       'max_surface_gas_rate': 204015021.2, 'active_node': True, 'unit_system': UnitSystem.ENGLISH,
       'min_pressure': 5.0},
      )),
    
    # two constraint tables 1 date same well
    ('''TIME 01/04/2024

CONSTRAINTS
well1      ACTIVATE
well1           DPBHAVG 10.24
well1            QALLMAX NONE    QALLRMAX NONE   QOSMIN 25.2     QOSMAX 4000.49
well1            QGSMAX 12222.26
well1           WCUTMAX 0.90
ENDCONSTRAINTS

CONSTRAINTS
well1           WCUTMAX 0.95
ENDCONSTRAINTS
''',
     ({'date': '01/04/2024', 'name': 'well1', 'max_avg_comp_dp': 10.24, 'max_reservoir_total_fluids_rate': None,
       'max_qmult_total_reservoir_rate': None, 'min_surface_oil_rate': 25.2, 'max_surface_oil_rate': 4000.49,
       'max_surface_gas_rate': 12222.26, 'max_watercut': 0.95, 'active_node': True, 'unit_system': UnitSystem.ENGLISH},))
], ids=['basic_test', 'Change in Time', 'more Keywords', 'constraint table', 'multiple constraints on same well',
        'inline before table', 'QMULT', 'Clearing Constraints', 'activate keyword', 'GORLIM_drawdowncards',
        'MULT keyword with a number after it', 'loading in pressure', 'line continuation',
        'line continuation with whitespace', 'QALLMAX None values',  'two constraint tables 1 date same well'])
def test_load_constraints(mocker, file_contents, expected_content):
    # Arrange
    start_date = '01/01/2019'
    mocker.patch('ResSimpy.DataModelBaseClasses.DataObjectMixin.uuid4', return_value='uuid_1')

    surface_file = NexusFile(location='surface.dat', file_content_as_list=file_contents.splitlines())
    expected_constraints = {}

    for constraint in expected_content:
        well_name = constraint['name']
        if expected_constraints.get(well_name, None) is not None:
            expected_constraints[well_name].append(NexusConstraint(constraint, date_format=DateFormat.MM_DD_YYYY,
                                                                   start_date=start_date))
        else:
            expected_constraints[well_name] = [NexusConstraint(constraint, date_format=DateFormat.MM_DD_YYYY,
                                                               start_date=start_date)]

    expected_date_filtered_constraints = {}
    for constraint in expected_content:
        if constraint['date'] == '01/01/2019':
            well_name = constraint['name']
            if expected_date_filtered_constraints.get(well_name, None) is not None:
                expected_date_filtered_constraints[well_name].append(NexusConstraint(constraint,
                                                                                     date_format=DateFormat.MM_DD_YYYY,
                                                                                     start_date=start_date))
            else:
                expected_date_filtered_constraints[well_name] = [NexusConstraint(constraint,
                                                                                 date_format=DateFormat.MM_DD_YYYY,
                                                                                 start_date=start_date)]
        # set the expected iso_date in the constraints for adding to the expected dataframe
        constraint['iso_date'] = ISODateTime.convert_to_iso(date=constraint['date'], date_format=DateFormat.MM_DD_YYYY,
                                                            start_date=start_date)

    expected_single_name_constraint = {'well1': expected_constraints['well1']}
    mock_nexus_network = mocker.MagicMock()
    mocker.patch('ResSimpy.Nexus.NexusNetwork.NexusNetwork', mock_nexus_network)
    expected_df = pd.DataFrame([{k: v for k, v in x.items() if v is not None} for x in expected_content])

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
    assert result_single == expected_single_name_constraint
    assert result == expected_constraints
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

    def mock_open_wrapper(filename, mode):
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

    mocker.patch('ResSimpy.DataModelBaseClasses.DataObjectMixin.uuid4',
                 side_effect=['uuid1', 'uuid2', 'uuid3', 'uuid4', 'uuid5', 'uuid6',
                              'uuid7'])

    # Act
    model.network.constraints.get_all()

    result = model.model_files.surface_files[1].object_locations
    # Assert
    assert result == object_locations


def test_nexus_constraint_repr(mocker):
    # Arrange
    # patch the uuid
    mocker.patch('ResSimpy.DataModelBaseClasses.DataObjectMixin.uuid4', return_value='uuid1')
    constraint = NexusConstraint({'date': '01/01/2019', 'name': 'well1', 'max_surface_liquid_rate': 3884.0,
                                  'max_surface_water_rate': 0})
    expected_repr = ("NexusConstraint(ID='uuid1', Date='01/01/2019', name='well1', "
                     'max_surface_water_rate=0, max_surface_liquid_rate=3884.0, '
                     "ISO_Date='2019-01-01T00:00:00')")
    expected_str = ("NexusConstraint(_DataObjectMixin__date='01/01/2019', name='well1', "
                    'max_surface_water_rate=0, max_surface_liquid_rate=3884.0, '
                    '_DataObjectMixin__iso_date=ISODateTime(2019,T1,T1,T0,T0))')
    # Act
    repr_result = constraint.__repr__()
    str_result = constraint.__str__()

    # Assert
    assert repr_result == expected_repr
    assert str_result == expected_str


def test_nexus_constraints_skip_procs(mocker):
    # Arrange
    surface_content = '''TIME 04/10/2019

PROCS NAME START_SEAM_TUNING  CLEAR PRIORITY 2
	IF(TIME > 0.0) THEN
 DO something
 NODELIST, STATIC, WELLHEADS, BHNODES_INJ
 ENDDO
 ENDIF
ENDPROCS
PROCABORT ARRAYBOUNDS

PROCS NAME SETOPTIONS  CLEAR PRIORITY 1

INCLUDE procs_file.dat
CONSTRAINTS
   WELL1 QOSMAX 6100.7
ENDCONSTRAINTS
'''

    fcs_file_data = '''RUN_UNITS ENGLISH

    DATEFORMAT DD/MM/YYYY

    RECURRENT_FILES
    RUNCONTROL ref_runcontrol.dat
    SURFACE Network 1 surface.dat'''
    runcontrol_data = 'START 01/01/2020'

    extra_procs_data = '''
	IF( TIME > 0.0) THEN
 DO something
 NODELIST, STATIC, WELLHEADS, BHNODES_INJ
 ENDDO
 ENDIF
ENDPROCS'''

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            'fcs_file.dat': fcs_file_data,
            'surface.dat': surface_content,
            'ref_runcontrol.dat': runcontrol_data,
            'procs_file.dat': extra_procs_data,
        }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)
    model = NexusSimulator('fcs_file.dat')
    # Act
    constraint = model.network.constraints.get_all()['WELL1'][0]
    procs = model.network.procs.get_all()
    # Assert
    assert constraint.date == '04/10/2019'
    assert len(procs) == 2


def test_load_constraints_welllist(mocker: MockerFixture):
    """Ensure that a constraint applied to a welllist has the properties applied to all wells within it. """
    # Arrange
    fcs_file_contents = '''
         RUN_UNITS ENGLISH
         DATEFORMAT DD/MM/YYYY
         RECURRENT_FILES
         RUNCONTROL /nexus_data/runcontrol.dat
         SURFACE Network 1  /surface_file_01.dat
         '''
    start_date = '09/07/2024'
    runcontrol_contents = '''START 09/07/2024'''

    surface_file_contents = """
    WELLLIST some_wells
    ADD
    well_1
    ENDWELLLIST
    
    CONSTRAINTS
    some_wells	 QLIQSMAX 	3884.0  QWSMAX 	0
    ENDCONSTRAINTS
    
    TIME 23/08/2024
    
    ! Redefine the welllist to check that the new constraints only get applied to newly added wells after this point.
    WELLLIST some_wells
    ADD
    well_2
    ENDWELLLIST
    
    CONSTRAINT
    NAME   QOSMAX
    some_wells 123.4
    ENDCONSTRAINT
    
    TIME 15/10/2024
    
    WELLLIST some_wells
    REMOVE
    well_1
    ENDWELLLIST
    
    CONSTRAINTS
    some_wells	QLIQSMAX 4567
    ENDCONSTRAINTS
    
    """
    mocker.patch('ResSimpy.DataModelBaseClasses.DataObjectMixin.uuid4', return_value='uuid1')

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            '/path/fcs_file.fcs': fcs_file_contents,
            '/surface_file_01.dat': surface_file_contents,
            '/nexus_data/runcontrol.dat': runcontrol_contents}
                                        ).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)
    nexus_sim = get_fake_nexus_simulator(mocker, fcs_file_path='/path/fcs_file.fcs', mock_open=False)

    well_1_expected_constraint_1 = NexusConstraint(date='09/07/2024', name='well_1', max_surface_liquid_rate=3884.0,
                                                   max_surface_water_rate=0, unit_system=UnitSystem.ENGLISH,
                                                   date_format=DateFormat.DD_MM_YYYY,
                                                   start_date=start_date)

    well_1_expected_constraint_2 = NexusConstraint(date='23/08/2024', name='well_1', max_surface_oil_rate=123.4,
                                                   unit_system=UnitSystem.ENGLISH, date_format=DateFormat.DD_MM_YYYY,
                                                   start_date=start_date)

    well_2_expected_constraint_1 = NexusConstraint(date='23/08/2024', name='well_2', max_surface_oil_rate=123.4,
                                                   unit_system=UnitSystem.ENGLISH, date_format=DateFormat.DD_MM_YYYY,
                                                   start_date=start_date)

    well_2_expected_constraint_2 = NexusConstraint(date='15/10/2024', name='well_2', max_surface_liquid_rate=4567,
                                                   date_format=DateFormat.DD_MM_YYYY, unit_system=UnitSystem.ENGLISH,
                                                   start_date=start_date)

    # Act
    result = nexus_sim.network.constraints.get_all()

    # Assert
    assert result['well_1'] == [well_1_expected_constraint_1, well_1_expected_constraint_2]
    assert result['well_2'] == [well_2_expected_constraint_1, well_2_expected_constraint_2]


def test_load_constraints_deactivated_then_activated_differently(mocker: MockerFixture):
    # Arrange
    fcs_file_contents = '''
         RUN_UNITS ENGLISH
         DATEFORMAT DD/MM/YYYY
         RECURRENT_FILES
         RUNCONTROL /nexus_data/runcontrol.dat
         SURFACE Network 1  /surface_file_01.dat
         Wells Set 1 /wells.dat
         '''
    runcontrol_contents = '''START 24/09/2021'''

    surface_file_contents = """
WELLS
NAME    STREAM    IBAT    IPVT
well_1  PRODUCER    1    1
ENDWELLS

CONSTRAINTS
well_1 DEACTIVATE
ENDCONSTRAINTS

CONSTRAINTS
    well_1	 QWSMAX 1234
ENDCONSTRAINTS

TIME 25/07/2026
ACTIVATE
CONNECTION
well_1
ENDACTIVATE

TIME 26/07/2026
CONSTRAINTS
    well_1	 QWSMAX 4321
ENDCONSTRAINTS

"""
    wellspec_file_contents = """
        WELLSPEC well_1
        IW JW L RADW KHMULT SKIN
        1  2  3  4.5 NA 00.00
    """

    mocker.patch('ResSimpy.DataModelBaseClasses.DataObjectMixin.uuid4', return_value='uuid1')

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            '/path/fcs_file.fcs': fcs_file_contents,
            '/surface_file_01.dat': surface_file_contents,
            '/nexus_data/runcontrol.dat': runcontrol_contents,
            '/wells.dat': wellspec_file_contents}
                                        ).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)
    nexus_sim = get_fake_nexus_simulator(mocker, fcs_file_path='/path/fcs_file.fcs', mock_open=False)

    well_1_expected_constraint_0 = NexusConstraint(date='24/09/2021', start_date='24/09/2021', name='well_1',
                                                   active_node=False, date_format=DateFormat.DD_MM_YYYY,
                                                   unit_system=UnitSystem.ENGLISH, max_surface_water_rate=1234.0)

    well_1_expected_constraint_1 = NexusConstraint(date='26/07/2026', start_date='24/09/2021', name='well_1',
                                                   active_node=None, max_surface_water_rate=4321,
                                                   date_format=DateFormat.DD_MM_YYYY, unit_system=UnitSystem.ENGLISH)

    # Act
    constraints = nexus_sim.network.constraints.get_all()['well_1']
    result = NetworkOperationsMixIn.resolve_same_named_objects_constraints(constraints)
    ordered_result = sorted(result, key=lambda x: x.iso_date)

    # Assert
    assert len(ordered_result) == 2
    assert ordered_result[0] == well_1_expected_constraint_0
    assert ordered_result[1] == well_1_expected_constraint_1

def test_constraints_to_string_for_date():
    # Arrange
    constraints_props = ({'date': '01/01/2019', 'name': 'well1', 'max_surface_liquid_rate': 3884.0,
      'max_surface_water_rate': 0, 'unit_system': UnitSystem.ENGLISH, 'max_pressure': 3000},
     {'date': '01/01/2019', 'name': 'well2', 'max_surface_water_rate': 0.0, 'max_reverse_surface_liquid_rate': 10000.0,
      'max_surface_liquid_rate': 15.5, 'unit_system': UnitSystem.ENGLISH, 'min_pressure': 1200},
     {'date': '01/01/2020', 'name': 'well1', 'max_surface_liquid_rate': 5000.0, 'unit_system': UnitSystem.ENGLISH},
     {'date': '01/01/2020', 'name': 'well2', 'max_surface_water_rate': 0.0, 'max_surface_liquid_rate': 20.5,
      'unit_system': UnitSystem.ENGLISH}
     )
    constraints = {'well1': [NexusConstraint(constraint, date_format=DateFormat.MM_DD_YYYY, start_date='01/01/2019')
                             for constraint in constraints_props if constraint['name'] == 'well1'],
                   'well2': [NexusConstraint(constraint, date_format=DateFormat.MM_DD_YYYY, start_date='01/01/2019')
                             for constraint in constraints_props if constraint['name'] == 'well2']}
    
    # create a dummy constraints object to call the method on
    nexus_constraints = NexusConstraints(None, None) 
    nexus_constraints._constraints = constraints
    
    date_for_string_1 = ISODateTime(year=2019, month=1, day=1)
    date_for_string_2 = ISODateTime(year=2020, month=1, day=1)
    
    expected_result_1 = """CONSTRAINTS
well1 PMAX 3000 QWSMAX 0 QLIQSMAX 3884.0
well2 PMIN 1200 QWSMAX 0.0 QLIQSMAX 15.5 QLIQSMAX- 10000.0
ENDCONSTRAINTS
"""

    expected_result_2 = """CONSTRAINTS
well1 QLIQSMAX 5000.0
well2 QWSMAX 0.0 QLIQSMAX 20.5
ENDCONSTRAINTS
"""
    # Act
    result_1 = nexus_constraints.to_string_for_date(date_for_string_1)
    result_2 = nexus_constraints.to_string_for_date(date_for_string_2)
    
    # Assert
    assert result_1 == expected_result_1
    assert result_2 == expected_result_2
