.. _readme:

HIgh-Resolution Energy demand model (HIRE)
====================================
.. image:: https://img.shields.io/badge/docs-latest-brightgreen.svg
    :target: http://ed.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://travis-ci.org/nismod/energy_demand.svg?branch=master 
    :target: https://travis-ci.org/nismod/energy_demand

.. image:: https://coveralls.io/repos/github/nismod/energy_demand/badge.svg?branch=master
    :target: https://coveralls.io/github/nismod/energy_demand?branch=master

.. image:: https://zenodo.org/badge/72533183.svg
   :target: https://zenodo.org/badge/latestdoi/72533183

**HIRE** was written in Python (Python>=3.6) and developed at the `Environmental Change Institute,
University of Oxford <http://www.eci.ox.ac.uk>`_ within the
EPSRC sponsored MISTRAL programme, as part of the `Infrastructure Transition
Research Consortium <http://www.itrc.org.uk/>`_.

More information on the model can be found in:

    Eggimann, S., Hall, W.J., Eyre, N. (2019): A high-resolution spatio-temporal
    energy demand simulation of large-scale heat pump diffusion to explore the
    potential of heating demand side management. Applied Energy, 236, 997–1010.
    `https://doi.org/10.1016/j.apenergy.2018.12.052 <https://doi.org/10.1016/j.apenergy.2018.12.052>`_.


1. Download input data
-------------------------------------
Most data for running HIRE are freely available online. For some input data it is necessary to request access.
For more information on all necessary input datasets see `here <https://ed.readthedocs.io/en/latest/documentation.html#data-sets>`_)

All necessary input data to run HIRE can be downloaded (`here <TODO_DATA_LINK>`_), where
for the restricted datasets a dummy input dataset is used instead.

For data inquires, plese contact sven.eggimann@ouce.ox.ac.uk or `the consortium <https://www.itrc.org.uk/contact-us/>`_).
Also check whether data area available `here <https://www.nismod.ac.uk>`_.

2. Initialising and running the model (local)
-------------------------------------
The recommended installation method is to use `conda <http://conda.pydata.org/miniconda.html>`_,
which handles packages and virtual environments. First, create a conda environment

    conda create --name energy_demand python=3.6

and activate it

    activate energy_demand

In order to run HIRE, first the model needs to be set up (Section 1.1 or Section 1.1).

2.1 Model Set-Up (with complete data)
-------------------------------------

1.  Add all necessary data into a local directory such as ``path/to/energy_data_folder`` and
    download the energy_demand python code.

    Note: Because some data is not open source, the full data needs to be optained
    from the consortium. However, the model can be run with dummy data (see Section 1)

2.  Update the paths in the ``wrapperconfig.ini`` file in the config folder

3.  Navigate to the folder where the python code is saved. Open a command and type into
    a command line (in a virtual environment):
 
    ``python setup.py develop``

4.  Install HIRE from within the console with the command

    ``energy_demand setup -f path/to/config.ini``

    The ``path/to/energy_data_folder`` is the path to the location with
    the necessary data to run the model.

    Note: The ``setup`` command generates new subfolders in the 
    ``energy_data_folder``.


2.2 Alternative Model Set-Up (with restricted dummy data)
---------------------------------------------

1.  Add the minimum data requirements into a local directory as ``path/to/energy_data_folder`` and
    download the energy_demand python code.

2.  Update the paths in the ``wrapperconfig.ini`` file in the config folder

3.  Navigate to the folder where the python code is saved. Open a command and type into
    a command line (in a virtual environment):

    ``python setup.py develop``

4.  Install HIRE from within the console with the command

    ``energy_demand minimal_setup -f path/to/config.ini``

    Example: energy_demand minimal_setup -f  C:/Users/fred1234/data_energy_demand

    The ``path/to/energy_data_folder`` is the path to the location with
    the necessary minimum dummy data to run the model.

    Note: The ``minimal_setup`` command generates new folders in the 
    ``energy_data_folder``.

3. Running HIRE with smif
---------------------------------------------

1. Set up the model as outlined in 1.1 'Model Set-Up'

2. Install and set-up smif (see instructions `here <https://github.com/nismod/smif>`_)

3. pip install ``energy_demand``

4. Run the energy demand model for a scenario with 
   the command: ``smif run NAME_SCENARIO``

   For an overview of all possible scenario and their explanation,
   see here `here <https://LINKTOBEDFINED.htm>`_

    To change the logger level of an individual sector model with smif, type:

    ``smif -v run modelrun_id`` or ``smif -vv run modelrun_id``

4. Generating plots based from simulation results
---
Every time a model gets run, the specific model simulation results
are stored in the result folder named after the timestamp of the model execution.

In order to generate plots of the results, the scripts in the 'processing'
folder needs to be used. Proceed as follows:

1. Select all generated result folders for which you want to generate plots.

2. Copy them into an empty folder.

3. Configure the 'energy_demand/processing/multiple_scenarios.py' file,
   namely the arguments of the process_result_multi_scen() function,
   and execute the function.

   This generates all plots in the invidual result folders.

   Note:
   In the 'process_result_multi_scen' function all plots
   which should be generated can be configured
