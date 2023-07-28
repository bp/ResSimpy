
import pytest
from tests.utility_for_tests import get_fake_stat_pathlib_time

@pytest.fixture
def globalFixture(mocker):
    get_fake_stat_pathlib_time(mocker)


    
  