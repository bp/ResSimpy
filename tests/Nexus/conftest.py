
import pytest
from ResSimpy.Utils.Test_Utils.utility_for_tests import get_fake_stat_pathlib_time

@pytest.fixture
def fixture_for_osstat_pathlib(mocker):
    get_fake_stat_pathlib_time(mocker)


    
  