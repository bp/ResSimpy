import pytest
from ResSimpy.Nexus.resqml_to_nexus_deck.ResqmlToNexusDeck import ResqmlToNexusDeck
import resqpy.model
import resqpy.crs
import resqpy.well
import os
import numpy as np


@pytest.mark.parametrize('is_gas_model, expected_dirname', [
    (False, 'Oil_Template_Model'),
    (True, 'Gas_Template_Model'),
    (True, 'Gas_Template_Model'),
    (False, 'Oil_Template_Model'),
])
def test_select_correct_model_template(mocker, is_gas_model, expected_dirname):
    # Arrange
    epc_path = '/path/to/input.epc'
    output_folder = '/another/path/to/output/deck'

    resqpy_grid_mock = mocker.Mock(name="Resqpy Grid Mock")
    resqpy_grid_class_mock = mocker.Mock(name="Resqpy Grid Class Mock", return_value=resqpy_grid_mock)
    resqpy_units_mock = mocker.Mock(name="Units mock", return_value='m')
    resqpy_grid_xyzbox_mock = mocker.Mock(name="XYZ Box", return_value=np.zeros((2, 3)))
    mocker.patch.object(resqpy_grid_mock, attribute='xy_units', new=resqpy_units_mock)
    mocker.patch.object(resqpy_grid_mock, attribute='z_units', new=resqpy_units_mock)
    mocker.patch.object(resqpy_grid_mock, attribute='xyz_box', new=resqpy_grid_xyzbox_mock)

    resqpy_parts_mock = mocker.Mock(name="Resqpy Parts Mock", return_value=['Grid_1'])
    resqpy_model_mock = mocker.Mock(name="Resqpy Model Mock")
    mocker.patch.object(resqpy.model, attribute='Model', return_value=resqpy_model_mock)
    mocker.patch.object(resqpy_model_mock, attribute='parts', new=resqpy_parts_mock)
    mocker.patch.object(resqpy_model_mock, attribute='grid', new=resqpy_grid_class_mock)

    resqpy_crs_mock = mocker.Mock(name="crs mock", return_value=False)
    mocker.patch.object(resqpy.crs, attribute='Crs', return_value=resqpy_crs_mock)

    nexus_deck_creator = ResqmlToNexusDeck(epc_path=epc_path, output_folder=output_folder,
                                           is_gas_model=is_gas_model)

    # Act
    result = nexus_deck_creator.get_model_template_location()

    # Assert
    full_path = os.path.dirname(result)
    directory_name = os.path.basename(full_path)
    assert directory_name == expected_dirname


@pytest.mark.parametrize('well_ids, well_names, expected_result', [
    (['aaa_id_1', 'aaa_id_2'], ['Well 1', 'Well 2'], [('Well 1', 'aaa_id_1'), ('Well 2', 'aaa_id_2')]),
    (['efffc581-9be9-4b0c-b55a-0fdb040f217a', '283fd9b3-63f3-4fe3-8206-3c36e280110c',
      'ccc5c20c-258e-4a13-b48b-c477741f4af1', '807f1bf3-7807-4cd2-b174-b51eade065cb'],
     ['W13(WW11) Interpretation', 'N02(NW02) Interpretation', 'C23Z(CP23) Interpretation', 'C31(CW32) Interpretation'],
     [('W13(WW11) Interpretation', 'efffc581-9be9-4b0c-b55a-0fdb040f217a'),
      ('N02(NW02) Interpretation', '283fd9b3-63f3-4fe3-8206-3c36e280110c'),
      ('C23Z(CP23) Interpretation', 'ccc5c20c-258e-4a13-b48b-c477741f4af1'),
      ('C31(CW32) Interpretation', '807f1bf3-7807-4cd2-b174-b51eade065cb')]),
    # Check we are filtering duplicates
    (['aaa_id_1', 'aaa_id_2', 'aaa_id_1'], ['Well 1', 'Well 2', 'Well 1'],
     [('Well 1', 'aaa_id_1'), ('Well 2', 'aaa_id_2')]),
])
def test_get_trajectories(mocker, well_ids, well_names, expected_result):
    # Arrange
    resqpy_model_mock = mocker.Mock(name="Resqpy Model Mock", return_value='model')
    mocker.patch.object(resqpy.model, attribute='Model', return_value=resqpy_model_mock)
    resqpy_uuids_value_mock = mocker.Mock(return_value=well_ids, name="UUIDs Value")
    mocker.patch.object(resqpy_model_mock, 'uuids', resqpy_uuids_value_mock)

    well_name_mock = mocker.MagicMock(name="Well Name")
    well_name_mock.side_effect = well_names
    mocker.patch.object(resqpy.well, 'well_name', new=well_name_mock)

    # Act
    result = ResqmlToNexusDeck.get_trajectories('test/model/address')

    # Assert
    assert result == expected_result

    for index, call in enumerate(well_name_mock.calls()):
        assert call[0] == well_names[index]

@pytest.mark.parametrize('trajectory_units, expected_returned_units', [
    ('m', 'm'),
    ('ft', 'ft'),
    ('ft[US]', 'ft')
])
def test_get_trajectory_units(mocker, trajectory_units, expected_returned_units):
    # Arrange
    root_for_uuid_mock = mocker.Mock(name="root_for_uuid mock", return_value='2cbf7ec1-4aad-4a35-bae7-bb3d8b9871c1')
    resqpy_model_mock = mocker.Mock(name="Resqpy Model Mock", return_value='model')
    mocker.patch.object(resqpy_model_mock, attribute='root_for_uuid', return_value=root_for_uuid_mock)
    mocker.patch.object(resqpy.model, attribute='Model', return_value=resqpy_model_mock)

    trajectory_mock = mocker.Mock(name="Trajectory Mock")
    well_mock = mocker.Mock(name="Well Mock")
    uom_value_mock = mocker.Mock(name="units value mock", return_value=trajectory_units)
    mocker.patch.object(trajectory_mock, 'md_uom', new=trajectory_units)
    mocker.patch.object(resqpy.well, 'Trajectory', return_value=trajectory_mock)

    # Act
    result = ResqmlToNexusDeck.get_trajectory_units('model/address', 'efffc581-9be9-4b0c-b55a-0fdb040f217a')

    # Assert
    assert result == expected_returned_units
