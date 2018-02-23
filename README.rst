.. _readme:


High Resolution Energy Demand Model
====================================
.. image:: https://img.shields.io/badge/docs-latest-brightgreen.svg
    :target: http://ed.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://travis-ci.org/nismod/energy_demand.svg?branch=master 
    :target: https://travis-ci.org/nismod/energy_demand

.. image:: https://coveralls.io/repos/github/nismod/energy_demand/badge.svg?branch=master
    :target: https://coveralls.io/github/nismod/energy_demand?branch=master


*(click on the 'docs' button to get directed to the full model documentation)*


**HIRE** was written and developed at the `Environmental Change Institute,
University of Oxford <http://www.eci.ox.ac.uk>`_ within the
EPSRC sponsored MISTRAL programme, as part of the `Infrastructure Transition
Research Consortium <http://www.itrc.org.uk/>`_.

A full model description can be found `here <http://ed.readthedocs.io/en/latest/?badge=latest>`_.

The research behind the model witih the MISTRAL
modelling context is documented in:

- Eggimann et al. (2019): Modelling energy demand and supply
  within a system-of-systems appraoch. (working paper)


Note: A previous energy demand model has been developped within
`NISMOD <http://www.itrc.org.uk/nismod/#.WfCJg1tSxaQ>`_ by Pranab et al. 2014. 
HIRE is an extensive development into a high temporal and spatial 
energy demand model simulation.



1. Initialising and running the model (local)
========================
**HIRE** is written in Python (Python>=3.6). In order to run HIRE,
first the model needs to be set up one (Section 1.1). The scenario Set-up need to be
run every time the model is run with different assumptions (Section 1.2).

1.1 Model Set-Up (with complete data)
---------------------------------------------

1.  Add all necessary data into a local directory as ``path/to/energy_data_folder`` and
    download the energy_demand python code.

   Note: Because some data is not open source, the full data needs to be optained
   from the consortium. However, the model can be run with dummy data (see Section 1.2)


2. Navigate to the folder where the python code is saved. Open a command and type into
   a command line (in a virtual environment):

   ``python setup.py develop``

3. Install HIRE from within the console with the command

   ``energy_demand post_install_setup -d path/to/energy_data_folder``

   The ``path/to/energy_data_folder`` is the path to the location with
   the necessary data to run the model.

   Note: The `post_install_setup` generates new folders in the 
   ``energy_data_folder``.

1.2 Alternative Model Set-Up (with restricted data)
---------------------------------------------

1.  Add the minimum data requirements into a local directory as ``path/to/energy_data_folder`` and
    download the energy_demand python code.

2. Navigate to the folder where the python code is saved. Open a command and type into
   a command line (in a virtual environment):

   ``python setup.py develop``

3. Install HIRE from within the console with the command

   ``energy_demand post_install_setup_minimum -d1 path/to/energy_data_folder -d2 path/to/python_files``

   Example:
    energy_demand post_install_setup_minimum -d1  C:/Users/cenv0553/nismod/data_energy_demand -d2 C:/Users/cenv0553/nismod/models/energy_demand

   The ``path/to/energy_data_folder`` is the path to the location with
   the necessary minimum dummy data to run the model.

   Note: The `post_install_setup_minimum` generates new folders in the 
   ``energy_data_folder``.

2. Running the model with smif
========================

1. Set up the model as outlined in 1.1 'Model Set-Up'

2. Install and set-up smif (see instructions `here <https://github.com/nismod/smif>`_)

3. Run the the energy demand model for a scenario with 
   the command: ``smif run NAME_SCENARIO``

   For an overview of all possible scenario and their explanation,
   see here `here <https://LINKTOBEDFINED.htm>`_

Other help
==========
To change the logger level of an individual sector model with smif, type:

``smif -v run modelrun_id`` or ``smif -vv run modelrun_id``

Literature
========================
Baruah, P., Eyre, N., Qadrdan, M., Chaudry, M., Blainey, S., Hall, J. W., … Tran, M. (2014). Energy
system impacts from heat and transport electrification. Proceedings of the ICE - Energy, 
167(3), 139–151. https://doi.org/10.1680/ener.14.00008
