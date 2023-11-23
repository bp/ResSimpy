from pytest_mock import MockerFixture

# Initial tests assuming well information is in the base .in file for the OpenGoSim model
def test_load_basic_well(mocker: MockerFixture):
    # Arrange
    in_file_text = """
! Initial comment describing the model
SIMULATION
    SIMULATION_TYPE SUBSURFACE
        
END    
"""

    # Act

    # Assert



# TODO: Add tests that test loading wells via include files etc