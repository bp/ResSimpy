import os
import pytest
from ResSimpy.Nexus.DataModels.FcsFile import FcsNexusFile
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from tests.multifile_mocker import mock_multiple_files


def test_fcs_file(mocker):
    # Arrange
    fcs_content = '''DESC reservoir1
RUN_UNITS ENGLISH
DATEFORMAT DD/MM/YYYY
GRID_FILES
	 STRUCTURED_GRID nexus_data/mp2020_structured_grid_1_reg_update.dat
	 OPTIONS nexus_data/nexus_data/mp2020_ref_options_reg_update.dat'''

    fcs_path = '/root_folder/test_fcs.fcs'
    root_folder = '/root_folder'
    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            '/root_folder/test_fcs.fcs': fcs_content,
            }).return_value
        return mock_open
    mocker.patch("builtins.open", mock_open_wrapper)
    mocker.patch("os.path.isfile", lambda x: True)
    structured_grid_path = os.path.join(root_folder, 'nexus_data/mp2020_structured_grid_1_reg_update.dat')
    options_file_path = os.path.join(root_folder, 'nexus_data/nexus_data/mp2020_ref_options_reg_update.dat')
    expected_includes = [ structured_grid_path, options_file_path]
    expected_structured_grid_file = NexusFile(location=structured_grid_path,
                                              origin=fcs_path, include_locations=None,
                                              include_objects=None, file_content_as_list=None)
    
    expected_options_file = NexusFile(location=options_file_path,
                                      include_locations=None, origin=fcs_path, include_objects=None, file_content_as_list=None)
    expected_fcs_file = FcsNexusFile(location=fcs_path, origin=None,
                                     include_objects=[expected_structured_grid_file, expected_options_file],
                                     file_content_as_list=[
                                         'DESC reservoir1', 'RUN_UNITS ENGLISH', 'DATEFORMAT DD/MM/YYYY',
                                         'GRID_FILES', '	 STRUCTURED_GRID ', expected_structured_grid_file, '',
                                         '	 OPTIONS ', expected_options_file, '', ],
                                     structured_grid_file=expected_structured_grid_file,
                                     options_file=expected_options_file, include_locations=expected_includes,
                                     )

    # Act
    fcs_file = FcsNexusFile.generate_fcs_structure(fcs_path)
    # Assert
    assert fcs_file == expected_fcs_file
    assert fcs_file.structured_grid_file == expected_fcs_file.structured_grid_file


def test_fcs_file_multiple_methods(mocker):
    # Arrange
    fcs_content = '''DESC reservoir1
    RUN_UNITS ENGLISH
    DATEFORMAT DD/MM/YYYY
    INITIALIZATION_FILES
	 EQUIL Method 1 nexus_data/nexus_data/mp2017hm_ref_equil_01.dat
	 EQUIL Method 2 nexus_data/nexus_data/mp2017hm_ref_equil_02.dat
	 EQUIL Method 3 nexus_data/nexus_data/mp2017hm_ref_equil_03.dat'''
  
    fcs_path = 'test_fcs.fcs'
    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            'test_fcs.fcs': fcs_content,
            }).return_value
        return mock_open
    mocker.patch("builtins.open", mock_open_wrapper)
    mocker.patch("os.path.isfile", lambda x: True)
    expected_includes = ['nexus_data/nexus_data/mp2017hm_ref_equil_01.dat',
                         'nexus_data/nexus_data/mp2017hm_ref_equil_02.dat',
	                     'nexus_data/nexus_data/mp2017hm_ref_equil_03.dat', ]
    expected_equil_1 = NexusFile(location='nexus_data/nexus_data/mp2017hm_ref_equil_01.dat',
                                 origin=fcs_path, include_locations=None,
                                 include_objects=None, file_content_as_list=None)
    expected_equil_2 = NexusFile(location='nexus_data/nexus_data/mp2017hm_ref_equil_02.dat',
                                 origin=fcs_path, include_locations=None,
                                 include_objects=None, file_content_as_list=None)
    expected_equil_3 = NexusFile(location='nexus_data/nexus_data/mp2017hm_ref_equil_03.dat',
                                 origin=fcs_path, include_locations=None,
                                 include_objects=None, file_content_as_list=None)
    expected_fcs_file = FcsNexusFile(
        location=fcs_path, origin=None,
        include_objects=[expected_equil_1, expected_equil_2, expected_equil_3],
        file_content_as_list=[
            'DESC reservoir1', '    RUN_UNITS ENGLISH', '    DATEFORMAT DD/MM/YYYY',
            '    INITIALIZATION_FILES', '	 EQUIL Method 1 ', expected_equil_1, '',
            '	 EQUIL Method 2 ', expected_equil_2, '', '	 EQUIL Method 3 ',
            expected_equil_3, ''],
        equil_files={1: expected_equil_1, 2: expected_equil_2, 3: expected_equil_3},
        include_locations=expected_includes,
    )
    # Act
    result = FcsNexusFile.generate_fcs_structure(fcs_path)
    # Assert
    assert result == expected_fcs_file
    
    
