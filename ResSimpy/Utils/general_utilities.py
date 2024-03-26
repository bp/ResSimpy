def check_if_string_is_float(x: str) -> bool:
    """Function to check if a string can be successfully cast to a float.

    Args:
        x (str): String input to check

    Returns:
        bool: True if string can be successfully cast to a float, otherwise false.
    """
    try:
        float(x)
        return True
    except ValueError:
        return False
