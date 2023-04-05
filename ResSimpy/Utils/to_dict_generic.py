from typing import Any

from ResSimpy.Nexus.NexusEnums.UnitsEnum import UnitSystem


def to_dict(nexus_object: Any, keys_in_nexus_style: bool = False, add_date: bool = True, add_units: bool = True) -> \
        dict[str, None | str | int | float]:
    """ Returns a dictionary of the key properties of a connection. Requires a nexus mapping dictionary

    Args:
        nexus_object (Any): Nexus object with a mapping dictionary defined
        keys_in_nexus_style (bool): if True returns the key values in Nexus keywords, otherwise returns the
            attribute name as stored by ressimpy
        add_date (bool): adds a date attribute if it exists
        add_units (bool): adds a units attribute if it exists.

    Returns:

    """
    mapping_dict = nexus_object.get_nexus_mapping()
    if keys_in_nexus_style:
        result_dict = {x: nexus_object.__getattribute__(y[0]) for x, y in mapping_dict.items()}

    else:
        result_dict = {y[0]: nexus_object.__getattribute__(y[0]) for y in mapping_dict.values()}

    extra_attributes = {}
    if add_date and nexus_object.getattr('date') is not None:
        date = {'date': nexus_object.getattr('date')}
        extra_attributes.update(date)
    if add_units and nexus_object.getattr('unit_system') is not None:
        unit_sys = nexus_object.getattr('unit_system')
        if isinstance(unit_sys, UnitSystem):
            units = {'unit_system': unit_sys.value}
        else:
            units = {'unit_system': unit_sys}
        extra_attributes.update(units)
    return result_dict
