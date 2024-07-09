from pytest_mock import MockerFixture

from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.DataModels.Network.NexusConList import NexusConList
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.NexusWellList import NexusWellList
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.Nexus.nexus_collect_tables import collect_all_tables_to_objects
from ResSimpy.Nexus.nexus_load_list_table import load_table_to_lists


class TestNexusConList:
    file_content = '''TIME 01/01/2020
CONLIST well_list_name 
ADD
well_1 
terminal_to_sink
! comment
ENDCONLIST
'''

    def test_nexus_conlist_add(self):
        # Arrange
        existing_conlist = NexusConList(name='well_list_name', elements_in_the_list=['test_well', 'test_well2'],
                                        date='01/01/2019', date_format=DateFormat.DD_MM_YYYY)
        expected_conlist = NexusConList(name='well_list_name', elements_in_the_list=['test_well', 'test_well2',
                                                                            'well_1', 'terminal_to_sink'],
                                        date='01/01/2020', date_format=DateFormat.DD_MM_YYYY)
        file_as_list = self.file_content.splitlines()
        
        row_object = NexusConList
        
        # Act
        welllist = load_table_to_lists(file_as_list=file_as_list,
                                       row_object=NexusConList,
                                       current_date='01/01/2020',
                                       previous_lists=[existing_conlist],
                                       date_format=DateFormat.DD_MM_YYYY,
                                       table_header='CONLIST',
                                       table_start_index=0)[0][0]

        # Assert
        assert welllist == expected_conlist
        
    def test_nexus_conlist_and_welllist(self, mocker: MockerFixture):
        # Arrange
        mocker.patch('ResSimpy.DataObjectMixin.uuid4', return_value='uuid_1')
        expected_welllists = [
            NexusWellList(name='well_list_name', elements_in_the_list=['wellname_1', 'wellname_2', 'wellname_3'],
                          date='01/01/2020', date_format=DateFormat.MM_DD_YYYY),
            NexusWellList(name='well_list_name', elements_in_the_list=['wellname_2', 'wellname_3'],
                          date='01/01/2023', date_format=DateFormat.MM_DD_YYYY),
        ]
        expected_conlists = [
            NexusConList(name='conlist_name', elements_in_the_list=['wellcon_1', 'wellcon_3', 'wellname_1'],
                          date='01/01/2020', date_format=DateFormat.MM_DD_YYYY),
            NexusConList(name='conlist_name', elements_in_the_list=['wellcon_1', 'wellname_1'],
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
        CONLIST conlist_name
        ADD
        wellcon_1
        wellcon_3
        ! comment
        
        wellname_1
        ENDCONLIST
        TIME 01/01/2023
        WELLLIST well_list_name
        REMOVE
        wellname_1
        ENDWELLLIST
        
        CONLIST conlist_name    !Comment
        REMOVE
        wellcon_3
        ENDCONLIST
        '''.splitlines()

        nexus_file = NexusFile(location='', file_content_as_list=file_as_list)

        # Act
        nexus_obj_dict, _ = collect_all_tables_to_objects(
            nexus_file=nexus_file, table_object_map={'WELLLIST': NexusWellList,
                                                     'CONLIST': NexusConList},
            start_date='01/01/2019',
            default_units=UnitSystem.ENGLISH,
            date_format=DateFormat.MM_DD_YYYY
        )
        # Assert
        assert nexus_obj_dict['WELLLIST'] == expected_welllists
        assert nexus_obj_dict['CONLIST'] == expected_conlists
