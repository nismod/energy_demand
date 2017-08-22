
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

### 1.1 Energy demand simulation
Total energy demand of a (simulation) year (![equation](https://latex.codecogs.com/gif.latex?ED_%7By%7D%5E%7Btot%7D "ED_{y}^{tot}")) is calculated over all regions (r), sectors (s), end-uses (e), technologies (t) and fuel-types (f) as follows:


![equation](https://latex.codecogs.com/gif.latex?ED_%7By%7D%5E%7Btot%7D%20%3D%20%5Csum_%7Br%7D%20%5Csum_%7Bs%7D%5Csum_%7Be%7D%5Csum_%7Bt%7D%5Csum_%7Bf%7DED_%7BSD%7D%20&plus;%20ED_%7Beff%7D%20&plus;%20ED_%7Btech%7D%20&plus;%20ED_%7Bclimate%7D%20&plus;%20ED_%7Bbehaviour%7D "ED_{y}^{tot} = \sum_{r} \sum_{s}\sum_{e}\sum_{t}\sum_{f}ED_{SD} + ED_{eff} + ED_{tech} + ED_{climate} + ED_{behaviour}")

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;![equation](https://latex.codecogs.com/gif.latex?ED_%7BSD%7D "ED_{SD}: "):        Demand change related to change in scenario driver (SD)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;![equation](https://latex.codecogs.com/gif.latex?ED_%7Beff%7D "ED_{eff}"):      Demand change related to change in technology efficiency

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;![equation](https://latex.codecogs.com/gif.latex?ED_%7Btech%7D "ED_{tech}"):      Demand change related to change in technology mix

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;![equation](https://latex.codecogs.com/gif.latex?ED_%7Bclimate%7D "ED_{climate}"):  Demand change related to change in climate

![equation](https://latex.codecogs.com/gif.latex?ED_%7Bbehaviour%7D "ED_{behaviour}"):      Demand change related to change in behaviour (e.g. smart meter, base temperatures)

Energy demand change in relation to the base year (by) for end-use specific scenario drivers is defined as follows: 

![equation](https://latex.codecogs.com/gif.latex?ED_%7BSD%7D%20%3D%20%5Cfrac%7BED_%7BSD%7D%5E%7Btot%7D%7D%7BSD%28by%29%7D%20*%20SD%28simulation%20year%29 "ED_{SD} = \frac{ED_{SD}^{tot}}{SD(by)} * SD(simulation year)")


## 2. Model integration


## 2.1 Energy supply and demand model

LORBEM IPSUMLORBEM IPSUMLORBEM IPSUMLORBEM IPSUM
![Image of model integration](../docs/documentation_images/001-Supply_and_demand_overview.png)

## 2.2 Optimised and constrained model run

LORBEM IPSUMLORBEM IPSUMLORBEM IPSUMLORBEM IPSUM

![Two modes](../docs/documentation_images/002-constrained_optimised_modes.png)



10 Reading the code
===================

## 10.1 Abbreviations

Within the code, different abbreviations are consistenly used
across all modules.

    rs:         Residential Submodel
    ss:         Srvice Submodel
    ts:         Transportation Submodel

    bd:         Base demand
    by:         Base year
    cy:         Current year
    dw:         Dwelling
    p:          Fraction, i.e. (100% = 1.0)
    e:          Electricitiy
    g:          Gas
    lu:         Look up

    h:          Hour
    d:          Day
    y:          Year
    yearday:    Day in a year ranging from 0 to 364

    hp:         Heat pump
    tech:       Technology
    temp:       Temperature


## 10.2 Load profiles annotation

> `y`:  Total demand in a year


> `yd`: 'Yearly load profile' - Profile for every day in a year of total yearly demand(365)

> `yh`: 'Daily load profile'  - Profile for every hour in a year of total yearly demand (365, 24)

> `dh`: Load profile of a single day

> `y_dh`: Daily load profile within each day (365, 25). Within each day, sums up to 1.0

11.Data
===================

## 11.1 Household Electricity Servey

The Household Electricity Survey (HES) was the most detailed monitoring of electricity use ever carried out in the UK.
Electricity consumption was monitored at an appliance level in 250 owner-occupied households across England from 2010 to 2011.

- [More information](https://www.gov.uk/government/collections/household-electricity-survey)

- [24 hour spreadsheet tool](https://www.gov.uk/government/publications/spreadsheet-tools-for-users)

**Data preparation**

Monthly load profiles were taken from a 24 hours preadsheet tool and aggregated on an hourly basis.


## 11.2 Carbon Trust advanced metering trial

Metering trial for electricity and gas use across different sectors for businesses (service sector).

>
> - [More information](http://data.ukedc.rl.ac.uk/simplebrowse/edc/efficiency/residential/Buildings/AdvancedMeteringTrial_2006/)
>
> - Carbon Trust (2007). Advanced metering for SMEs Carbon and cost savings. Retrieved from >z
>   [https://www.carbontrust.com/media/77244/ctc713_advanced_metering_for_smes.pdf](https://www.carbontrust.com/media/77244/ctc713_advanced_metering_for_smes.pdf)
