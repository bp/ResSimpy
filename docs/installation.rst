Installation
============

resqpy is written for Python 3.10+.

You can install the library using pip:

.. code-block:: bash

	$ pip install ResSimpy

To install a development version on your local machine, use:

.. code-block:: bash

	$ pip install -e /path/to/working/copy

To build the documentation locally (requires sphinx):

.. code-block:: bash

	$ sphinx-apidoc -f -o docs/source ResSimpy
	$ cd docs 
	$ .\make html
