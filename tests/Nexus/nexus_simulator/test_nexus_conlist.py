from ResSimpy.Nexus.DataModels.Network.NexusConList import NexusConList
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
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
        
    