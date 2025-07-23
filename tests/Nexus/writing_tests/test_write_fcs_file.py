from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.DataModels.FcsFile import FcsNexusFile
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat


def test_fcs_file_to_string(mocker):
    mocker.patch("os.path.isfile", lambda x: True)
    fcs_path = 'test_fcs.fcs'
    equil_1 = NexusFile(location='nexus_data/nexus_data/ref_equil_01.dat',
                        origin=fcs_path, include_locations=None,
                        include_objects=None, file_content_as_list=None)
    equil_2 = NexusFile(location='nexus_data/nexus_data/ref_equil_02.dat',
                        origin=fcs_path, include_locations=None,
                        include_objects=None, file_content_as_list=None)
    equil_3 = NexusFile(location='nexus_data/nexus_data/ref_equil_03.dat',
                        origin=fcs_path, include_locations=None,
                        include_objects=None, file_content_as_list=None)
    structured_grid_file = NexusFile(location='nexus_data/structured_grid_1_reg_update.dat',
                                     origin=fcs_path, include_locations=None,
                                     include_objects=None, file_content_as_list=None)
    options_file = NexusFile(location='nexus_data/nexus_data/ref_options_reg_update.dat',
                             include_locations=None,
                             origin=fcs_path, include_objects=None, file_content_as_list=None)
    wells_file_1 = NexusFile(location='wells_1.dat', origin=fcs_path, include_locations=None, include_objects=None,
                           file_content_as_list=None)
    wells_file_2 = NexusFile(location='wells_2.dat', origin=fcs_path, include_locations=None, include_objects=None,
                            file_content_as_list=None)
    hyd_method_file = NexusFile(location='hyd.dat', origin=fcs_path, include_locations=None,
                                include_objects=None, file_content_as_list=None)

    runcontrol_file = NexusFile(location='nexus_data/runcontrol.dat', origin=fcs_path,
                                include_locations=None, include_objects=None, file_content_as_list=None)
    
    surface_network_file = NexusFile(location='nexus_data/nexus_data/surface.dat',
                                        origin=fcs_path, include_locations=None,
                                        include_objects=None, file_content_as_list=None)
    
    rock_file = NexusFile(location='nexus_data/rock_1.dat', origin=fcs_path,
                            include_locations=None, include_objects=None, file_content_as_list=None)
    relperm_file = NexusFile(location='nexus_data/relperm_1.dat', origin=fcs_path,
                            include_locations=None, include_objects=None, file_content_as_list=None)
    
    pvt_file_1 = NexusFile(location='nexus_data/pvt_1.dat', origin=fcs_path,
                            include_locations=None, include_objects=None, file_content_as_list=None)
    pvt_file_2 = NexusFile(location='nexus_data/pvt_2.dat', origin=fcs_path,
                            include_locations=None, include_objects=None, file_content_as_list=None)
    
    water_file_1 = NexusFile(location='nexus_data/water_1.dat', origin=fcs_path,
                            include_locations=None, include_objects=None, file_content_as_list=None)
    water_file_2 = NexusFile(location='nexus_data/water_2.dat', origin=fcs_path,
                            include_locations=None, include_objects=None, file_content_as_list=None)
    
    
    equil_files = {1: equil_1, 2: equil_2, 3: equil_3}

    # fcs to_string method shouldn't depend on the following:
    include_objects = []
    fcs_contents_as_list = []
    include_locations = []
    fcs_file = FcsNexusFile(location=fcs_path, origin=None, include_objects=include_objects,
                            equil_files=equil_files, structured_grid_file=structured_grid_file,
                            runcontrol_file=runcontrol_file, surface_files={1: surface_network_file},
                            options_file=options_file, well_files={1: wells_file_1, 2: wells_file_2},
                            hyd_files={3: hyd_method_file}, pvt_files={1: pvt_file_1, 2: pvt_file_2},
                            water_files={1: water_file_1, 2: water_file_2},
                            rock_files={1: rock_file}, relperm_files={1: relperm_file},
                            file_content_as_list=fcs_contents_as_list,
                            include_locations=include_locations)
    expected_string = """DESC Model created with ResSimpy
RUN_UNITS ENGLISH
DEFAULT_UNITS METBAR
DATEFORMAT DD/MM/YYYY

GRID_FILES
    STRUCTURED_GRID nexus_data/structured_grid_1_reg_update.dat
    OPTIONS nexus_data/nexus_data/ref_options_reg_update.dat

INITIALIZATION_FILES
    EQUIL METHOD 1 nexus_data/nexus_data/ref_equil_01.dat
    EQUIL METHOD 2 nexus_data/nexus_data/ref_equil_02.dat
    EQUIL METHOD 3 nexus_data/nexus_data/ref_equil_03.dat

ROCK_FILES
    ROCK METHOD 1 nexus_data/rock_1.dat
    RELPM METHOD 1 nexus_data/relperm_1.dat

PVT_FILES
    PVT METHOD 1 nexus_data/pvt_1.dat
    PVT METHOD 2 nexus_data/pvt_2.dat
    WATER METHOD 1 nexus_data/water_1.dat
    WATER METHOD 2 nexus_data/water_2.dat

RECURRENT_FILES
    RUNCONTROL nexus_data/runcontrol.dat
    WELLS SET 1 wells_1.dat
    WELLS SET 2 wells_2.dat
    SURFACE NETWORK 1 nexus_data/nexus_data/surface.dat

NET_METHOD_FILES
    HYD METHOD 3 hyd.dat
"""

    # Act
    result = fcs_file.to_string(dateformat=DateFormat.DD_MM_YYYY, run_units=UnitSystem.ENGLISH,
                                default_units=UnitSystem.METBAR)

    # Assert
    assert result == expected_string