def test_fcs_file_all_methods(mocker):
    # Currently this test doesn't cover ensuring that the include file object gets into the fcs file.
    # Arrange
    fcs_content = '''DESC reservoir1
    RUN_UNITS ENGLISH
    DATEFORMAT DD/MM/YYYY
    INITIALIZATION_FILES
	 EQUIL Method 1 nexus_data/nexus_data/mp2017hm_ref_equil_01.dat
	 EQUIL Method 2 nexus_data/nexus_data/mp2017hm_ref_equil_02.dat
    STRUCTURED_GRID nexus_data/mp2020_structured_grid_1_reg_update.dat
	 OPTIONS nexus_data/nexus_data/mp2020_ref_options_reg_update.dat
     INCLUDE wells.inc
     HYD METHOd 3 hyd.dat'''
    include_contents = 'WELLS SET 1 wells.dat'
    
    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            'test_fcs.fcs': fcs_content,
            'wells.inc': include_contents,
            }).return_value
        return mock_open
    mocker.patch("builtins.open", mock_open_wrapper)
    mocker.patch("os.path.isfile", lambda x: True)
    fcs_path = 'test_fcs.fcs'
    expected_includes = ['nexus_data/nexus_data/mp2017hm_ref_equil_01.dat',
                         'nexus_data/nexus_data/mp2017hm_ref_equil_02.dat',
                         'nexus_data/mp2020_structured_grid_1_reg_update.dat',
                         'nexus_data/nexus_data/mp2020_ref_options_reg_update.dat',
                         #'wells.inc',  # TODO fix this test to ensure the include files get included here 
                         'wells.dat',
                         'hyd.dat']
    expected_equil_1 = NexusFile(location='nexus_data/nexus_data/mp2017hm_ref_equil_01.dat',
                                 origin=fcs_path, include_locations=None,
                                 include_objects=None, file_content_as_list=None)
    expected_equil_2 = NexusFile(location='nexus_data/nexus_data/mp2017hm_ref_equil_02.dat',
                                 origin=fcs_path, include_locations=None,
                                 include_objects=None, file_content_as_list=None)
    expected_structured_grid_file = NexusFile(location='nexus_data/mp2020_structured_grid_1_reg_update.dat',
                                              origin=fcs_path, include_locations=None,
                                              include_objects=None, file_content_as_list=None)
    expected_options_file = NexusFile(location='nexus_data/nexus_data/mp2020_ref_options_reg_update.dat', include_locations=None,
                                      origin=fcs_path, include_objects=None, file_content_as_list=None)
    expected_wells_file = NexusFile(location='wells.dat', origin=fcs_path, include_locations=None, include_objects=None,
                                    file_content_as_list=None)
    expected_hyd_method_file = NexusFile(location='hyd.dat', origin=fcs_path, include_locations=None,
                                         include_objects=None, file_content_as_list=None)

    equil_files = {1: expected_equil_1, 2: expected_equil_2, }
    include_objects = [expected_equil_1, expected_equil_2, expected_structured_grid_file, expected_options_file,
                       expected_wells_file, expected_hyd_method_file]
    expected_fcs_contents_as_list = ['DESC reservoir1',
                                     '    RUN_UNITS ENGLISH',
                                     '    DATEFORMAT DD/MM/YYYY',
                                     '    INITIALIZATION_FILES',
                                     '	 EQUIL Method 1 ',
                                     expected_equil_1,
                                     '',
                                     '	 EQUIL Method 2 ',
                                     expected_equil_2,
                                     '',
                                     '    STRUCTURED_GRID ',
                                     expected_structured_grid_file,
                                     '',
                                     '	 OPTIONS ',
                                     expected_options_file,
                                     '',
                                     '     INCLUDE ',
                                     'WELLS SET 1 ',
                                     expected_wells_file,
                                     '',
                                     '     HYD METHOd 3 ',
                                     expected_hyd_method_file,
                                     '',
                                     ]
    expected_fcs_file = FcsNexusFile(location=fcs_path, origin=None, include_objects=include_objects,
                                     equil_files=equil_files, structured_grid_file=expected_structured_grid_file, 
                                     options_file=expected_options_file, well_files={1: expected_wells_file},
                                     hyd_files={3: expected_hyd_method_file},
                                     file_content_as_list=expected_fcs_contents_as_list, include_locations=expected_includes)
    # Act
    result = FcsNexusFile.generate_fcs_structure(fcs_file_path=fcs_path)
    
    # Assert
    assert result == expected_fcs_file
    
    
