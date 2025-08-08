from __future__ import annotations
from ResSimpy.DataModelBaseClasses.DynamicProperty import DynamicProperty
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from typing import TYPE_CHECKING, TypeAlias

if TYPE_CHECKING:
    from ResSimpy.Nexus.NexusAquiferMethods import NexusAquiferMethods
    from ResSimpy.Nexus.NexusEquilMethods import NexusEquilMethods
    from ResSimpy.Nexus.NexusGasliftMethods import NexusGasliftMethods
    from ResSimpy.Nexus.NexusHydraulicsMethods import NexusHydraulicsMethods
    from ResSimpy.Nexus.NexusPVTMethods import NexusPVTMethods
    from ResSimpy.Nexus.NexusRelPermMethods import NexusRelPermMethods
    from ResSimpy.Nexus.NexusRockMethods import NexusRockMethods
    from ResSimpy.Nexus.NexusSeparatorMethods import NexusSeparatorMethods
    from ResSimpy.Nexus.NexusValveMethods import NexusValveMethods
    from ResSimpy.Nexus.NexusWaterMethods import NexusWaterMethods

    DynamicMethodCollection: TypeAlias = (
            NexusRockMethods | NexusPVTMethods | NexusEquilMethods | NexusWaterMethods |
            NexusSeparatorMethods | NexusHydraulicsMethods | NexusAquiferMethods | NexusValveMethods |
            NexusGasliftMethods | NexusRelPermMethods
               )


def add_dynamic_method(dynamic_method_collection: DynamicMethodCollection, method: DynamicProperty, new_file_name: str,
                       create_new_file: bool = False) -> None:
    """Adds a new DynamicMethod to the collection.

    Args:
        dynamic_method_collection (DynamicMethodCollection): The collection to add the method to.
        method (DynamicProperty): The dynamic method to add.
        new_file_name (str): The name of the file to save the method to.
        create_new_file (bool): Whether to create a new file for the method.
    """
    if new_file_name is None or new_file_name.strip() == '':
        raise ValueError('New file name must be provided and cannot be empty when adding a new method.')

    if method.input_number in dynamic_method_collection.inputs:
        raise ValueError(f'Method with input number {method.input_number} already exists in the collection.')

    method_type = dynamic_method_collection._method_type()

    if not isinstance(method, method_type):
        raise TypeError(f'Expected method of type {method_type.__name__}, but got {type(method).__name__}.')

    dynamic_method_collection.__properties_loaded = True  # We are adding a new method so no more loading can happen.

    new_nexus_file = NexusFile(location=new_file_name,
                               origin=None,  # Should get connected to the parent fcs file later
                               include_objects=None,
                               file_content_as_list=method.to_string().splitlines(keepends=True)
                               )
    new_nexus_file._file_modified_set(True)  # Mark the file as modified
    method.file = new_nexus_file

    if create_new_file:
        method.write_to_file(new_file_path=new_file_name, overwrite_file=False)

    # explicit guard against the method type is used above so ignore mypy.
    dynamic_method_collection.inputs[method.input_number] = method  # type: ignore[assignment]
    dynamic_method_collection.files[method.input_number] = method.file
    if dynamic_method_collection._model_files is not None:
        dynamic_method_collection._model_files._add_file(new_nexus_file, keyword=dynamic_method_collection.keyword,
                                                         method_number=method.input_number)
