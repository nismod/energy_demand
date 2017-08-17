.. _getting_started:

Getting Started
===============

To specify a system-of-systems model, you must configure one or more simulation
models, outlined in the section below, and configure a system-of-systems
model, as outlined immediately below.

First, setup a new system-of-systems modelling project with the following
folder structure::

        /config
        /planning
        /data
        /models

This folder structure is optional, but helps organise the configuration files,
which can be important as the number and complexity of simulation models
increases.

The ``config`` folder contains the configuration for the system-of-systems
model::

        /config/model.yaml
        /config/timesteps.yaml

The ``planning`` folder contains one file for each ::

        /planning/pre-specified.yaml

The ``data`` folder contains a subfolder for each sector model::

        /data/<sector_model_1>
        /data/<sector_model_2>

The ``/data/<sector_model>`` folder contains all the configuration files for a
particular sector model.  See adding a sector model for more information.::

        /data/<sector_model>/inputs.yaml
        /data/<sector_model>/outputs.yaml
        /data/<sector_model>/time_intervals.yaml
        /data/<sector_model>/regions.geojson
        /data/<sector_model>/interventions.yaml

The ``/models/<sector_model/`` contains the executable for a sector model,
as well as a Python file which implements :class:`smif.sector_model.SectorModel`
and provides a way for `smif` to run the model, and access model outputs.
See adding a sector model for more information.::

       /models/<sector_model>/run.py
       /models/<sector_model>/<executable or library>


Necessary inputs
=================
- Economic data for regions
- 
-


Scenario Drivers
=================
- population (regional demography)
- gross added value
- energy prices
- 





Llighting
=========
- floor area
- 


All other appliances
=========
- population
- gross added value?

'''
----------------------
# RESIDENTIAL END_USES
----------------------

The ECUK table serves as the most important national energy demand input.

[y]   Yearly variation
[h]   Shape of each hour in a day
[d]   Shape of each day in a year
[p_h] Peal Shape of heak day in hours
[p_d] Relationship between demand of peak day and demand in a year

ECUK TABLE FUEL DATA                              Shapes
====================                              ==================
                                                  [y] ?? Wheater Generator

heating (Table 3.8)                 -->           [h,p_h] Sansom (2014) which is based on Carbon Trust field data:
                                                  [d,p_d] National Grid (residential data based on CWW):

Water_heating (Table 3.8)                 -->     [d,h,p_d,p_h] HES: Water heating (shapes for all fuels)

Cooking (Table 3.8)                       -->     [d,h,p_d,p_h] HES: Cooking (shapes for all fuels)

Lighting (Table 3.8)                      -->     [d,h,p_d,p_h] HES: Lighting

Appliances (elec) (Table 3.02)
  cold (table 3.8)                        -->     [d,h,p_d,p_h] HES: Cold appliances
  wet (table 3.8)                         -->     [d,h,p_d,p_h] HES: Washing/drying
  consumer_electronics (table 3.8)        -->     [d,h,p_d,p_h] HES: Audiovisual
  home_computing (table 3.8)              -->     [d,h,p_d,p_h] HES: ICT

----------------------
# Service END_USES
----------------------

ECUK TABLE FUEL DATA                              Shapes
====================                              ==================

Carbon Trust data is for sectors and in electricity and gas

For Elec, individual shapes are used to generate shape
For gas, all gas data cross all sectors is used to generate shape
--> For enduse where both elec and gas are used, take shape of dominant fueltype and use same load shape for other fueltypes

ENDUSE
  Catering
  Computing
  Cooling and ventilation
  Hot water
  Heating
  Lighting
  Other

SECTORS                                           SHAPES
  Community, arts and leisure (individ)    -->    Carbon Trust: Community
  Education (individ)                      -->    Carbon Trust: Education
  Retail (individ)                         -->    Carbon Trust: Retail
  Health (individ)                         -->    Carbon Trust: Health
  Offices (individ)                        -->    Carbon Trust: Offices

  Emergency Services (aggr)                -->    Carbon Trust: Manufacturing, other Sectors ?? (or averaged of all?)
  Hospitality (aggr)
  Military (aggr)
  Storage (aggr)

  TODO: Exclude heating from electricity by contrasting winter/summer
  (excl. heating with summer/winter comparison)
  Select individual load shapes for different sectors where possible (only electricity) (excl. heating with summer/winter comparison)
  For sectors where no carbon trail data relates,use aggregated load curves from carbon trust with: Financial, Government, Manufacturing, other Sectors

SHAPES Elec
Calculate electricity shapes for aggregated and individual sectors:
    [h]    Carbon Trust Metering Trial: averaged daily profily for every month (daytype, month, h)
    [p_h]  Carbon Trust Metering Trial: maximum peak day is selected and daily load shape exported
    [d]    Carbon Trust Metering Trial: Use (daytype, month, h) to distribute over year
    [p_d]  Carbon Trust Metering Trial: Select day with most enduse and compare how relateds to synthetically generated year

SHAPES Gas
Calculate gas shapes across all sectors:
    [h]   Carbon Trust Metering Trial: averaged daily profily for every month
    [p_h] Carbon Trust Metering Trial: the maximum peak day is selected and daily load shape exported
    [p_d] National Grid (non-residential data based on CWW)
    [d]   National Grid (non-residential data based on CWW) used to assign load for every day (then multiply with h shape)

USED SHAPES FOR ENDUSES

Catering (e,g) (Table 5.05)                         -->   Use electricity shape (disaggregate other fueltypes with this shape)

Computing (e) (Table 5.05)                          -->   Use electricity shape

Cooling and Ventilation (mainly e) (Table 5.05)     -->   Use electricity shapes and distribute other fueltypes with this shape
                                                    -->   SHAPE?

Hot Water (e,g) (Table 5.05)                        -->   More gas enduse --> Use gas shape across all sectors and distribute also with it elec.

Heating (mainly g) (Table 5.05)                     -->   Use gas load shape accross all sectors and disaggregate other fuels with this load shape

Lighting (e) (Table 5.05)                           -->   Use electricity shapes

Other (e,g) (Table 5.05)                            -->   Use overall electricity and overall gas curve

'''
