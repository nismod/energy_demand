.. _readme:

====
High Resolution Energy Demand Model
====

SUBBILBE

Description
===========


Description
--------------------

BLABLABLA

    # THIS IS NOW IN A GREY BOX
    
HIRE
=======================

**HIRE** is written in Python (Python>=3.6).





Data
----

1. **Household Electricity Servey**

    The Household Electricity Survey (HES) was the most detailed monitoring of electricity use ever carried out in the UK.
    Electricity consumption was monitored at an appliance level in 250 owner-occupied households across England from 2010 to 2011.

    **More information**:
    https://www.gov.uk/government/collections/household-electricity-survey 
    https://www.gov.uk/government/publications/spreadsheet-tools-for-users (24 hour spreadsheet tool)

    **Data preparation**

    Monthly load profiles were taken from a 24 hours preadsheet tool and aggregated on an hourly basis.
    

2. **Carbon Trust advanced metering trial**

    Metering trial for electricity and gas use across different sectors for businesses (service sector).

    More information:

    http://data.ukedc.rl.ac.uk/simplebrowse/edc/efficiency/residential/Buildings/AdvancedMeteringTrial_2006/
    
    Carbon Trust (2007). Advanced metering for SMEs Carbon and cost savings.
    Retrieved from https://www.carbontrust.com/media/77244/ctc713_advanced_metering_for_smes.pdf


    
    **Data cleaning**

    Removed minus values and filled missing values, removed one or two lines with more values (meausring errors?
    (some entries have huge minus values? Some have more than 48 measurements?)

    Only those datasets are used which cover full years!!

    THE VALUES ARE AGGREGATED ONLY ON A MONTHLY BASES AS TO FEW DATASETS COVER FULL YEARS



Energy Demand and Energy Supply Interaction
=======================
The linkages between the energy demand and energy supply 
modelled are shown below. All other model interlinkages 
are also visualised.


.. class:: no-web

    .. image:: https://github.com/nismod/energy_demand/blob/master/docs/documentation_images/001-Supply_and_demand_overview.jpg
        :alt:
        :width: 100%
        :align: center

.. class:: no-web no-pdf

The energy demand and energy supply model can be run in an optimised and constrained version. The difference between the two modes is visualised below.

.. class:: no-web

    .. image:: https://github.com/nismod/energy_demand/blob/master/docs/documentation_images/002-constrained_optimised_modes.jpg
        :alt:
        :width: 60%
        :align: center

.. class:: no-web no-pdf


A word from our sponsors
========================

**HIRE** was written and developed at the `Environmental Change Institute,
University of Oxford <http://www.eci.ox.ac.uk>`_ within the
EPSRC sponsored MISTRAL programme, as part of the `Infrastructure Transition
Research Consortium <http://www.itrc.org.uk/>`_.
