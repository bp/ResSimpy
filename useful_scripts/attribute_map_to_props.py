import sys
sys.path.insert(0, '/path/to/ResSimpy/on/local/machine')
from ResSimpy.Units.AttributeMappings.BaseUnitMapping import BaseUnitMapping
from ResSimpy.Units.AttributeMappings.DynamicPropertyUnitMapping import PVTUnits


def attribute_map_to_property(attribute_map: BaseUnitMapping):
    for key, value in attribute_map.attribute_map.items():
        print(
            f"""
    @property
    def {key}(self) -> str:
        \"\"\"Returns the unit for {key}.\"\"\"
        return self.get_unit_for_attribute('{key}')""")

if __name__ == "__main__":
    attribute_map_to_property(PVTUnits)
