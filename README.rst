.. _readme:

====
High Resolution Energy Demand Model
====

SUBBILBE

Description
===========

LOREM IPSUM
    
HIRE
=======================

**HIRE** is written in Python (Python>=3.6).


Residential model
=======================
NOT IN HEADER BUT NEW TITLE

=====                       =====
ECUK Data (Table 5.05)      Carbon Trust Datase
=====                       =====
Community, arts and leisure	Community
Education	                Education
Emergency Services	        Aggregated across all sectors
Health	                    Health
Hospitality	                Aggregated across all sectors
Military	                Aggregated across all sectors
Offices	                    Offices
Retail	                    Retail
Storage	                    Aggregated across all sectors
=====                       =====

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
    

2. Carbon Trust advanced metering trial

    Metering trial for electricity and gas use across different sectors for businesses (service sector).

    More information:
    http://data.ukedc.rl.ac.uk/simplebrowse/edc/efficiency/residential/Buildings/AdvancedMeteringTrial_2006/
    
    Carbon Trust (2007). Advanced metering for SMEs Carbon and cost savings.
    Retrieved from https://www.carbontrust.com/media/77244/ctc713_advanced_metering_for_smes.pdf


    Data preparation
    The sectors of the metering trial were mapped as follows the the different sectors found in the 
    ECUK table:

            ECUK                                Carbon Trust

            Community, arts and leisure         Community
            Education                           Education
            Retail                              Retail
            Health                              Health
            Offices                             Financial & Government

            Emergency Services                  All sector data (excl. other sectors)
            Hospitality                         All sector data (excl. other sectors)
            Military                            All sector data (excl. other sectors)
            Storage                             All sector data (excl. other sectors)
    
    A gas demand load curve is extracted across all sectors. No individual gas curve was possible 
    due to the sample size for all individual sectors. For the first 5 sectors an individual
    electricity load curve was generated. For the emergency service, hopsitality, militars and
    storage sector no individual electricity curve was generated. Instead an electricity curve
    aggregated over all sectors (excl. other sectors) is used.
       
    The dataset does not allow to differentiate between different enduses from the ECUK table.
    The fuel data of the ECUK table 5.05 for the service sector enduses is disaggregated as follows:

    gas fueltype:       Aggregated gas fuel load curve across all sectors
    electricity:        If availalbe, individual electricity load shape
    other fueltypes:    Also electricity shape

    End-Use from ECUK table
    - Catering                
    - Computing                   electricity shape
    - Cooling and Ventilation 
    - Hot Water                   
    - Heating                     gas shape
    - Lighting
    - Other

    Shapes gas (across all sectors)
    The Carbon Trust Meterin Trial data is only used to derive averaged daily profiles and peak day.
    National Grid data (non-residential data based on CWW) is used to assign load for every day

    [h]   Carbon Trust Metering Trial: averaged daily profily for every month
    [p_h] Carbon Trust Metering Trial: the maximum peak day is selected and daily load shape exported
    [p_d] National Grid (non-residential data based on CWW)
    [d]   National Grid (non-residential data based on CWW) used to assign load for every day (then multiply with h shape)

    Note: The carbon trust electricity data contains some electricity for electric heating. Contrasting  electricity use from 
    Januar and July shows that there are differences in electricity consumption in some cases over 20% due to electric heating and lighting.
    Excluding these shares is not possible. For some sectory (e.g. Community, Office) differences are minor. In case better data sources
    become available, the load shapes of the different enduses needs to be improved.

    
    **Data cleaning**

    Removed minus values and filled missing values, removed one or two lines with more values (meausring errors?
    (some entries have huge minus values? Some have more than 48 measurements?)

    Only those datasets are used which cover full years!!

    THE VALUES ARE AGGREGATED ONLY ON A MONTHLY BASES AS TO FEW DATASETS COVER FULL YEARS


Description
--------------------

BLABLABLA

    # THIS IS NOW IN A GREY BOX
    LROBEM

Energy Demand and Energy Supply Interaction
=======================
The linkages between the energy demand and energy supply 
modelled are shown below. All other model interlinkages 
are also visualised.


.. class:: no-web

    .. image:: https://github.com/nismod/energy_demand/tree/master/docs/documentation_images/001-Supply_and_demand_overview.jpgpng
        :alt: Model interlinkages overview
        :width: 100%
        :align: center


.. class:: no-web no-pdf


A word from our sponsors
========================

**HIRE** was written and developed at the `Environmental Change Institute,
University of Oxford <http://www.eci.ox.ac.uk>`_ within the
EPSRC sponsored MISTRAL programme, as part of the `Infrastructure Transition
Research Consortium <http://www.itrc.org.uk/>`_.
