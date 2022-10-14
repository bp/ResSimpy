import numpy as np
import sys

# Global mocks for reuse between tests
resqml_model_mock = resqml_model_class_mock = resqml_parts_mock = resqml_parts_value_mock = resqml_grid_mock = \
    resqml_grid_value_mock = units_mock = xyz_box_mock = resqml_well_mock = None


def reset_mocks():
    global resqml_parts_value_mock, resqml_parts_mock, resqml_grid_mock, units_mock, resqml_grid_value_mock, \
        xyz_box_mock, resqml_model_mock, resqml_well_mock, resqml_model_class_mock

    resqml_model_mock = resqml_model_class_mock = resqml_parts_mock = resqml_parts_value_mock = resqml_grid_mock = \
        resqml_grid_value_mock = units_mock = xyz_box_mock = resqml_well_mock = None

    # if 'rq' in sys.modules:
    #     del sys.modules['resqpy']

    keys = sys.modules.keys()
    for key in keys:
        del key
        # if key != 'sys':
        #     del key


def declare_resqml_mocks(mocker):
    global resqml_parts_value_mock, resqml_parts_mock, resqml_grid_mock, units_mock, resqml_grid_value_mock, \
        xyz_box_mock, resqml_model_mock, resqml_well_mock, resqml_model_class_mock

    resqml_model_mock = mocker.Mock(name="Model Import", return_value=resqml_model_class_mock)
    resqml_well_mock = mocker.Mock(name="Well Import", return_value=resqml_well_mock)
    resqml_model_class_mock = mocker.Mock(name="Class Import")
    resqml_parts_value_mock = mocker.MagicMock(return_value=['Grid_1'], name="Parts Value")
    resqml_parts_mock = mocker.MagicMock(return_value=resqml_parts_value_mock, name="parts Import")

    resqml_grid_mock = mocker.MagicMock(name="Grid Mock", return_value="Test Units")
    resqml_grid_value_mock = mocker.MagicMock(return_value=resqml_grid_mock, name="Grid Value")
    units_mock = mocker.MagicMock(return_value='Test Units')
    xyz_box_mock = mocker.MagicMock(return_value=np.zeros((2, 3)))


def patch_resqml_mocks(mocker):
    global resqml_parts_value_mock, resqml_parts_mock, resqml_grid_mock, units_mock, resqml_grid_value_mock, \
        xyz_box_mock, resqml_model_mock, resqml_well_mock, resqml_model_class_mock

    mocker.patch.object(resqml_model_mock, 'model', resqml_model_class_mock)
    mocker.patch.object(resqml_model_class_mock, 'Model', resqml_parts_mock)
    mocker.patch.object(resqml_parts_value_mock, 'parts', resqml_parts_value_mock)
    mocker.patch.object(resqml_grid_mock, 'xy_units', units_mock)
    mocker.patch.object(resqml_grid_mock, 'z_units', units_mock)
    mocker.patch.object(resqml_grid_mock, 'xyz_box', xyz_box_mock)
    mocker.patch.object(resqml_parts_value_mock, 'grid', resqml_grid_value_mock)
    mocker.patch.object(resqml_well_mock, 'well', resqml_well_mock)


def mock_imports(mocker):
    orig_import = __import__

    generic_mock = mocker.MagicMock(name="Generic Import")
    resqml_mock = mocker.MagicMock(name="RESQPY Mock")

    def import_mock(name: str, *args, **kwargs):
        if name.startswith('resqpy.model'):
            return resqml_model_mock
        if name.startswith('resqpy.well'):
            return resqml_well_mock
        elif name.startswith('resqpy'):
            return resqml_mock(name, *args, **kwargs)
        if name.__contains__('simkit'):
            return generic_mock(name, *args, **kwargs)
        if name.endswith('envmodules') or name.endswith('env_modules_python'):
            return generic_mock(mocker, name, *args, **kwargs)
        return orig_import(name, *args, **kwargs)

    mocker.patch('builtins.__import__', side_effect=import_mock)
