import pytest

from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.NexusWellList import NexusWellList
from ResSimpy.Nexus.nexus_collect_tables import collect_all_tables_to_objects
from ResSimpy.Nexus.nexus_load_well_list import load_well_list_from_table, load_well_lists


class TestNexusWellList:
    file_content = '''TIME 01/01/2020
WELLLIST well_list_name 
ADD
wellname_1 
wellname_2
! comment

wellname_n
ENDWELLLIST'''

    def test_nexus_welllist_add(self):
        # Arrange
        existing_welllist = NexusWellList(name='well_list_name', wells=['test_well', 'test_well2'],
                                          date='01/01/2019')
        expected_welllist = NexusWellList(name='well_list_name', wells=['test_well', 'test_well2',
        'wellname_1', 'wellname_2', 'wellname_n'],
                                          date='01/01/2020')
        file_as_list = self.file_content.splitlines()

        # Act
        welllist = load_well_list_from_table(well_list_as_list_str=file_as_list, current_date='01/01/2020',
                                             well_list_name='well_list_name',
                                             previous_well_list=existing_welllist)

        # Assert
        assert welllist == expected_welllist

    def test_nexus_welllist_remove(self):
        # Arrange
        existing_welllist = NexusWellList(name='well_list_name', wells=['test_well', 'test_well2'],
                                          date='01/01/2019')
        expected_welllist = NexusWellList(name='well_list_name', wells=['test_well'],
                                          date='01/01/2020')
        file_as_list = '''TIME 01/01/2020
        WELLLIST well_list_name
        REMOVE
        test_well2
        ENDWELLLIST'''.splitlines()

        # Act
        welllist = load_well_list_from_table(well_list_as_list_str=file_as_list, current_date='01/01/2020',
                                             well_list_name='well_list_name',
                                             previous_well_list=existing_welllist)

        assert welllist == expected_welllist

    def test_nexus_welllist_clear(self):
        # Arrange
        existing_welllist = NexusWellList(name='well_list_name', wells=['test_well', 'test_well2'],
                                          date='01/01/2019')
        expected_welllist = NexusWellList(name='well_list_name', wells=['wellname_1', 'wellname_2', 'wellname_3'],
                                          date='01/01/2020')
        file_as_list = '''TIME 01/01/2020
        WELLLIST well_list_name
        CLEAR
        ADD
        wellname_1
        wellname_2
        
        wellname_3
        ENDWELLLIST'''.splitlines()

        # Act
        welllist = load_well_list_from_table(well_list_as_list_str=file_as_list, current_date='01/01/2020',
                                             well_list_name='well_list_name',
                                             previous_well_list=existing_welllist)

        assert welllist == expected_welllist

    def test_nexus_welllist_no_previous(self):
        # Arrange
        expected_welllist = NexusWellList(name='well_list_name', wells=['wellname_1', 'wellname_2', 'wellname_3'],
                                          date='01/01/2020')
        file_as_list = '''TIME 01/01/2020
        WELLLIST well_list_name
        CLEAR
        ADD
        wellname_1
        wellname_2
        
        wellname_3
        ENDWELLLIST'''.splitlines()

        # Act
        welllist = load_well_list_from_table(well_list_as_list_str=file_as_list, current_date='01/01/2020',
                                             well_list_name='well_list_name')

        assert welllist == expected_welllist

    def test_nexus_wellllist_empty(self):
        # Arrange
        expected_welllist = NexusWellList(name='well_list_name', wells=[],
                                          date='01/01/2020')
        file_as_list = '''TIME 01/01/2020
        WELLLIST well_list_name
        CLEAR
        ENDWELLLIST'''.splitlines()

        # Act
        welllist = load_well_list_from_table(well_list_as_list_str=file_as_list, current_date='01/01/2020',
                                             well_list_name='well_list_name')

        assert welllist == expected_welllist

    def test_load_several_welllists(self):
        # Arrange
        expected_welllists = [
            NexusWellList(name='well_list_name', wells=['wellname_1', 'wellname_2', 'wellname_3'],
                          date='01/01/2020'),
            NexusWellList(name='well_list_name_2', wells=['wellname_4', 'wellname_5', 'wellname_6'],
                            date='01/01/2020'),
            NexusWellList(name='well_list_name', wells=['wellname_2', 'wellname_3'],
                          date='01/01/2023'),
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
        )
        # Assert
        assert nexus_obj_dict['WELLLIST'] == expected_welllists

