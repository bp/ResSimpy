from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.Nexus.DataModels.NexusCompletion import NexusCompletion
from ResSimpy.Enums.UnitsEnum import UnitSystem
import pytest


@pytest.mark.parametrize("add_date, add_units, expected_result", [
    (True, True, {'date': '01/02/2023', 'grid': 'GRID1', 'i': 1, 'j': 2, 'k': 3,
                  'partial_perf': 0.1, 'well_radius': 4.5, 'unit_system': 'ENGLISH'}),
    (True, False, {'date': '01/02/2023', 'grid': 'GRID1', 'i': 1, 'j': 2, 'k': 3,
                   'partial_perf': 0.1, 'well_radius': 4.5}),
    (False, False, {'grid': 'GRID1', 'i': 1, 'j': 2, 'k': 3,
                    'partial_perf': 0.1, 'well_radius': 4.5})
])
def test_nexus_completion_to_dict(add_date, add_units, expected_result):
    # Arrange

    # Act
    result = (NexusCompletion(date='01/02/2023', i=1, j=2, k=3, skin=None, well_radius=4.5, angle_v=None, grid='GRID1',
                              partial_perf=0.1, date_format=DateFormat.DD_MM_YYYY, unit_system=UnitSystem.ENGLISH)
              .to_dict(add_date=add_date, add_units=add_units, include_nones=False))

    # Assert
    assert result == expected_result


def test_nexus_completion_to_dict_include_nones():
    expected_result = {'angle_a': None,
                       'angle_open_flow': None,
                       'angle_v': None,
                       'cell_number': None,
                       'comp_dz': None,
                       'date': '01/02/2023',
                       'depth': None,
                       'depth_to_bottom': None,
                       'depth_to_top': None,
                       'dfactor': None,
                       'flowsector': None,
                       'fracture_mult': None,
                       'grid': 'GRID1',
                       'i': 1,
                       'j': 2,
                       'k': 3,
                       'kh_mult': None,
                       'layer_assignment': None,
                       'length': None,
                       'mdcon': None,
                       'measured_depth': None,
                       'non_darcy_model': None,
                       'parent_node': None,
                       'partial_perf': 0.1,
                       'peaceman_well_block_radius': None,
                       'perm_thickness_ovr': None,
                       'permeability': None,
                       'polymer_block_radius': None,
                       'polymer_well_radius': None,
                       'portype': None,
                       'pressure_avg_pattern': None,
                       'rel_perm_method': None,
                       'sector': None,
                       'skin': None,
                       'status': None,
                       'temperature': None,
                       'unit_system': 'ENGLISH',
                       'well_group': None,
                       'well_indices': None,
                       'well_radius': 4.5,
                       'x': None,
                       'y': None,
                       'zone': None}

    result = NexusCompletion(date='01/02/2023', i=1, j=2, k=3, skin=None, well_radius=4.5, angle_v=None,
                             grid='GRID1', partial_perf=0.1, date_format=DateFormat.DD_MM_YYYY,
                             unit_system=UnitSystem.ENGLISH).to_dict(add_date=True, add_units=True, include_nones=True)

    # Assert
    assert result == expected_result
