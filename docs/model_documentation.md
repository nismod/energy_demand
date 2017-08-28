
Model Documentation
===================

## Overview


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

## Energy demand simulation

Total energy demand of a (simulation) year (![equation](https://latex.codecogs.com/gif.latex?ED_%7By%7D%5E%7Btot%7D "ED_{y}^{tot}")) is calculated over all regions (r), sectors (s), end-uses (e), technologies (t) and fuel-types (f) as follows:


![equation](https://latex.codecogs.com/gif.latex?ED_%7By%7D%5E%7Btot%7D%20%3D%20%5Csum_%7Br%7D%20%5Csum_%7Bs%7D%5Csum_%7Be%7D%5Csum_%7Bt%7D%5Csum_%7Bf%7DED_%7BSD%7D%20&plus;%20ED_%7Beff%7D%20&plus;%20ED_%7Btech%7D%20&plus;%20ED_%7Bclimate%7D%20&plus;%20ED_%7Bbehaviour%7D "ED_{y}^{tot} = \sum_{r} \sum_{s}\sum_{e}\sum_{t}\sum_{f}ED_{SD} + ED_{eff} + ED_{tech} + ED_{climate} + ED_{behaviour}")

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;![equation](https://latex.codecogs.com/gif.latex?ED_%7BSD%7D "ED_{SD}: "):        Demand change related to change in scenario driver (SD)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;![equation](https://latex.codecogs.com/gif.latex?ED_%7Beff%7D "ED_{eff}"):      Demand change related to change in technology efficiency

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;![equation](https://latex.codecogs.com/gif.latex?ED_%7Btech%7D "ED_{tech}"):      Demand change related to change in technology mix

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;![equation](https://latex.codecogs.com/gif.latex?ED_%7Bclimate%7D "ED_{climate}"):  Demand change related to change in climate

![equation](https://latex.codecogs.com/gif.latex?ED_%7Bbehaviour%7D "ED_{behaviour}"):      Demand change related to change in behaviour (e.g. smart meter, base temperatures)

Energy demand change in relation to the base year (by) for end-use specific scenario drivers is defined as follows: 

![equation](https://latex.codecogs.com/gif.latex?ED_%7BSD%7D%20%3D%20%5Cfrac%7BED_%7BSD%7D%5E%7Btot%7D%7D%7BSD%28by%29%7D%20*%20SD%28simulation%20year%29 "ED_{SD} = \frac{ED_{SD}^{tot}}{SD(by)} * SD(simulation year)")

For the residential and service sub-model, SD values are calculated based on a dwelling stock where scenario drivers are calculated either for dwellings or a group of dwelling (e.g. dwelling types).


<table align="center">
  <tr>
    <th align="left">Scenario Driver</th>
    <th align="left">Enduse(s)</th>
  </tr>
  <tr>
    <td>Floor Area</td>
    <td>Space heating, lighting</td>
  </tr>
  <tr>
    <td>Heating Degree Days</td>
    <td>Space heating</td>
  </tr>
  <tr>
    <td>Cooling degree Days</td>
    <td>Cooling and Ventilation</td>
  </tr>
    <tr>
    <td>Population</td>
    <td>Water heating, cooking, appliances ...</td>
  </tr>
    <tr>
    <td>GVA</td>
    <td>Enduses in industry submodel, appliances</td>
  </tr>
</table>

*Table 1: End-use specific scenario drivers for energy demand*



## 3. Model integration

This section explains how the energy demand and energy supply model interact.

### 3.1 Energy supply and demand model

Lorem ipsum...
![Image of model integration](../docs/documentation_images/001-Supply_and_demand_overview.png)
*Figure 1: Interaction*

### 3.2 Optimised and constrained model run

Lorem ipsum...

![Two modes](../docs/documentation_images/002-constrained_optimised_modes.png)
*Figure 2: Interaction*

## 4. Virtual Building Stock

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam eu mi placerat, ultricies urna id, pharetra dui. Mauris quis mi sit amet sem eleifend sagittis. Nulla at malesuada magna, sit amet placerat dui. Suspendisse potenti. Sed non elit euismod, dapib

## 5.0 Model Parameters

### 5.1 General model parameters

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam eu mi placerat, ultricies urna id, pharetra dui. Mauris quis mi sit amet sem eleifend sagittis. Nulla at malesuada magna, sit amet placerat dui. Suspendisse potenti. Sed non elit euismod, dapibus sapien eu, scelerisque nisi. Duis euismod enim eu mi vestibulum tristique. Nulla lacinia turpis vitae mattis iaculis. Phasellus venenatis nisi diam, fringilla tempus neque tincidunt et. Aenean odio dui, interdum a libero a, cursus pharetra lacus. Ut 

#### 5.1.1 Technologies

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam eu mi placerat, ultricies urna id, pharetra dui. Mauris quis mi sit amet sem eleifend sagittis. Nulla at malesuada magna, sit amet placerat dui. Suspendisse potenti. Sed non elit euismod, dapibus sapien eu, scelerisque nisi. Duis euismod enim eu mi vestibulum tristique. Nulla lacinia turpis vitae mattis iaculis. Phasellus venenatis nisi diam, fringilla tempus neque tincidunt et. Aenean odio dui, interdum a libero a, cursus pharetra lacus. Ut 

#### 5.1.2 Load profiles

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam eu mi placerat, ultricies urna id, pharetra dui. Mauris quis mi sit amet sem eleifend sagittis. Nulla at malesuada magna, sit amet placerat dui. Suspendisse potenti. Sed non elit euismod, dapibus sapien eu, scelerisque nisi. Duis euismod enim eu mi vestibulum tristique. Nulla lacinia turpis vitae mattis iaculis. Phasellus venenatis nisi diam, fringilla tempus neque tincidunt et. Aenean odio dui, interdum a libero a, cursus pharetra lacus. Ut 

#### 5.1.3 Base year fuel assignement

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam eu mi placerat, ultricies urna id, pharetra dui. Mauris quis mi sit amet sem eleifend sagittis. Nulla at malesuada magna, sit amet placerat dui. Suspendisse potenti. Sed non elit euismod, dapibus sapien eu, scelerisque nisi. Duis euismod enim eu mi vestibulum tristique. Nulla lacinia turpis vitae mattis iaculis. Phasellus venenatis nisi diam, fringilla tempus neque tincidunt et. Aenean odio dui, interdum a libero a, cursus pharetra lacus. Ut Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam eu mi placerat, ultricies urna id, pharetra dui. Mauris quis mi sit amet sem eleifend sagittis. Nulla at malesuada magna, sit amet placerat dui. Suspendisse potenti. Sed non elit euismod, dapibus sapien eu, scelerisque nisi. Duis euismod enim eu mi vestibulum tristique. Nulla lacinia turpis vitae mattis iaculis. Phasellus venenatis nisi diam, fringilla tempus neque tincidunt et. Aenean odio dui, interdum a libero a, cursus pharetra lacus. Ut 

### 5.2 Scenario input parameters
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam eu mi placerat, ultricies urna id, pharetra dui. Mauris quis mi sit amet sem eleifend sagittis. Nulla at malesuada magna, sit amet placerat dui. Suspendisse potenti. Sed non elit euismod, dapibus sapien eu, scelerisque nisi. Duis euismod enim eu mi vestibulum tristique. Nulla lacinia turpis vitae mattis iaculis. Phasellus venenatis nisi diam, fringilla tempus neque tincidunt et. Aenean odio dui, interdum a libero a, cursus pharetra lacus. Ut 

## 6. Disaggregation
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam eu mi placerat, ultricies urna id, pharetra dui. Mauris quis mi sit amet sem eleifend sagittis. Nulla at malesuada magna, sit amet placerat dui. Suspendisse potenti. Sed non elit euismod, dapibus sapien eu, scelerisque nisi. Duis euismod enim eu mi vestibulum tristique. Nulla lacinia turpis vitae mattis iaculis. Phasellus venenatis nisi diam, fringilla tempus neque tincidunt et. Aenean odio dui, interdum a libero a, cursus pharetra lacus. Ut 

### 6.1 Temporal disaggregation

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam eu mi placerat, ultricies urna id, pharetra dui. Mauris quis mi sit amet sem eleifend sagittis. Nulla at malesuada magna, sit amet placerat dui. Suspendisse potenti. Sed non elit euismod, dapibus sapien eu, scelerisque nisi. Duis euismod enim eu mi vestibulum tristique. Nulla lacinia turpis vitae mattis iaculis. Phasellus venenatis nisi diam, fringilla tempus neque tincidunt et. Aenean odio dui, interdum a libero a, cursus pharetra lacus. Ut 

### 6.2 Spatial disaggregation

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam eu mi placerat, ultricies urna id, pharetra dui. Mauris quis mi sit amet sem eleifend sagittis. Nulla at malesuada magna, sit amet placerat dui. Suspendisse potenti. Sed non elit euismod, dapibus sapien eu, scelerisque nisi. Duis euismod enim eu mi vestibulum tristique. Nulla lacinia turpis vitae mattis iaculis. Phasellus venenatis nisi diam, fringilla tempus neque tincidunt et. Aenean odio dui, interdum a libero a, cursus pharetra lacus. Ut 

## 10. Reading the code

This section provides an overview of how to read the code.

### 10.1 Abbreviations

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

### 10.2 Load profiles annotation

> `y`:  Total demand in a year

> `yd`: 'Yearly load profile' - Profile for every day in a year of total yearly demand(365)

> `yh`: 'Daily load profile'  - Profile for every hour in a year of total yearly demand (365, 24)

> `dh`: Load profile of a single day

> `y_dh`: Daily load profile within each day (365, 25). Within each day, sums up to 1.0


## 11.Technologies

Based on ECUK() different technologies are assigned to enduses. Efficiencies are 

### 11.1 Residential sector

<table align="center">
  <tr>
    <th align="left">Enduse</th>
    <th align="left">Technologies</th>
  </tr>
  <tr>
    <td>Wet</td>
    <td>Washing machine, tubmle dryer, dishwasher, washer dryer</td>
  </tr>
  <tr>
    <td>Cooking</td>
    <td>Oven, Standard hub (different fueltypes), Induction hob</td>
  </tr>
  <tr>
    <td>Cold</td>
    <td>Chest freezer, Fridge freezer, Refrigerator, Upright freezer</td>
  </tr>
    <tr>
    <td>Lighting</td>
    <td>Light bulb (incandescent), Halogen, Light saving, Fluorescent, LED</td>
  </tr>
    <tr>
    <td>Space and Water Heating</td>
    <td>Boiler (different fueltypes), Condensing boiler, ASHP, GSHP, Micro-CHP, Fuel cell, Storage heating, Night storage</td>
  </tr>
    <tr>
    <td>Wet</td>
    <td>heater, Heat network generation technologies (CHP,...)</td>
  </tr>
</table>

*Table 2: Technology assignement to enduses*

## 12 Used Data Sets

This section provides an overview of all used datasets in HIRE and necessary data preparation.

### 12.1 National Energy Data

The base year energy consumption of the UK (ECUK) in terms of fuels and technology shares for the residential, service and industry sectors is taken from the Department for Business, Energy and Industrial Strategy ([BEIS, 2016](https://www.gov.uk/government/collections/energy-consumption-in-the-uk)). National final energy data is provided for 6 fuel types (solid fuel, gas, electricity, oil, heat sold, bioenergy and waste) in the unit of ktoe (tonne of oil equivalents). All energy unit conversions are based on the unit converter by the International Energy Agency ([IEA, 2017](http://www.iea.org/statistics/resources/unitconverter)).


### 12.2 Household Electricity Servey

The [Household Electricity Survey (HES)](https://www.gov.uk/government/collections/household-electricity-survey) is the most detailed monitoring of electricity use ever carried out in the UK.
Electricity consumption was monitored at an appliance level in 250 owner-occupied households across England from 2010 to 2011. The load profiles for different residential enduses are taken from a [24 hour spreadsheet tool](https://www.gov.uk/government/publications/spreadsheet-tools-for-users).

> **Data preparation**
>
> Monthly load profiles were taken from a 24 hours preadsheet tool and aggregated on an hourly basis.


### 12.3 Carbon Trust advanced metering trial

Metering trial for electricity and gas use across different sectors for businesses (service sector).

 - [More information](http://data.ukedc.rl.ac.uk/simplebrowse/edc/efficiency/residential/Buildings/AdvancedMeteringTrial_2006/)

 - Carbon Trust (2007). Advanced metering for SMEs Carbon and cost savings. Retrieved from >z
   [https://www.carbontrust.com/media/77244/ctc713_advanced_metering_for_smes.pdf](https://www.carbontrust.com/media/77244/ctc713_advanced_metering_for_smes.pdf)

### 12.4 Temperature data

To calculate regional daily hourly load heating profiles, hourly temperature data are used from the [UK Met Office (2015)](http://catalogue.ceda.ac.uk/uuid/916ac4bbc46f7685ae9a5e10451bae7c.) and loaded for weather stations across the UK.

## Literature

BEIS (2016): Energy consumption in the UK (ECUK). London, UK. Available at: [https://www.gov.uk/government/collections/energy-consumption-in-the-uk](https://www.gov.uk/government/collections/energy-consumption-in-the-uk)

UK Met Office (2015): ‘MIDAS: UK hourly weather observation data’. Centre for Environmental Data Analysis. Available    at: [http://catalogue.ceda.ac.uk/uuid/916ac4bbc46f7685ae9a5e10451bae7c](http://catalogue.ceda.ac.uk/uuid/916ac4bbc46f7685ae9a5e10451bae7c).