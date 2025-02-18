"""Creates a repr for data objects that removes attributes that are None from the representation."""
from typing import Any, Optional


def generic_repr(input_class: Any, exclude_attributes: Optional[list[str]] = None) -> str:
    """Creates a prettier object representation while removing attributes that are None from that representation.

    Args:
    ----
        input_class (Any): a class with attributes to summarise
        exclude_attributes (list[str]): a list of attributes to exclude. Defaults to None.

    Returns:
    -------
        (str): Pretty representation of the string.
    """
    filtered_attrs = {k: v for k, v in vars(input_class).items() if v is not None}

    # Remove the leading underscores from the repr.
    sanitised_attrs = {}
    for key in filtered_attrs.keys():
        if exclude_attributes is not None and key in exclude_attributes:
            continue
        elif key == '_DataObjectMixin__id':
            sanitised_key = 'ID'
        elif key == '_DataObjectMixin__iso_date':
            sanitised_key = 'ISO_Date'
        elif key == '_DataObjectMixin__date':
            sanitised_key = 'Date'
        elif key[0] == '_':
            sanitised_key = key[1:] if key[1] != '_' else key[2:]
        else:
            sanitised_key = key

        sanitised_attrs[sanitised_key] = filtered_attrs[key] if sanitised_key != 'ISO_Date' \
            else str(filtered_attrs[key])

    attrs = ', '.join(f"{k}={v!r}" for k, v in sanitised_attrs.items())
    return f"{input_class.__class__.__name__}({attrs})"


def generic_str(input_class: Any) -> str:
    """Creates a string representation of the object while removing None and ids from the string.

    Args:
        input_class (Any): a class with attributes to summarise

    Returns:
        (str): String representation of the object.
    """
    filtered_attrs = {k: v for k, v in vars(input_class).items() if v is not None}
    id_keys = [id_attr for id_attr in filtered_attrs if id_attr.endswith('__id')]
    for id_attr in id_keys:
        del filtered_attrs[id_attr]

    attrs = ', '.join(f"{k}={v!r}" for k, v in filtered_attrs.items())
    return f"{input_class.__class__.__name__}({attrs})"
