"""Unit tests for the NexusLGRs.load_lgrs method."""
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.StructuredGrid.NexusGrid import NexusGrid
from ResSimpy.Nexus.DataModels.StructuredGrid.NexusLGR import NexusLGR
from ResSimpy.Nexus.DataModels.StructuredGrid.NexusLGRs import NexusLGRs

"""TODO:
load just the LGR and CARTREF
Load the grids to the LGR object.
Add omits/INGRID
Handle Nested refinements and other geometry LGR"""


class TestLoadLGRs:
    grid_file_contents = """
NX NY NZ
 80  86  84
LGR
CARTREF lgr_01                         
  14  20   29  29  1  10  ! comment
  
  6*5  1*7 6*5
  9   ! comment
  
  10*1
ENDREF 
ENDLGR

LGR
CARTREF lgr_02                         
  1  3   29  29  10  10  ! comment
  
  1 2 3 
  9   ! comment
  10
ENDREF 
ENDLGR

"""
    expected_lgr_1 = NexusLGR(parent_grid='ROOT', name='lgr_01', i1=14, i2=20, j1=29, j2=29, k1=1, k2=10,
                              nx=[5, 5, 5, 5, 5, 5, 7, 5, 5, 5, 5, 5, 5],
                              ny=[9],
                              nz=[1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
                              )
    expected_lgr_2 = NexusLGR(parent_grid='ROOT', name='lgr_02', i1=1, i2=3, j1=29, j2=29, k1=10, k2=10,
                              nx=[1, 2, 3],
                              ny=[9],
                              nz=[10]
                              )

    def test_load_lgrs(self):
        # Arrange

        lgrs = NexusLGRs(grid_file_as_list=self.grid_file_contents.splitlines(keepends=True), parent_grid=None)

        # Act
        lgrs.load_lgrs()

        # Assert
        assert lgrs.lgrs[0] == self.expected_lgr_1
        assert lgrs.lgrs[1] == self.expected_lgr_2

    def test_load_lgrs_into_grid_object(self):
        # Arrange
        grid_nexus_file = NexusFile(location='grid.dat',
                                    file_content_as_list=self.grid_file_contents.splitlines(keepends=True))
        nexus_grid = NexusGrid(grid_nexus_file=grid_nexus_file, model_unit_system=UnitSystem.ENGLISH)

        # Act
        # call it this way so that we can also test lazy loading via the property
        lgrs_list = nexus_grid.lgrs.lgrs

        # Assert
        assert lgrs_list[0] == self.expected_lgr_1
        assert lgrs_list[1] == self.expected_lgr_2

    def test_get_by_name(self):
        lgrs = NexusLGRs(grid_file_as_list=self.grid_file_contents.splitlines(keepends=True), parent_grid=None)
        lgrs.load_lgrs()

        # Act
        result = lgrs.get(name='lgr_02')

        # Assert
        assert result == self.expected_lgr_2
