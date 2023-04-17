from typing import Any

from ResSimpy.Nexus.NexusEnums.UnitsEnum import UnitSystem


def to_dict(nexus_object: Any, keys_in_nexus_style: bool = False, add_date: bool = True, add_units: bool = True) -> \
        dict[str, None | str | int | float]:
    """ Returns a dictionary of the attributes of a Nexus object. Requires a nexus mapping dictionary.
        Useful for creating dataframes of objects

    Args:
        nexus_object (Any): Nexus object with a mapping dictionary defined
        keys_in_nexus_style (bool): if True returns the key values in Nexus keywords, otherwise returns the
            attribute name as stored by ressimpy
        add_date (bool): adds a date attribute if it exists
        add_units (bool): adds a units attribute if it exists.

    Returns:
        a dictionary keyed by attributes and values as the value of the attribute
    """
    mapping_dict = nexus_object.get_nexus_mapping()
    if keys_in_nexus_style:
        result_dict = {x: nexus_object.__getattribute__(y[0]) for x, y in mapping_dict.items()}

    else:
        result_dict = {y[0]: nexus_object.__getattribute__(y[0]) for y in mapping_dict.values()}

    if add_date:
        result_dict['date'] = getattr(nexus_object, 'date')
    if add_units:
        unit_sys = getattr(nexus_object, 'unit_system')
        if isinstance(unit_sys, UnitSystem):
            result_dict['unit_system'] = unit_sys.value
    return result_dict
