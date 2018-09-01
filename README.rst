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

**HIRE** was written in Python (Python>=3.6) and developed at the `Environmental Change Institute,
University of Oxford <http://www.eci.ox.ac.uk>`_ within the
EPSRC sponsored MISTRAL programme, as part of the `Infrastructure Transition
Research Consortium <http://www.itrc.org.uk/>`_.

More information on the model can be found in Eggimann, Hall and Eyre (2018). Please use 
this reference for citing HIRE.

1. Initialising and running the model (local)
=============================================
The recommended installation method is to use `conda <http://conda.pydata.org/miniconda.html>`_,
which handles packages and virtual environments. First, create a conda environment

    conda create --name energy_demand python=3.6

and activate it

    activate energy_demand

In order to run HIRE, first the model needs to be set up (Section 1.1 or Section 1.1).

1.1 Model Set-Up (with complete data)
-------------------------------------

1.  Add all necessary data into a local directory such as ``path/to/energy_data_folder`` and
    download the energy_demand python code.

    Note: Because some data is not open source, the full data needs to be optained
    from the consortium. However, the model can be run with dummy data (see Section 1.2)

2.  Update the paths in the ``wrapperconfig.ini`` file in the config folder

3.  Navigate to the folder where the python code is saved. Open a command and type into
    a command line (in a virtual environment):
 
    ``python setup.py develop``

4.  Install HIRE from within the console with the command

    ``energy_demand setup -d path/to/energy_data_folder``

    The ``path/to/energy_data_folder`` is the path to the location with
    the necessary data to run the model.

    Note: The ``setup`` command generates new subfolders in the 
    ``energy_data_folder``.


1.2 Alternative Model Set-Up (with restricted data)
---------------------------------------------

1.  Add the minimum data requirements into a local directory as ``path/to/energy_data_folder`` and
    download the energy_demand python code.

2.  Update the paths in the ``wrapperconfig.ini`` file in the config folder

3.  Navigate to the folder where the python code is saved. Open a command and type into
    a command line (in a virtual environment):

    ``python setup.py develop``

4.  Install HIRE from within the console with the command

    ``energy_demand minimal_setup -d path/to/energy_data_folder``

    Example: energy_demand minimal_setup -d  C:/Users/fred1234/data_energy_demand

    The ``path/to/energy_data_folder`` is the path to the location with
    the necessary minimum dummy data to run the model.

    Note: The ``minimal_setup`` command generates new folders in the 
    ``energy_data_folder``.

2. Running the model with smif
================================================

1. Set up the model as outlined in 1.1 'Model Set-Up'

2. Install and set-up smif (see instructions `here <https://github.com/nismod/smif>`_)

3. pip install ``energy_demand``

4. Run the energy demand model for a scenario with 
   the command: ``smif run NAME_SCENARIO``

   For an overview of all possible scenario and their explanation,
   see here `here <https://LINKTOBEDFINED.htm>`_

    To change the logger level of an individual sector model with smif, type:

    ``smif -v run modelrun_id`` or ``smif -vv run modelrun_id``


3. Generating plots based from simulation results
================================================
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


4. Explanation of other scripts
=============================================

``scripts/smif_data_related/generate_data_version.py``: With the file an automatic packaging 
of all necessary data to back up a new data version.

``scripts/smif_data_related/script_data_preparation_MISTRAL_pop_gva.py``: This file generates 
setor specific GVA data and popluation data (it is executed in the ``energy_demand setup`` command)
    