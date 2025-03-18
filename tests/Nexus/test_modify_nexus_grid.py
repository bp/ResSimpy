import os
from ResSimpy.DataModelBaseClasses.GridArrayDefinition import GridArrayDefinition
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.StructuredGrid.NexusGrid import NexusGrid
from tests.multifile_mocker import mock_multiple_files
from tests.utility_for_tests import uuid_side_effect

class TestModifyNexusGrid:
    def setup_method(self, mocker):
        self.grid_text = """! Grid dimensions
        NX NY NZ
        1 2 3
        test string
        DUMMY VALUE
        ! comment
        !dummy text

        other text
        NETGRS VALUE
        INCLUDE  /path_to_netgrs_file/net_to_gross.inc

        LIST

        POROSITY VALUE
        !ANOTHER COMMENT
        INCLUDE path/to/porosity.inc
        KX CON
        25.2
        """
        self.new_grid_array_definition = GridArrayDefinition(value='/new_path_to_netgrs_file/new_net_to_gross_file.inc',
                                                             modifier='VALUE')

    def test_load_grid_with_ids(self, mocker):
        # mock uuid
        mocker.patch('ResSimpy.DataModelBaseClasses.GridArrayDefinition.uuid4',
                     side_effect=uuid_side_effect())

        def mock_open_wrapper(filename, mode):
            mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
                'test_location/grid.dat': self.grid_text,
                '/path_to_netgrs_file/net_to_gross.inc': '',
                'path/to/porosity.inc': '',
                os.path.join('test_location', 'path/to/porosity.inc'): '',
            }).return_value
            return mock_open

        mocker.patch("builtins.open", mock_open_wrapper)

        grid_nexus_file = NexusFile.generate_file_include_structure(file_path='test_location/grid.dat')

        grid = NexusGrid(model_unit_system=UnitSystem.METRIC,
                         grid_nexus_file=grid_nexus_file)
        expected_netgrs = GridArrayDefinition(value='/path_to_netgrs_file/net_to_gross.inc',
                                              absolute_path='/path_to_netgrs_file/net_to_gross.inc',
                                              modifier='VALUE')

        expected_porosity = GridArrayDefinition(value='path/to/porosity.inc',
                                                absolute_path=os.path.join('test_location', 'path/to/porosity.inc'),
                                                modifier='VALUE')
        expected_kx = GridArrayDefinition(value='25.2', modifier='CON')

        # uuid number based on how far down the attributes of the NexusGrid the array is
        expected_netgrs_id = 'uuid0'
        expected_porosity_id = 'uuid1'
        expected_kx_id = 'uuid6'

        expected_object_locs = {'uuid0': [9, 10],
                                'uuid1': [14, 16],
                                'uuid6': [17, 18]}

        # Assert
        assert grid.netgrs == expected_netgrs
        assert grid.netgrs.id == expected_netgrs_id
        assert grid.porosity == expected_porosity
        assert grid.porosity.id == expected_porosity_id
        assert grid.kx == expected_kx
        assert grid.kx.id == expected_kx_id

        assert grid_nexus_file.object_locations == expected_object_locs

    def test_nexus_grid_remove_basic_test(self, mocker):
        # mock uuid
        mocker.patch('ResSimpy.DataModelBaseClasses.GridArrayDefinition.uuid4',
                     side_effect=uuid_side_effect())
        expected_output = """! Grid dimensions
        NX NY NZ
        1 2 3
        test string
        DUMMY VALUE
        ! comment
        !dummy text

        other text

        LIST

        POROSITY VALUE
        !ANOTHER COMMENT
        INCLUDE path/to/porosity.inc
        KX CON
        25.2
        """

        def mock_open_wrapper(filename, mode):
            mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
                'test_location/grid.dat': self.grid_text,
                '/path_to_netgrs_file/net_to_gross.inc': '',
                'path/to/porosity.inc': '',
                os.path.join('test_location', 'path/to/porosity.inc'): '',
            }).return_value
            return mock_open

        mocker.patch("builtins.open", mock_open_wrapper)
        grid_nexus_file = NexusFile.generate_file_include_structure(file_path='test_location/grid.dat')
        grid = NexusGrid(model_unit_system=UnitSystem.METRIC,
                         grid_nexus_file=grid_nexus_file)
        array_to_remove = 'netgrs'
        # Act
        grid.remove(array=array_to_remove)
        # Assert
        assert grid_nexus_file.file_content_as_list == expected_output.splitlines(keepends=True)
        assert grid.netgrs == GridArrayDefinition()

    def test_nexus_grid_modify_basic_test(self, mocker):
        # mock uuid
        mocker.patch('ResSimpy.DataModelBaseClasses.GridArrayDefinition.uuid4',
                     side_effect=uuid_side_effect())
        expected_output = """! Grid dimensions
        NX NY NZ
        1 2 3
        test string
        DUMMY VALUE
        ! comment
        !dummy text

        other text
NETGRS VALUE
INCLUDE /new_path_to_netgrs_file/new_net_to_gross_file.inc

        LIST

        POROSITY VALUE
        !ANOTHER COMMENT
        INCLUDE path/to/porosity.inc
        KX CON
        25.2
        """
        
        def mock_open_wrapper(filename, mode):
            mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
                'test_location/grid.dat': self.grid_text,
                '/path_to_netgrs_file/net_to_gross.inc': '',
                'path/to/porosity.inc': '',
                os.path.join('test_location', 'path/to/porosity.inc'): '',
            }).return_value
            return mock_open

        mocker.patch("builtins.open", mock_open_wrapper)
        grid_nexus_file = NexusFile.generate_file_include_structure(file_path='test_location/grid.dat')
        grid = NexusGrid(model_unit_system=UnitSystem.METRIC,
                         grid_nexus_file=grid_nexus_file)
        array_to_modify = 'NETGRS'
        # Act
        grid.modify(array=array_to_modify, new_properties=self.new_grid_array_definition)
        # Assert
        assert grid_nexus_file.file_content_as_list == expected_output.splitlines(keepends=True)
        # check the ids:
        assert grid.netgrs.id == self.new_grid_array_definition.id
        assert grid.netgrs == self.new_grid_array_definition
