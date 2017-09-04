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

Navigate to the folder with the python code. Open a command and type in

``setup.py develop``

Install the energy demand model from the console with the command

``energy_demand post_install_setup -d path/to/energy_data_folder``

Initialise for every scenario from the command

``energy_demand scenario_initialisation -d2 path/to/energy_data_folder``

Note: The processed data folder gets generated upon the ``post_install_setup``
and is stored in the same folder as the path/to/data

Run the energy demand model from the console with the command

``energy_demand run -d path/to/data``



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
