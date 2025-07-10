from ResSimpy import NexusSimulator


def test_multi_reservoir_handling():
    # Arrange
    # Current development stage expects to throw a warning describing partial handling of multires models
    # We should also expect the reservoir files to be added to the model's reservoir list.
    
    test_fcs_file = """! Multireservoir network connection
    
    RUN_UNITS METBAR
    
    DEFAULT_UNITS METBAR
    
    DATEFORMAT DD/MM/YYYY
    
    RESERVOIR  RUM  rumaila.fcs
    
    RESERVOIR GAW  ghawar.fcs
    
    RESERVOIR BURG  burgan.fcs
    
    
    """
    
    fcs_path = '/this/is/a/test/path/test.fcs'
    
    # Act
    result = NexusSimulator(fcs_path)
    
    # Assert
    assert result.multires is True
    assert result.reservoir_paths == {'RUM': 'rumaila.fcs', 'GAW': 'ghawar.fcs', 'BURG': 'burgan.fcs'}