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
