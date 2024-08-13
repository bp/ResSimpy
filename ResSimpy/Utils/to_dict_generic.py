from typing import Any

from ResSimpy.Enums.UnitsEnum import UnitSystem


def to_dict(nexus_object: Any, keys_in_nexus_style: bool = False, add_date: bool = True, add_iso_date: bool = False,
            add_units: bool = True, include_nones: bool = True,
            units_as_string: bool = True) -> dict[str, None | str | int | float]:
    """Returns a dictionary of the attributes of a Nexus object. Requires a nexus mapping dictionary.

        Useful for creating dataframes of objects.

    Args:
    ----
        nexus_object (Any): Nexus object with a mapping dictionary defined
        keys_in_nexus_style (bool): if True returns the key values in Nexus keywords, otherwise returns the
            attribute name as stored by ressimpy
        add_date (bool): adds a date attribute if it exists
        add_iso_date (bool): adds an iso date attribute if it exists.
        add_units (bool): adds a units attribute if it exists.
        include_nones (bool): If False filters the nones out of the dictionary. Defaults to True.
        units_as_string (bool): If set to true, the unit system will be stored as a string in the dictionary.
            Defaults to True.

    Returns:
    -------
        a dictionary keyed by attributes and values as the value of the attribute
    """
    mapping_dict = nexus_object.get_keyword_mapping()
    if keys_in_nexus_style:
        result_dict = {x: nexus_object.__getattribute__(y[0]) for x, y in mapping_dict.items()}

    else:
        result_dict = {y[0]: nexus_object.__getattribute__(y[0]) for y in mapping_dict.values()}

    if add_date:
        try:
            result_dict['date'] = getattr(nexus_object, 'date')
        except AttributeError:
            raise AttributeError('Date was requested from the object but does not have a date associated with it.'
                                 f'Try setting add_date to False. Full contents of object: {nexus_object}')
    if add_iso_date and getattr(nexus_object, 'iso_date', None) is not None:
        result_dict['iso_date'] = getattr(nexus_object, 'iso_date')

    if add_units:
        try:
            unit_sys = getattr(nexus_object, 'unit_system')
        except AttributeError:
            raise AttributeError(
                'Unit system was requested from the object but does not have a unit system associated with it.'
                f'Try setting add_units to False. Full contents of the object: {nexus_object}')
        if isinstance(unit_sys, UnitSystem):
            result_dict['unit_system'] = unit_sys.value if units_as_string else unit_sys

    if hasattr(nexus_object, 'control_mode'):
        result_dict['control_mode'] = getattr(nexus_object, 'control_mode')

    if not include_nones:
        result_dict = {k: v for k, v in result_dict.items() if v is not None}
    return result_dict
