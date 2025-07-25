from pytest_mock import MockerFixture
import pandas as pd

from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.DataModels.Network.NexusWellLists import NexusWellLists
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.NexusWellList import NexusWellList
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.Nexus.NexusNetwork import NexusNetwork
from ResSimpy.Nexus.nexus_collect_tables import collect_all_tables_to_objects
from ResSimpy.Nexus.nexus_load_list_table import load_list_from_table
from ResSimpy.Time.ISODateTime import ISODateTime
from tests.utility_for_tests import get_fake_nexus_simulator


class TestNexusWellList:
    file_content = '''TIME 01/01/2020
WELLLIST well_list_name 
ADD
wellname_1 
wellname_2
! comment

wellname_n
ENDWELLLIST'''
    well_list = NexusWellList(name='well_list_name', elements_in_the_list=['wellname_1', 'wellname_2', 'wellname_3'],
                              date='01/01/2020', date_format=DateFormat.DD_MM_YYYY)
    well_list2 = NexusWellList(name='well_list_name_2',
                               elements_in_the_list=['wellname_4', 'wellname_5', 'wellname_6'],
                               date='01/01/2020', date_format=DateFormat.DD_MM_YYYY)
    well_list3 = NexusWellList(name='well_list_name',
                               elements_in_the_list=['wellname_2', 'wellname_3'],
                               date='01/01/2023', date_format=DateFormat.DD_MM_YYYY)
    well_list4 = NexusWellList(name='well_list_name_2',
                               elements_in_the_list=['wellname_4', 'wellname_5', 'wellname_6'],
                               date='01/02/2023', date_format=DateFormat.DD_MM_YYYY)

    def test_nexus_welllist_add(self):
        # Arrange
        existing_welllist = NexusWellList(name='well_list_name', elements_in_the_list=['test_well', 'test_well2'],
                                          date='01/01/2019', date_format=DateFormat.DD_MM_YYYY)
        expected_welllist = NexusWellList(name='well_list_name', elements_in_the_list=['test_well', 'test_well2',
                                                                                       'wellname_1', 'wellname_2',
                                                                                       'wellname_n'],
                                          date='01/01/2020', date_format=DateFormat.DD_MM_YYYY)
        file_as_list = self.file_content.splitlines()

        # Act
        welllist = load_list_from_table(table_as_list_str=file_as_list, current_date='01/01/2020',
                                        list_name='well_list_name',
                                        previous_list_object=existing_welllist, date_format=DateFormat.DD_MM_YYYY,
                                        table_header='WELLLIST', row_object=NexusWellList)

        # Assert
        assert welllist == expected_welllist

    def test_nexus_welllist_remove(self):
        # Arrange
        existing_welllist = NexusWellList(name='well_list_name', elements_in_the_list=['test_well', 'test_well2'],
                                          date='01/01/2019', date_format=DateFormat.DD_MM_YYYY)
        expected_welllist = NexusWellList(name='well_list_name', elements_in_the_list=['test_well'],
                                          date='01/01/2020', date_format=DateFormat.DD_MM_YYYY)
        file_as_list = '''TIME 01/01/2020
        WELLLIST well_list_name
        REMOVE
        test_well2
        ENDWELLLIST'''.splitlines()

        # Act
        welllist = load_list_from_table(table_as_list_str=file_as_list, current_date='01/01/2020',
                                        list_name='well_list_name',
                                        previous_list_object=existing_welllist, date_format=DateFormat.DD_MM_YYYY,
                                        table_header='WELLLIST', row_object=NexusWellList)

        assert welllist == expected_welllist

    def test_nexus_welllist_clear(self):
        # Arrange
        existing_welllist = NexusWellList(name='well_list_name', elements_in_the_list=['test_well', 'test_well2'],
                                          date='01/01/2019', date_format=DateFormat.DD_MM_YYYY)
        expected_welllist = NexusWellList(name='well_list_name',
                                          elements_in_the_list=['wellname_1', 'wellname_2', 'wellname_3'],
                                          date='01/01/2020', date_format=DateFormat.DD_MM_YYYY)
        file_as_list = '''TIME 01/01/2020
        WELLLIST well_list_name
        CLEAR
        ADD
        wellname_1
        wellname_2
        
        wellname_3
        ENDWELLLIST'''.splitlines()

        # Act
        welllist = load_list_from_table(table_as_list_str=file_as_list, current_date='01/01/2020',
                                        list_name='well_list_name',
                                        previous_list_object=existing_welllist, date_format=DateFormat.DD_MM_YYYY,
                                        table_header='WELLLIST', row_object=NexusWellList)

        assert welllist == expected_welllist

    def test_nexus_welllist_no_previous(self):
        # Arrange
        expected_welllist = NexusWellList(name='well_list_name',
                                          elements_in_the_list=['wellname_1', 'wellname_2', 'wellname_3'],
                                          date='01/01/2020', date_format=DateFormat.DD_MM_YYYY)
        file_as_list = '''TIME 01/01/2020
        WELLLIST well_list_name
        CLEAR
        ADD
        wellname_1
        wellname_2
        
        wellname_3
        ENDWELLLIST'''.splitlines()

        # Act
        welllist = load_list_from_table(table_as_list_str=file_as_list, current_date='01/01/2020',
                                        list_name='well_list_name', date_format=DateFormat.DD_MM_YYYY,
                                        table_header='WELLLIST', row_object=NexusWellList)

        assert welllist == expected_welllist

    def test_nexus_wellllist_empty(self):
        # Arrange
        expected_welllist = NexusWellList(name='well_list_name', elements_in_the_list=[],
                                          date='01/01/2020', date_format=DateFormat.DD_MM_YYYY)
        file_as_list = '''TIME 01/01/2020
        WELLLIST well_list_name
        CLEAR
        ENDWELLLIST'''.splitlines()

        # Act
        welllist = load_list_from_table(table_as_list_str=file_as_list, current_date='01/01/2020',
                                        list_name='well_list_name', date_format=DateFormat.DD_MM_YYYY,
                                        table_header='WELLLIST', row_object=NexusWellList)

        assert welllist == expected_welllist

    def test_load_several_welllists(self, mocker: MockerFixture):
        # Arrange
        mocker.patch('ResSimpy.DataModelBaseClasses.DataObjectMixin.uuid4', return_value='uuid_1')
        expected_welllists = [
            NexusWellList(name='well_list_name', elements_in_the_list=['wellname_1', 'wellname_2', 'wellname_3'],
                          date='01/01/2020', date_format=DateFormat.MM_DD_YYYY),
            NexusWellList(name='well_list_name_2', elements_in_the_list=['wellname_4', 'wellname_5', 'wellname_6'],
                          date='01/01/2020', date_format=DateFormat.MM_DD_YYYY),
            NexusWellList(name='well_list_name', elements_in_the_list=['wellname_2', 'wellname_3'],
                          date='01/01/2023', date_format=DateFormat.MM_DD_YYYY),
        ]

        file_as_list = '''
        TIME 01/01/2020
        WELLLIST well_list_name
        ADD
        wellname_1
        wellname_2
        
        wellname_3
        ENDWELLLIST
        WELLLIST well_list_name_2
        ADD
        wellname_4
        wellname_5
        
        wellname_6
        ENDWELLLIST
        TIME 01/01/2023
        WELLLIST well_list_name
        REMOVE
        wellname_1
        ENDWELLLIST
        '''.splitlines()

        nexus_file = NexusFile(location='', file_content_as_list=file_as_list)

        # Act
        nexus_obj_dict, _ = collect_all_tables_to_objects(
            nexus_file=nexus_file, table_object_map={'WELLLIST': NexusWellList},
            start_date='01/01/2019',
            default_units=UnitSystem.ENGLISH,
            date_format=DateFormat.MM_DD_YYYY
        )
        # Assert
        assert nexus_obj_dict['WELLLIST'] == expected_welllists

    def test_get_by_name(self, mocker):
        # Arrange

        # get a mock network

        mock_nexus_network = mocker.MagicMock()
        well_lists = NexusWellLists(mock_nexus_network, well_lists=[self.well_list, self.well_list2, self.well_list3,
                                                                    self.well_list4])

        expected_result_1 = [self.well_list, self.well_list3]
        expected_result_2 = [self.well_list2, self.well_list4]
        # Act
        result = well_lists.get_all_by_name('well_list_name')
        result_2 = well_lists.get_all_by_name('well_list_name_2')
        # Assert
        assert result == expected_result_1
        assert result_2 == expected_result_2

    def test_get_all_by_name(self, mocker: MockerFixture):
        dummy_model = get_fake_nexus_simulator(mocker, mock_open=True)
        dummy_network = NexusNetwork(model=dummy_model, assume_loaded=True)

        welllists = [
            NexusWellList(name='well_list_name', elements_in_the_list=['wellname_1', 'wellname_2', 'wellname_3'],
                          date='01/01/2020',
                          date_format=DateFormat.DD_MM_YYYY),
            NexusWellList(name='well_list_name_2', elements_in_the_list=['wellname_4', 'wellname_5', 'wellname_6'],
                          date='01/01/2020',
                          date_format=DateFormat.DD_MM_YYYY),
            NexusWellList(name='well_list_name', elements_in_the_list=['wellname_2', 'wellname_3'], date='01/01/2023',
                          date_format=DateFormat.DD_MM_YYYY)]

        welllist = NexusWellLists(parent_network=dummy_network, well_lists=welllists)

        expected_result_1 = [
            NexusWellList(name='well_list_name', elements_in_the_list=['wellname_1', 'wellname_2', 'wellname_3'],
                          date='01/01/2020',
                          date_format=DateFormat.DD_MM_YYYY),
            NexusWellList(name='well_list_name', elements_in_the_list=['wellname_2', 'wellname_3'], date='01/01/2023',
                          date_format=DateFormat.DD_MM_YYYY)]

        # Act
        result = welllist.get_all_by_name('well_list_name')

        # Assert
        assert result == expected_result_1

    def test_welllist_get_df(self, mocker: MockerFixture):
        dummy_model = get_fake_nexus_simulator(mocker, mock_open=True)
        dummy_network = NexusNetwork(model=dummy_model, assume_loaded=True)

        welllists = [
            NexusWellList(name='well_list_name', elements_in_the_list=['wellname_1', 'wellname_2', 'wellname_3'],
                          date='01/01/2020',
                          date_format=DateFormat.DD_MM_YYYY),
            NexusWellList(name='well_list_name_2', elements_in_the_list=['wellname_4', 'wellname_5', 'wellname_6'],
                          date='01/01/2020',
                          date_format=DateFormat.DD_MM_YYYY),
            NexusWellList(name='well_list_name', elements_in_the_list=['wellname_2', 'wellname_3'], date='01/01/2023',
                          date_format=DateFormat.DD_MM_YYYY)]

        welllist = NexusWellLists(parent_network=dummy_network, well_lists=welllists)

        expected_result = pd.DataFrame(
            {'name': ['well_list_name'] * 3 + ['well_list_name_2'] * 3 + ['well_list_name'] * 2,
             'well': ['wellname_1', 'wellname_2', 'wellname_3',
                      'wellname_4', 'wellname_5', 'wellname_6',
                      'wellname_2', 'wellname_3'],
             'date': ['01/01/2020'] * 6 + ['01/01/2023'] * 2})
        # Act
        result = welllist.get_df()

        # Assert
        pd.testing.assert_frame_equal(result, expected_result)

    def test_add_then_remove_wells_from_welllist(self, mocker: MockerFixture):
        # Arrange
        mocker.patch('ResSimpy.DataModelBaseClasses.DataObjectMixin.uuid4', return_value='uuid_1')
        expected_welllists = [
            NexusWellList(name='some_wells', elements_in_the_list=['well_1'],
                          date='09/07/2024', date_format=DateFormat.DD_MM_YYYY),
            NexusWellList(name='some_wells', elements_in_the_list=['well_1', 'well_2'],
                          date='23/08/2024', date_format=DateFormat.DD_MM_YYYY),
            NexusWellList(name='some_wells', elements_in_the_list=['well_2'],
                          date='15/10/2024', date_format=DateFormat.DD_MM_YYYY),
        ]

        file_as_list = '''
    WELLLIST some_wells
    ADD
    well_1
    ENDWELLLIST

    TIME 23/08/2024

    WELLLIST some_wells
    ADD
    well_2
    ENDWELLLIST

    TIME 15/10/2024

    WELLLIST some_wells
    REMOVE
    well_1
    ENDWELLLIST
        '''.splitlines()

        nexus_file = NexusFile(location='', file_content_as_list=file_as_list)

        # Act
        nexus_obj_dict, _ = collect_all_tables_to_objects(
            nexus_file=nexus_file, table_object_map={'WELLLIST': NexusWellList},
            start_date='09/07/2024',
            default_units=UnitSystem.ENGLISH,
            date_format=DateFormat.DD_MM_YYYY
        )
        # Assert
        assert nexus_obj_dict['WELLLIST'] == expected_welllists

    def test_multiple_changes_same_date(self, mocker: MockerFixture):
        # Arrange
        mocker.patch('ResSimpy.DataModelBaseClasses.DataObjectMixin.uuid4', return_value='uuid_1')
        expected_welllists = [
            NexusWellList(name='some_wells', elements_in_the_list=['well_1'],
                          date='09/07/2024', date_format=DateFormat.DD_MM_YYYY),
            NexusWellList(name='some_wells', elements_in_the_list=['well_1', 'well_2'],
                          date='23/08/2024', date_format=DateFormat.DD_MM_YYYY),
            NexusWellList(name='some_wells', elements_in_the_list=['well_1', 'well_3'],
                          date='26/12/2024', date_format=DateFormat.DD_MM_YYYY),
        ]

        file_as_list = '''
    WELLLIST some_wells
    ADD
    well_1
    ENDWELLLIST

    TIME 23/08/2024

    WELLLIST some_wells
    ADD
    well_2
    ENDWELLLIST
        
    TIME 26/12/2024
    ! Multiple changes on the same date.
    WELLLIST some_wells
    REMOVE
    well_2
    ENDWELLLIST
    
    WELLLIST some_wells
    ADD
    well_3
    ENDWELLLIST
        '''.splitlines()

        nexus_file = NexusFile(location='', file_content_as_list=file_as_list)

        # Act
        nexus_obj_dict, _ = collect_all_tables_to_objects(
            nexus_file=nexus_file, table_object_map={'WELLLIST': NexusWellList},
            start_date='09/07/2024',
            default_units=UnitSystem.ENGLISH,
            date_format=DateFormat.DD_MM_YYYY
        )
        # Assert
        assert nexus_obj_dict['WELLLIST'] == expected_welllists

    def test_to_string_for_date(self, mocker):
        # Arrange

        # get a mock network

        mock_nexus_network = mocker.MagicMock()
        well_lists = NexusWellLists(mock_nexus_network, well_lists=[self.well_list, self.well_list2, self.well_list3,
                                                                    self.well_list4])
        
        date = ISODateTime(year=2020, month=1, day=1)
        
        expected_string = """WELLLIST well_list_name
CLEAR
ADD
wellname_1 wellname_2 wellname_3
ENDWELLLIST
WELLLIST well_list_name_2
CLEAR
ADD
wellname_4 wellname_5 wellname_6
ENDWELLLIST
"""
        # Act
        result = well_lists.to_string_for_date(date)

        # Assert
        assert result == expected_string
