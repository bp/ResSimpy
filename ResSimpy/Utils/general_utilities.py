import re


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


def convert_to_number(x: str) -> int | float:
    """Function that takes a numerical string and casts it to an int or float, as appropriate.

    Args:
        x (str): Numerical string

    Returns:
        int | float: integer or float value from input numerical string
    """
    try:
        # Try to convert the string to an integer
        return int(x)
    except ValueError:
        # If it fails, try to convert the string to a float
        try:
            return float(x)
        except ValueError:
            raise ValueError(f'Provided string {x} is erroneous and needs to be either an integer or a float.')


def expand_string_list_of_numbers(s: str) -> str:
    """Function that's a string of numbers with repeats such as 1 2 3*4 5 and expands it appropriately into 1 2 4 4 4 5.

    Args:
        s (str): Input string of numbers with repeats, e.g., 1 2 3*4 5

    Returns:
        str: Expanded string of numbers, e.g., 1 2 4 4 4 5
    """
    # Find all occurrences of the pattern 'count*number' where number can be an integer or a float
    pattern = re.compile(r'(\d+)\*(\d+\.?\d*[eE]?[-+]?\d+)')
    matches = pattern.findall(s)

    # Replace each match with the expanded string
    for match in matches:
        count = int(match[0])
        str_value = match[1]
        value = convert_to_number(str_value)
        expanded = ' '.join([str(value)] * count)
        s = s.replace(f'{count}*{str_value}', expanded)

    return s


def is_number(s: str) -> bool:
    """Function that checks for floats, numbers and scientific notation to see if it can be converted to a float.

    Args:
        s (str): String input to check

    Returns:
        bool: True if string can be converted into float
    """

    try:
        float(s)
        return True
    except ValueError:
        return False
