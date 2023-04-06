def prop_dict_params(property_dict: dict[str, tuple[str, type]]):
    """ A meta function for generating docstrings and dataclass data from a mapping dictionary
    Args:
        property_dict (dict[str, tuple[str, type]]): a dictionary of the form key: (property, type)

    Returns:
        A print-out ready for docstrings and dataclass property definition

    """
    print('"""')
    print('Attributes:')
    for key, value in property_dict.items():
        print(f'    {value[0]} ({value[1].__name__}): COMMENT ({key})')
    print('"""')
    for key, value in property_dict.items():
        print(f'{value[0]}: Optional[{str(value[1].__name__)}] = None')
