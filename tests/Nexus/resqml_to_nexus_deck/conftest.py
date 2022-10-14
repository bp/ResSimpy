import pytest
# from resqml_to_nexus_deck_mocks import declare_resqml_mocks, patch_resqml_mocks, mock_imports, reset_mocks

def mock_dependencies(mocker):
    resqpy_mock = mocker.Mock(name="Resqpy Mock")
    mocker.patch.object()

@pytest.fixture(scope="function", autouse=True)
def resqpy_mocks(mocker):
    """ Test fixture to import the ResqmlToNexusDeck class after mocking out the external imports """
    # mock_dependencies(mocker)
    # declare_resqml_mocks(mocker)
    # patch_resqml_mocks(mocker)
    # # mock_imports(mocker)
    #
    # yield
    #
    # reset_mocks()
