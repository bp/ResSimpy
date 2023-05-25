Getting started
===============

.. code-block:: python

    >>> from ResSimpy import NexusSimulator

A first step is typically to instantiate a :class:`Simulator` object, passing in the location of the model you wish to work with. Here a Nexus Simulator model is instantiated.:

.. code-block:: python

    >>> model = NexusSimulator(origin=r'<address of model>')

You are then able to access and modify parts of the model as you wish. For example, to view an overview of all of the wells in a model you could call:

.. code-block:: python

    >>> print(model.Wells.get_wells_overview())
	
The full list of API calls available to you can be found in this documentation.