"""A class to modify an existing object in a file with a new set of properties."""
from __future__ import annotations

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ResSimpy.Nexus.NexusNetwork import NexusNetwork


class ModifyObjectOperations:
    def __init__(self, object_to_modify: Any) -> None:
        """Initialises the ModifyObjectOperations class.

        Args:
            object_to_modify (Any): Passed in object to modify and pass back out.
        """
        self.object_to_modify = object_to_modify

    def modify_network_object(self, object_to_modify: dict[str, None | str | float | int],
                              new_properties: dict[str, None | str | float | int], network: NexusNetwork) -> None:
        """Modifies an existing object based on a matching dictionary of properties.

        Partial matches allowed if precisely 1 matching object is found.
        Updates the properties with properties in the new_properties dictionary.
        Applies primarily to network based objects.

        Args:
            object_to_modify (dict[str, None | str | float | int]): dictionary containing attributes to match in the
            existing object set. Requires an implemented add, remove
            new_properties (dict[str, None | str | float | int]): properties to switch to in the new object
            network (NexusNetwork): The network object containing the object to modify.
        """
        # TODO apply this to more of the network attributes through the Base Class
        network_attribute_name = self.object_to_modify._network_element_name
        name = object_to_modify.get('name', None)
        if name is None:
            raise ValueError(f'Name is required for modifying {network_attribute_name}, '
                             f'instead got {name}')
        name = str(name)
        network_element = network.find_network_element_with_dict(name, object_to_modify,
                                                                 network_attribute_name)
        existing_properties = network_element.to_dict(include_nones=False, units_as_string=False)
        # pass through the start date
        if getattr(network_element, 'start_date', None) is not None:
            existing_properties['start_date'] = getattr(network_element, 'start_date')
        # do the union of the two dicts
        existing_properties.update(new_properties)

        self.object_to_modify.remove(object_to_modify)
        self.object_to_modify.add(existing_properties)