@pytest.mark.parametrize("input_line, expected_result", [
    ('STRUCTURED_GRID nexus_data/mp2020_structured_grid_1_reg_update.dat\n',
     ['STRUCTURED_GRID ', 'NEXUSFILE', '']),
    ('STRUCTURED_GRID nexus_data/mp2020_structured_grid_1_reg_update.dat !comment',
     ['STRUCTURED_GRID ', 'NEXUSFILE', ' !comment']),
    ('STRUCTURED_GRID nexus_data/mp2020_structured_grid_1_reg_update.dat !nexus_data/mp2020_structured_grid_1_reg_update.dat',
     ['STRUCTURED_GRID ', 'NEXUSFILE', ' !nexus_data/mp2020_structured_grid_1_reg_update.dat']),
    ('\t    STRUCTURED_GRID \t  nexus_data/mp2020_structured_grid_1_reg_update.dat',
     ['\t    STRUCTURED_GRID \t  ', 'NEXUSFILE', '']),
    ], ids=['basic', 'with_comment', 'with filename in comment', 'weird tabbing'])
def test_line_as_nexus_list(input_line, expected_result):
    # Arrange
    path = "nexus_data/mp2020_structured_grid_1_reg_update.dat"
    structured_grid_file = NexusFile(location=path, origin=None, include_locations=None,
                                     include_objects=None, file_content_as_list=None)
    expected_result = [x if x != 'NEXUSFILE' else structured_grid_file for x in expected_result]
    # Act
    result = FcsNexusFile.line_as_nexus_list(input_line, path, structured_grid_file)

    # Assert
    assert result == expected_result


