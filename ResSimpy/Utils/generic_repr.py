"""Creates a repr for data objects that removes attributes that are None from the representation."""
from typing import Any


def generic_repr(input_class: Any) -> str:
    """Creates a prettier object representation while removing attributes that are None from that
    representation.

    Args:
    ----
        input_class (Any): a class with attributes to summarise

    Returns:
    -------
        (str): Pretty representation of the string.
    """
    filtered_attrs = {k: v for k, v in vars(input_class).items() if v is not None}
    attrs = ', '.join(f"{k}={v!r}" for k, v in filtered_attrs.items())
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
