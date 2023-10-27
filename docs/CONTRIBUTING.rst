Contributing to ResSimpy
========================

ResSimpy is an open source project released under the Apache license. Contributions
of all forms are most welcome!

Ways of contributing
--------------------

* Submitting bug reports and feature requests (using the `GitHub issue tracker <https://github.com/bp/ResSimpy/issues>`_)
* Contributing code (in the form of `Pull requests <https://github.com/bp/ResSimpy/pulls>`_)
* Documentation or test improvements
* Publicity and support

Checklist for pull requests
---------------------------

1. Changes or additions should have appropriate unit tests (see below)
2. Follow the PEP8 style guide as far as possible (with caveats below).
3. All public functions and classes should have
   `Google-style docstrings <https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html>`_ 
4. All GitHub checks should pass

Development environment setup
-----------------------------

1. Clone the repo

   Create a fork of the repository using the GitHub website. Note: this step can be
   skipped if you already have write access to the main repo. Then, clone your fork
   locally to your computer to your working area:

   .. code-block:: bash

      git clone <url from GitHub>
      cd resqpy

2. Set up a Python environment
   **Note: due to a requirement of one of the dependencies, you will need to use a 64-bit installation of Python when working with ResSimpy.**
   The RESQPY project uses `Poetry <https://python-poetry.org/>`_ for dependency management and environment setup. Please `install Poetry <https://python-poetry.org/docs/master/#installing-with-pip>`_ first if you have not already done so.
   With Poetry installed, please then install the `Poetry Dynamic Versioning Plugin <https://github.com/mtkennerly/poetry-dynamic-versioning>`_.
   **Note: some Windows PCs run into issues related to the default Maximum path limit. If you receive errors when creating a Poetry virtual environment, please try `enabling long paths <https://learn.microsoft.com/en-us/windows/win32/fileio/maximum-file-path-limitation?tabs=registry>`_.

   Once both those packages are installed, the environment can then be setup automatically with all dependencies installed using the following command in the base directory (the directory with the pyproject.toml file):

   .. code-block:: bash

      poetry install
        
   You can then switch to the virtual environment that you have just created using:

   .. code-block:: bash

      poetry shell

   Whilst inside the virtual environment, you can run all of the unit tests to confirm that the setup was successful using the command:

   .. code-block:: bash

      pytest tests

   If at a later date you wish to ensure that the dependencies in your dev environment are up to date with the latest supported versions, you can again run `poetry install` and your libraries will automatically be updated.
    
3. Make a Pull Request

   Create a new branch from master:

   .. code-block:: bash

      git checkout master
      git pull
      git checkout -b <your-branch-name>

   You can then commit and push your changes as usual. Open a Pull Request on
   GitHub to submit your code to be merged into master.

Code Style
----------

Please try to write code according to the
`PEP8 Python style guide <https://www.python.org/dev/peps/pep-0008/>`_, which
defines conventions such as variable naming and capitalisation. A consistent
style makes it much easier for other developers to read and understand your
code.

See :ref:`Running Other Checks on your local machine` for how to check your code for conformance to PEP8 style.

Tests
-----

Why write tests?
^^^^^^^^^^^^^^^^

Automated tests are used to check that code does what it is supposed to do. This
is absolutely key to maintaining quality: for example, automated tests enable
maintainers to check whether anything breaks when new versions of 3rd party
libraries are released.

As a rule of thumb: if you want your code to still work in 6 months' time,
ensure it has some unit tests!

Writing tests
^^^^^^^^^^^^^

pytest is a framework for running automated tests in Python. It is a high-level
framework, so very little code is required to write a test.

Tests are written in the form of functions with the prefix ``test_``. Look in the
tests directory for examples of existing tests. A typical pattern is
``Arrange-Act-Assert``:

.. code:: python

    def test_get_first_perforation(completions, expected_perforation):
        """Test to check that the first_perforation property returns the correct completion"""
        # Arrange
        completion_1 = NexusCompletion(date='01/02/2023', i=1, j=2, k=3, skin=None, well_radius=4.5, angle_v=None, grid='GRID1',
                      partial_perf=0.1, date_format=DateFormat.DD_MM_YYYY),
        completion_2 = NexusCompletion(date='01/01/2023', i=1, j=2, k=3, well_radius=9.11, partial_perf=0.5,
                      date_format=DateFormat.DD_MM_YYYY)

        completions = [completion_1, completion_2]

        well = NexusWell(well_name='test well', completions=completions,
                         unit_system=UnitSystem.ENGLISH)

        expected_perforation = completion2

        # Act
        result = well.first_perforation

        # Assert
        assert result == expected_perforation

Running tests and other checks
^^^^^^^^^^^^^

You should run all the unit tests and checks on your local machine before submitting a pull request.

You can run the tests against your local clone of the codebase
from the command line when running inside the Poetry shell:

.. code:: bash

    pytest tests

There are several command line options that can be appended, for example:

.. code:: bash

    pytest -k foobar  # selects just tests with "foobar" in the name
    pytest -rA        # prints summary of all executed tests at end

Running Other Checks on your local machine.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
We also run various type checkers, linters and static analysis to ensure high code quality. You can run these checks
yourself on your local machine using the following commands in the poetry shell:

.. code:: bash

    flake8 ResSimpy --append-config ./.config/flake8
    mypy ResSimpy --config-file ./.config/mypy
    ruff check ResSimpy

A shell script ``run_all_checks.sh`` has been provided for your convenience to allow you to run all the checks at the same
time inside the poetry shell if you wish to.

Other Considerations
^^^^^^^^^^^^^^^^^^^^
Please be aware that all keywords / trademarks used on this project need the full legal approval of the trademark holder.
If we receive a PR that contains a keyword or trademark that does not have such an approval we will not be able to accept
it without an advanced approval to use that word.

Get in touch
------------

For bug reports and feature requests, please use the GitHub issue page.