def test_get_full_network(mocker):
    # Arrange
    fcs_content = '''DESC reservoir1
    RUN_UNITS ENGLISH
    DATEFORMAT DD/MM/YYYY
    INITIALIZATION_FILES
	 EQUIL Method 1 nexus_data/nexus_data/mp2017hm_ref_equil_01.dat
	 EQUIL Method 2 nexus_data/nexus_data/mp2017hm_ref_equil_02.dat
    STRUCTURED_GRID nexus_data/mp2020_structured_grid_1_reg_update.dat
	 OPTIONS nexus_data/nexus_data/mp2020_ref_options_reg_update.dat
     INCLUDE wells.inc
     HYD METHOd 3 hyd.dat'''
    include_contents = 'WELLS SET 1 wells.dat'

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            'test_fcs.fcs': fcs_content,
            'wells.inc': include_contents,
            }).return_value
        return mock_open
    mocker.patch("builtins.open", mock_open_wrapper)
    mocker.patch("os.path.isfile", lambda x: True)
    fcs_path = 'test_fcs.fcs'

    expected_to_list = [
        'test_fcs.fcs',
        'nexus_data/nexus_data/mp2017hm_ref_equil_01.dat',
        'nexus_data/nexus_data/mp2017hm_ref_equil_01.dat',
        'nexus_data/nexus_data/mp2017hm_ref_equil_02.dat',
        'nexus_data/nexus_data/mp2017hm_ref_equil_02.dat',
        'nexus_data/mp2020_structured_grid_1_reg_update.dat',
        'nexus_data/mp2020_structured_grid_1_reg_update.dat',
        'nexus_data/nexus_data/mp2020_ref_options_reg_update.dat',
        'nexus_data/nexus_data/mp2020_ref_options_reg_update.dat',
        'wells.dat',
        'wells.dat',
        'hyd.dat',
        'hyd.dat',
        ]

    expected_from_list = [
        None,
        'test_fcs.fcs',
        'test_fcs.fcs',
        'test_fcs.fcs',
        'test_fcs.fcs',
        'test_fcs.fcs',
        'test_fcs.fcs',
        'test_fcs.fcs',
        'test_fcs.fcs',
        'test_fcs.fcs',
        'test_fcs.fcs',
        'test_fcs.fcs',
        'test_fcs.fcs',
    ]

    equil1 = NexusFile(location='nexus_data/nexus_data/mp2017hm_ref_equil_01.dat',
                       origin=fcs_path, include_locations=None,
                       include_objects=None, file_content_as_list=None)
    equil_2 = NexusFile(location='nexus_data/nexus_data/mp2017hm_ref_equil_02.dat',
                        origin=fcs_path, include_locations=None,
                        include_objects=None, file_content_as_list=None)
    structured_grid_file = NexusFile(location='nexus_data/mp2020_structured_grid_1_reg_update.dat',
                                     origin=fcs_path, include_locations=None,
                                     include_objects=None, file_content_as_list=None)
    options_file = NexusFile(location='nexus_data/nexus_data/mp2020_ref_options_reg_update.dat', include_locations=None,
                             origin=fcs_path, include_objects=None, file_content_as_list=None)
    wells_file = NexusFile(location='wells.dat', origin=fcs_path, include_locations=None, include_objects=None,
                           file_content_as_list=None)
    hyd_method_file = NexusFile(location='hyd.dat', origin=fcs_path, include_locations=None,
                                include_objects=None, file_content_as_list=None)

    equil_files = {1: equil1, 2: equil_2, }
    include_objects = [equil1, equil_2, structured_grid_file, options_file,
                       wells_file, hyd_method_file]
    fcs_contents_as_list = ['DESC reservoir1',
                            '    RUN_UNITS ENGLISH',
                            '    DATEFORMAT DD/MM/YYYY',
                            '    INITIALIZATION_FILES',
                            '	 EQUIL Method 1 ',
                            equil1,
                            '',
                            '	 EQUIL Method 2 ',
                            equil_2,
                            '',
                            '    STRUCTURED_GRID ',
                            structured_grid_file,
                            '',
                            '	 OPTIONS ',
                            options_file,
                            '',
                            '     ',
                            'WELLS SET 1 ',
                            wells_file,
                            '',
                            '',
                            '     HYD METHOd 3 ',
                            hyd_method_file,
                            '',
                            ]
    compiled_fcs_file = FcsNexusFile(location=fcs_path, origin=None, include_objects=include_objects,
                                     equil_files=equil_files, structured_grid_file=structured_grid_file, 
                                     options_file=options_file, well_files={1: wells_file},
                                     hyd_files={3: hyd_method_file},
                                     file_content_as_list=fcs_contents_as_list, include_locations=[])

    # Act
    from_list, to_list = compiled_fcs_file.get_full_network()

    # Assert
    assert to_list == expected_to_list
    assert from_list == expected_from_list
