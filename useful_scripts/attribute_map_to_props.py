from ResSimpy.Units.AttributeMapping import AttributeMapBase


def attribute_map_to_property(attribute_map: AttributeMapBase):
    for key, value in attribute_map.attribute_map.items():
        print(
            f"""
    @property
    def {key}(self) -> str:
        \"\"\"Returns the unit for {key}.\"\"\"
        return self.get_unit_from_attribute('{key}')""")