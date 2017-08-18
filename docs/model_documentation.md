
Model Documentation
===================

## 1. Overview

The energy demand model of the ITRC-MISTRAL framework allows 
the simulation of long-term changes in energy demand patterns
for the residential, service and industry sector on a high temporal
and spatial scale. National end-use specific energy demand data is
disaggregated on local authority district level and a bottom-up approach
is implemented for hourly energy demand estimation for different fuel types
and end-uses. 
Future energy demand is simulated based on different
socio-technical scenario assumptions such as technology efficiencies,
changes in the technological mix per end-use consumptions or behavioural change.
Energy demand is simulated in relation to changes in scenario drivers of the
base year. End-use specific socio-technical drivers for energy demands
are defined and modelled where possible on a household level.

The energy demand model integrates energy demands across
all ITRC models and provides demands to the supply model.

### 1.1 Core concept 1


This summation expression $\sum_{i=1}^n X_i$ appears inline.


## 2. Model integration


## 2.1 Energy supply and demand model

LORBEM IPSUMLORBEM IPSUMLORBEM IPSUMLORBEM IPSUM
![Image of model integration](../docs/documentation_images/001-Supply_and_demand_overview.png)

## 2.2 Optimised and constrained model run

LORBEM IPSUMLORBEM IPSUMLORBEM IPSUMLORBEM IPSUM

![Two modes](../docs/documentation_images/002-constrained_optimised_modes.png)



Reading the code
===================

## Abbreviations

    rs:     Residential Submodel
    ss:     Srvice Submodel
    ts:     Transportation Submodel

    bd:     Base demand
    by = Base year
    cy = Current year
    dw = dwelling
    p  = Percent
    e  = electricitiy
    g  = gas
    lu = look up
    h = hour
    hp = heat pump
    tech = technology
    temp = temperature
    d = day
    y = year
    yearday = Day in a year ranging from 0 to 364

## Shapes

yd = for every year the day
yh = for every hour in a year
dh = every hour in day
y = for total year
y_dh = for every day in a year, the dh is provided

Data
===================

## Household Electricity Servey

    The Household Electricity Survey (HES) was the most detailed monitoring of electricity use ever carried out in the UK.
    Electricity consumption was monitored at an appliance level in 250 owner-occupied households across England from 2010 to 2011.

    **More information**:
    https://www.gov.uk/government/collections/household-electricity-survey 
    https://www.gov.uk/government/publications/spreadsheet-tools-for-users (24 hour spreadsheet tool)

    **Data preparation**

    Monthly load profiles were taken from a 24 hours preadsheet tool and aggregated on an hourly basis.
    

## Carbon Trust advanced metering trial

    Metering trial for electricity and gas use across different sectors for businesses (service sector).

    More information:

    http://data.ukedc.rl.ac.uk/simplebrowse/edc/efficiency/residential/Buildings/AdvancedMeteringTrial_2006/
    
    Carbon Trust (2007). Advanced metering for SMEs Carbon and cost savings.
    Retrieved from https://www.carbontrust.com/media/77244/ctc713_advanced_metering_for_smes.pdf

