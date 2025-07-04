"""Class to represent Nexus grid array functions."""
from dataclasses import dataclass
from typing import Optional
import pandas as pd

from ResSimpy.DataModelBaseClasses.GridArrayFunction import GridArrayFunction


@dataclass
class NexusGridArrayFunction(GridArrayFunction):
    """Class to hold Nexus grid array function attributes.

    Attributes:
        function_table (pd.DataFrame): Dependency between input and output grid arrays, represented in tabular form
        function_table_m (int): Maximum number of function table entries which can be used in tabular interpolation
        function_table_p_list (list[float]): Shifts of the first, second, ..., and N-th input arrays
    """

    function_table: Optional[pd.DataFrame] = None
    function_table_m: Optional[int] = None
    function_table_p_list: Optional[list[float]] = None

    def to_string(self) -> str:
        """Creates a string representation of the object."""

        # compile the function string
        func_string = "FUNCTION"

        # create beginning of string by checking region type
        if self.region_number is not None and self.region_type is not None:
            # the region number immediately follows the region type
            reg_num_str = ' '.join(str(num) for num in self.region_number)
            func_string += f" {self.region_type}\n{reg_num_str}\n"
        elif self.region_type is None:
            # if there is no region type, we just write FUNCTION
            func_string += "\n"

        if self.blocks is not None:
            # after region type comes BLOCKS
            block_num_str = ' '.join(str(num) for num in self.blocks)
            func_string += f"BLOCKS {block_num_str}\n"

        if self.grid_name is not None:
            # after blocks comes the grid
            func_string += f'GRID {self.grid_name}\n'

        if self.input_range is not None:
            input_vals = (
                ' '.join(f'{i:.5e}' if len(str(i)) > 5 else str(i) for pair in self.input_range for i in pair))
            func_string += 'RANGE INPUT' + ' ' + input_vals + '\n'

        if self.output_range is not None:
            output_vals = (
                ' '.join(f'{i:.5e}' if len(str(i)) > 5 else str(i) for pair in self.output_range for i in pair))
            func_string += 'RANGE OUTPUT' + ' ' + output_vals + '\n'

        if self.drange is not None:
            drange_vals = ' '.join(f'{num:.5e}' if len(str(num)) > 5 else str(num) for num in self.drange)
            func_string += 'DRANGE' + ' ' + drange_vals + '\n'

        if self.function_type is not None and self.function_type.value is not None:
            # ANALYT must always precede function type
            func_vals = ''
            if self.function_values is not None:
                func_vals = ' '+' '.join(str(num) for num in self.function_values)
            func_string += f'ANALYT {self.function_type.value}' + func_vals + '\n'

        # specify the end of the string with output/input arrays
        input_arr = output_arr = ''
        if self.input_array is not None and self.output_array is not None:
            input_arr = ' '.join(num for num in self.input_array)
            output_arr = ' '.join(num for num in self.output_array)

        return func_string + input_arr + ' OUTPUT ' + output_arr + '\n'

    def __str__(self) -> str:
        return self.to_string()

    def __repr__(self) -> str:

        beginning = 'NexusGridArrayFunction('
        close_it = ')'

        # for some reason python does not pick up dataclass_fields, but it still works.
        running_str = ''
        for param in self.__dataclass_fields__.values():

            field_name = param.name
            class_attr = getattr(self, param.name)

            if class_attr is not None:
                # covert class_attr to str since there are some lists
                running_str += field_name + '=' + str(class_attr) + ','

        # strings are immutable in python so need to overwrite with slice
        # this takes care of the extra ',' caused at the end of the above loop
        running_str = running_str[0:-1]
        return beginning + running_str + close_it
