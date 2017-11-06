"""Testing
"""

from pkg_resources import Requirement
from pkg_resources import resource_filename
import os

class TestDataPath:
    """Tests that the data_files configuration in setup.cfg places the data
    folder in a location relative to the energy_demand package
    """
    '''def test_get_path(self):
        path_main = resource_filename(Requirement.parse("energy_demand"),
                                      "data")
        # CHECK THAT DATA FOLDER IN NISMOD FOLDER
        expected = os.path.join(path_main)
        assert os.path.exists(expected)

        expected = os.path.join(path_main, 'submodel_residential')
        assert os.path.exists(expected)

        expected = os.path.join(path_main, 'submodel_service')
        assert os.path.exists(expected)'''
