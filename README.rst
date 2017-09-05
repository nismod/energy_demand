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

In order to run the model, the following steps are necessary. Step 1, 2 and 3
only needs to be execute once. Step 4 and 5 every time the model is run
with different assumptions.

1. Add the data into a local directory as ``path/to/energy_data_folder`` and
   download the energy_demand python code.


2. Navigate to the folder where the python code is saved. Open a command and type into
   a command line:

   ``setup.py develop``


3. Install the energy demand model from the console with the command

   ``energy_demand post_install_setup -d path/to/energy_data_folder``

   The ``path/to/energy_data_folder`` is the path to the location with
   the necessary data to run the model.

   Note: The `post_install_setup` generates new folders in the 
   ``energy_data_folder``.


4. For every scenario run, the energy demand module needs to be
   initialised from the command line as follows:

   ``energy_demand scenario_initialisation -d path/to/energy_data_folder``

   Note: Upon scenario initialisation, data gets saved in the ``_process_data`` 
   folder which contain assumption specific data.


5. Run the energy demand model from the console with the command

   ``energy_demand run -d path/to/energy_data_folder``


A word from our sponsors
========================

**HIRE** was written and developed at the `Environmental Change Institute,
University of Oxford <http://www.eci.ox.ac.uk>`_ within the
EPSRC sponsored MISTRAL programme, as part of the `Infrastructure Transition
Research Consortium <http://www.itrc.org.uk/>`_.
