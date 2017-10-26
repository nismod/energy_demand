.. _readme:


High Resolution Energy Demand Model
====================================
**HIRE** was written and developed at the `Environmental Change Institute,
University of Oxford <http://www.eci.ox.ac.uk>`_ within the
EPSRC sponsored MISTRAL programme, as part of the `Infrastructure Transition
Research Consortium <http://www.itrc.org.uk/>`_.

A full model description can be found here <http://ed.readthedocs.io/en/latest/?badge=latest>.

The research behind the model witih the MISTRAL
modelling context is documented in:

    - Eggimann et al. (2018): Modelling energy demand and supply
    within a system-of-systems appraoch. (working paper)


Note: A previous energy demand model has been developped within
NISMOD <http://www.itrc.org.uk/nismod/#.WfCJg1tSxaQ> by Pranab et al. 2014. 
HIRE is an extensive development into a high temporal and spatial 
energy demand model simulation.


.. image:: https://img.shields.io/badge/docs-latest-brightgreen.svg
    :target: http://ed.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://travis-ci.org/nismod/energy_demand.svg?branch=master 
    :target: https://travis-ci.org/nismod/energy_demand

.. image:: https://coveralls.io/repos/github/nismod/energy_demand/badge.svg
    :target: https://coveralls.io/github/nismod/energy_demand

*(click on the 'docs' button to get directed to the full model documentation)*

Running the model (local)
========================
**HIRE** is written in Python (Python>=3.6). In order to run HIRE,
the following steps are necessary. Step 1, 2 and 3 only needs to be
executed to set-up the model. Step 4 and 5 need to be run every time
the model is run with different assumptions.

Model Set-Up
-------------

```
1. Add all necessary HIRE data into a local directory as ``path/to/energy_data_folder`` and
   download the energy_demand python code.

   Note: Because some data is not open source, the full data needs to be optained
   from the consortium. Please contact XY.


2. Navigate to the folder where the python code is saved. Open a command and type into
   a command line (in a virtual environment):

   ``setup.py develop``

3. Install HIRE from within the console with the command

   ``energy_demand post_install_setup -d path/to/energy_data_folder``

   The ``path/to/energy_data_folder`` is the path to the location with
   the necessary data to run the model.

   Note: The `post_install_setup` generates new folders in the 
   ``energy_data_folder``.
```

Scenario Set-up 
----------------

```
4. For every scenario run, the energy demand module needs to be
   initialised from the command line as follows:

   ``energy_demand scenario_initialisation -d path/to/energy_data_folder``

   Note: Upon scenario initialisation, data gets saved in the ``_process_data`` 
   folder which contain assumption specific data.

5. Run the model from the console with the command

   ``energy_demand run -d path/to/energy_data_folder``
```

Running the model with smif
========================

```
Describe...
```

Literature
========================
Baruah, P., Eyre, N., Qadrdan, M., Chaudry, M., Blainey, S., Hall, J. W., … Tran, M. (2014). Energy
system impacts from heat and transport electrification. Proceedings of the ICE - Energy, 
167(3), 139–151. https://doi.org/10.1680/ener.14.00008


