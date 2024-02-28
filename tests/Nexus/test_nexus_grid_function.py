from ResSimpy.Enums.GridFunctionTypes import GridFunctionTypeEnum
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.StructuredGrid.NexusGrid import NexusGrid
from ResSimpy.Nexus.DataModels.StructuredGrid.NexusGridArrayFunction import NexusGridArrayFunction
from ResSimpy.Nexus.array_function_operations import object_from_array_function_block


class TestNexusGridFunction:
    def test_load_nexus_grid_function(self):
        # Arrange
        input_file = '''FUNCTION IREGION
    1
    ANALYT POLYN 1.0 0.0
    KX OUTPUT KY'''

        file = NexusFile(location='path/to/file.dat', file_content_as_list=input_file.splitlines(keepends=True))

        expected_result = [NexusGridArrayFunction(
            region_type='IREGION',
            region_number=[1],
            function_type=GridFunctionTypeEnum.POLYN,
            input_array=['KX'],
            output_array=['KY'],
            function_values=[1.0, 0.0]
        )]
        grid = NexusGrid(file)
        # Act
        result = grid.array_functions
        # Assert
        assert result == expected_result

    def test_object_from_array_function_block(self):
        # Arrange
        input_data = ['FUNCTION IREGION', '1', 'ANALYT POLYN 0.0 1212.59288582951', 'KX OUTPUT KX']
        expected_result = NexusGridArrayFunction(
            region_type='IREGION',
            region_number=[1],
            function_type=GridFunctionTypeEnum.POLYN,
            input_array=['KX'],
            output_array=['KX'],
            function_values=[0.0, 1212.59288582951]
        )
        # Act
        result = object_from_array_function_block(input_data, 1)
        # Assert
        assert result == expected_result
