import re


def create_getter_setter(string_to_modify: str) -> str:

    pattern = r"\.(.*?):"
    result_string = ''

    for x in string_to_modify.splitlines():
        match = re.search(pattern, x)
        attribute_key = match.group(1)
        class_key = x.split('=')[-1].replace('()','')
        result_string += (f"""
    @property
    def {attribute_key}(self) -> {class_key}:
        return self.__{attribute_key}
    
    
    @{attribute_key}.setter
    def {attribute_key}(self, cls):
        if not isinstance(cls, {class_key}):
            raise ValueError(f"{attribute_key} must take a valid {attribute_key} type."
                             f"Instead got provided class of {{type(cls)}}")
        self.__{attribute_key} = cls
    """)
    return result_string