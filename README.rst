.. _readme:


High Resolution Energy Demand Model
====================================
**HIRE** is written in Python (Python>=3.6).

# Very much work in progress

.. image:: https://img.shields.io/badge/docs-latest-brightgreen.svg
    :target: http://ed.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://travis-ci.org/nismod/energy_demand.svg?branch=master 
    :target: https://travis-ci.org/nismod/energy_demand

.. image:: https://coveralls.io/repos/github/nismod/energy_demand/badge.svg
    :target: https://coveralls.io/github/nismod/energy_demand

Running the model
========================

1. Navigate to the folder where the python code is saved. Open a command and type into
a command line:

``setup.py develop``

2. Install the energy demand model from the console with the command

``energy_demand post_install_setup -d path/to/energy_data_folder``

The ``path/to/energy_data_folder`` is the path to the location with
the necessary data to run the model.

Note: The ``post_install_setup`` generates new folders in the 
``energy_data_folder``.

3. For every scenario run, the energy demand module needs to be
initialised from the command line as follows:

``energy_demand scenario_initialisation -d path/to/energy_data_folder``

Note: Upon scenario initialisation, data gets saved in the ``_process_data`` 
folder which contain assumption specific data.

4. Run the energy demand model from the console with the command

``energy_demand run -d path/to/energy_data_folder``

Note: Step 1 and 2 only needs to be execute once, Step 3 and 4 every time
the model is run with different assumptions.

You'll need to python setup.py develop to install the simlink to the package.
You can change the actual command to run this in the setup.cfg file under
the heading console_scripts.
Also, add the data directory as data_files when the package is installed, 
so that the data files are accessible to the library. This needs a bit of extra work, 
but should allow any module within the package to access these data files programmatically, 
ithout having to specify a path. This will also work across platform.


A word from our sponsors
========================

**HIRE** was written and developed at the `Environmental Change Institute,
University of Oxford <http://www.eci.ox.ac.uk>`_ within the
EPSRC sponsored MISTRAL programme, as part of the `Infrastructure Transition
Research Consortium <http://www.itrc.org.uk/>`_.
