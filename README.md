# ResSimpy: Python API for working with Reservoir Simulator models

Contributing to ResSimpy
======================

Development environment setup
-----------------------------

1. Clone the repo

   Create a fork of the repository using the GitHub website. Note: this step can be
   skipped if you already have write access to the main repo. Then, clone your fork
   locally to your computer to your working area:

   .. code-block:: bash

      git clone <url from GitHub>
      cd ResSimpy

2. Set up a Python environment
   **Note: due to a requirement of one of the dependencies, you will need to use a 64-bit installation of Python when working with ResSimpy.**
   The ResSimpy project uses `Poetry <https://python-poetry.org/>`_ for dependency management and environment setup. Please `install Poetry <https://python-poetry.org/docs/master/#installing-with-pip>`_ first if you have not already done so.

   Once those packages are installed, the environment can then be setup automatically with all dependencies installed using the following command in the base directory (the directory with the pyproject.toml file):

   .. code-block:: bash

      poetry install
        
   You can then switch to the virtual environment that you have just created using:

   .. code-block:: bash

      poetry shell

   Whilst inside the virtual environment, you can run all of the unit tests to confirm that the setup was successful using the command:

   .. code-block:: bash

      pytest

   If at a later date you wish to ensure that the dependencies in your dev environment are up to date with the latest supported versions, you can again run `poetry install` and your libraries will automatically be updated.
    
3. Make a Pull Request

   Create a new branch from master:

   .. code-block:: bash

      git checkout master
      git pull
      git checkout -b <your-branch-name>

   You can then commit and push your changes as usual. Open a Pull Request on
   GitHub to submit your code to be merged into master.
