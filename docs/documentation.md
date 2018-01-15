Code Overview
===================
This section provides and overview how the model code is stored.

All model input data used to configure the model is storted in the 
`config_data` folder (i.e. load profiles of technologies,
fuel input data for the whole UK).

The python scripts are stored in the following folders:

- **assumptions** | Model assumptions which need to be configured 
- **basic** | Standard functions
- **charts** | Functions to generate charts
- **cli** | Script to run model from command line
- **dwelling_stock** | Dwelling stock related functions
- ...

All additional data necessary to run the model needs
to be stored in a local folder (`data_energy_demand`).

Documentation
===================

## 1. Introduction


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



## 2. Overview of model and simulation approach

![Model overview](../docs/documentation_images/000-model_overview.jpg)
*Figure XY: Overview of modelled end uses and sectors*


## 3. Main working steps

The main working steps as outlined in Figure XY are explained

### 3.1 Spatial disaggregation

### 3.2 Annual demand simulation

Total energy demand of a (simulation) year (![equation](https://latex.codecogs.com/gif.latex?ED_%7By%7D%5E%7Btot%7D "ED_{y}^{tot}"))is calculated over all regions (r), sectors (s), end-uses (e), technologies (t) and fuel-types (f) as follows:

![equation](https://latex.codecogs.com/gif.latex?ED_%7By%7D%5E%7Btot%7D%20%3D%20%5Csum_%7Br%7D%20%28%5Csum_%7Bs%7D%20%28%5Csum_%7Be%7D%20%28%5Csum_%7Bt%7D%20%28%5Csum_%7Bf%7D%28ED_%7BSD%7D%20&plus;%20ED_%7Beff%7D%20&plus;%20ED_%7Btech%7D%20&plus;%20ED_%7Bclimate%7D%20&plus;%20ED_%7Bbehaviour%7D%29%29%29%29%29 "ED_{y}^{tot} = \sum_{r} (\sum_{s} (\sum_{e} (\sum_{t} (\sum_{f}(ED_{SD} + ED_{eff} + ED_{tech} + ED_{climate} + ED_{behaviour})))))")

![equation](https://latex.codecogs.com/gif.latex?ED_%7BSD%7D "ED_{SD}: "):        Demand change related to change in scenario driver (SD)

![equation](https://latex.codecogs.com/gif.latex?ED_%7Beff%7D "ED_{eff}"):      Demand change related to change in technology efficiency

![equation](https://latex.codecogs.com/gif.latex?ED_%7Btech%7D "ED_{tech}"):      Demand change related to change in technology mix

![equation](https://latex.codecogs.com/gif.latex?ED_%7Bclimate%7D "ED_{climate}"):  Demand change related to change in climate

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

*Table 1.1: End-use specific scenario drivers for energy demand*

![Image of model integration](../docs/documentation_images/004-ULM_main_classes.jpg)
*Figure 3.1: Interaction*

## XY. Model Interaction



### 3.1 Energy supply and demand model

Lorem ipsum...
![Image of model integration](../docs/documentation_images/001-Supply_and_demand_overview.png)
*Figure 3.1: Interaction*

### 3.2 Optimised and constrained model run

Lorem ipsum...

![Two modes](../docs/documentation_images/002-constrained_optimised_modes.png)
*Figure 3.2: Interaction*

## 4. Generic Dwelling Stock Model

A generic dwelling model is implemented in HIRE which can be used in case no external dwelling stock model is available and can provide the necesarry ``dwelling`` inputs. However, instead of modelling every individual building, an abstracted dwelling respresentation of the the complete dwelling stock is modelled based on different simplified assumptions. The modelling steps are as follows for every ``Region`` (see Figure 4.1 for the detailed process flow):

1. Based on base year total population and total floor area, the floor area per person is calculated (``floor_area_pp``). The floor area per person can be changed over the simulation period.

2. Based on the floor area per person and scenario population input, total necessary new and existing floor area is calculated for the simulation year (by substracting the existing floor area of the total new floor area).

3. Based on assumptions on the dwelling type distribution (``assump_dwtype_distr``) the floor area per dwelling type is calculated.

4. Based on assumptions on the age of the dwelling types, different ``Dwelling`` objects are generated. The heat loss coefficient is calculated for every object.

5. Additional dwelling stock related properties can be added to the ``Dwelling`` objects which give
   indication of the energy demand and can be used for calculating the scenario drivers.

Note: The generic dwelling model can be replaced by directly defining the the ``dwelling`` objects, if the dwelling stock information is  information is available from another source.

![Dwelling model](../docs/documentation_images/003-dwelling_model.jpg)
*Figure 4.1: Modelling steps of the residential dwelling module*


## 5.0 Model Parameters

### 5.1 General model parameters

Lorem ipsu

#### 5.1.1 Technologies

Lorem 

#### 5.1.2 Load profiles

Lorem ips

#### 5.1.2 Demand side response and peak shifting

Intraday demand side responses per end use are modelled with help of load factors  (Petchers, 2003).  For every end use, a potential (linear) reduction of the load factor over time can be assumed with which the load factor of the current year is calculated (![equation](https://latex.codecogs.com/gif.latex?lf_%7Bcy%7D "l_{cy}"). With help lfcy, and the daily average load of the base year (l_av^by), the maximum hourly load per day is calculated as follows:

![equation](https://latex.codecogs.com/gif.latex?l_%7Bcy%7D%5E%7Bmax%7D%20%3D%20%5Cfrac%7Bl_%7Bby%7D%5E%7Bav%7D%7D%7Blf_%7Bcy%7D%7D "l_{cy}^{max} = \frac{l_{by}^{av}}{lf_{cy}}")

For all hours with loads higher than the new maximum hourly load, the shiftable load is distributed to all off-peak load hours as shown in Figure XY.

![Peak shiting](../docs/documentation_images/004-peak_shifting.jpg)
*Figure XX: Shifting loads from peak hours to off-peak hours based on load factor changes.*

#### 5.1.3 Base year fuel assignement

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam eu mi placerat, ultricies urna id, pharetra dui. Mauris quis mi sit amet se

### 5.2 Scenario input parameters
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam eu mi placerat, ultricies urna id, pharetra dui. Mauris quis mi sit am

## 6. Disaggregation
Lorem ipsum dolor sit ametes 

### 6.1 Temporal disaggregation

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam eu mi placerat, ultricies urna id, pharetra dui. Mauris quis mi sit ame

### 6.2 Spatial disaggregation


Employment data are used to improve industry related dissagregation: 

    wood        
    textiles       
    chemicals       None
    printing        None
    electrical_equipment        None
    paper       None
    basic_metals        None
    beverages       None
    pharmaceuticals       None
    machinery       None
    water_collection_treatment        None
    food_production       None
    rubber_plastics       None
    wearing_appeal        None
    other_transport_equipment       None
    leather       None
    motor_vehicles        None
    waste_collection        None
    tobacco       None
    mining        None
    other_manufacturing       None
    furniture       None
    non_metallic_minearl_products       None
    computer        None
    fabricated_metal_products       None
  
Matching of ECUK and employment data
      
## 10. Reading the code

This section provides an overview of how to read the code.

### 10.1 Abbreviations

Within the code, different abbreviations are consistenly used
across all modules.

    rs:         Residential Submodel
    ss:         Service Submodel
    ts:         Transportation Submodel

    bd:         Base demand
    by:         Base year
    cy:         Current year
    lp:         Load profile
    dw:         Dwelling
    p:          Fraction, i.e. (100% = 1.0)
    pp:         Per person
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

Different endings are appended to variables, depending on the temporal
resolution of the data. The following abbreviations hold true:

> `y`:  Total demand in a year

> `yd`: 'Yearly load profile' - Profile for every day in a year of total yearly demand(365)

> `yh`: 'Daily load profile'  - Profile for every hour in a year of total yearly demand (365, 24)

> `dh`: Load profile of a single day

> `y_dh`: Daily load profile within each day (365, 25). Within each day, sums up to 1.0


## 11.Technologies

Based on ECUK() different technologies are assigned to enduses. Efficiencies are calculated
based on....

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
    <td>Boiler (different fueltypes), Condensing boiler, ASHP, GSHP, Micro-CHP, Fuel cell, Storage heating, Night storage heater, Heat network generation technologies (CHP,...)</td>
</table>

*Table 2: Technology assignement to enduses*

## 12 Used Data Sets

This section provides an overview of all used datasets in HIRE and necessary data preparation.

### 12.1 National Energy Data

The base year energy consumption of the UK (ECUK) in terms of fuels and technology shares for the residential, service and industry sectors is taken from the Department for Business, Energy and Industrial Strategy ([BEIS, 2016](https://www.gov.uk/government/collections/energy-consumption-in-the-uk)). National final energy data is provided for 6 fuel types (solid fuel, gas, electricity, oil, heat sold, bioenergy and waste) in the unit of ktoe (tonne of oil equivalents). All energy unit conversions are based on the unit converter by the International Energy Agency ([IEA, 2017](http://www.iea.org/statistics/resources/unitconverter)).


### 12.2 Household Electricity Servey

The [Household Electricity Survey (HES)](https://www.gov.uk/government/collections/household-electricity-survey)
is the most detailed monitoring of electricity use ever carried out in the UK.
Electricity consumption was monitored at an appliance level in 250
owner-occupied households across England from 2010 to 2011.
The load profiles for different residential enduses for
different daytypes (weekend, working day) are taken from a [24 hour spreadsheet tool](https://www.gov.uk/government/publications/spreadsheet-tools-for-users).

### 12.3 Carbon Trust advanced metering trial

The (Carbon Trust, 2007) advanced metering trial dataset contains hourly electricity and gas demand measurements for different service (business) sectors. The Carbon Trust data does not allow distinguishing between different end uses within each sector. According to the dominant fuel type of each end use, either aggregated gas or sector specific load profiles are therefore assigned. For ‘water heating’, ‘space heating’ and the ‘other_gas_enduse’, all gas measurements across all sectors are used, because the sample size was too little to distinguish between gas use for different sectors. For all other end uses, sector specific electricity load profiles are assigned. The provided sectors in the data trial do not fully correspond to the ECUK sectors (see Table 5) and where a sector is missing, the aggregated profiles across all sectors are used. No technology specific load profiles are used.

<table align="center">
  <tr>
    <th align="left">ECUK Data (Table 5.05)</th>
    <th align="left">Carbon Trust Dataset</th>
  </tr>
  <tr>
    <td>Community, arts and leisure</td>
    <td>Community</td>
  </tr>
  <tr>
    <td>Education</td>
    <td>Education</td>
  </tr>
  <tr>
    <td>Emergency Services</td>
    <td>Aggregated across all sectors</td>
  </tr>
    <tr>
    <td>Health</td>
    <td>Health</td>
  </tr>
    <tr>
    <td>Hospitality</td>
    <td>Aggregated across all sectors</td>
  </tr>
    <tr>
    <td>Military</td>
    <td>Aggregated across all sectors</td>
  </tr>
    <tr>
    <td>Offices</td>
    <td>Offices</td>
  </tr>
    <tr>
    <td>Retail</td>
    <td>Retail</td>
  </tr>
    <tr>
    <td>Storage</td>
    <td>Aggregated across all sectors</td>
  </tr>
</table>

*Table 3: Matching sectors from the ECUK dataset and sectors from the Carbon Trust dataset*

Yearly load profiles are generated based on averaging measurements for every month and day type (weekend, working day). In addition, average peak daily load profiles and the peak day factor is calculated. Only the yearly load profile for space heating is generated as explained in Section XY . The daily load profiles are derived from gas load profile from the Carbon Trust dataset. Data preparation and cleaning was necessary of the raw input files (see XY):

Data preparation of the raw input files was necessary:
•	Half-hourly data was converted into hourly data
•	Within each sector, only datasets containing at least one full year of monitoring data are used, from which only one full year is selected
•	Only datasets having not more than one missing measurement point per day are used
•	The data was cleaned from obviously wrong measurement points (containing very large minus values)
•	missing measurement points are interpolated 


**More information**
 - The data download link can be found [here](http://data.ukedc.rl.ac.uk/simplebrowse/edc/efficiency/residential/Buildings/AdvancedMeteringTrial_2006/)

### 12.4 Temperature data

To calculate regional daily hourly load heating profiles, hourly temperature data are used from the UK Met Office (2015) and loaded for weather stations across the UK.

### 12.5 Census data

https://www.nomisweb.co.uk/census/2011/qs605uk.pdf

**More information**
- The data download link can be found [here](http://catalogue.ceda.ac.uk/uuid/916ac4bbc46f7685ae9a5e10451bae7c)
- The station ID can be retreived [here](http://badc.nerc.ac.uk/cgi-bin/midas_stations/search_by_name.cgi.py?name=&minyear=&maxyear=)
- Metadatda of raw data can be found [here](http://artefacts.ceda.ac.uk/badc_datadocs/ukmo-midas/WH_Table.html)


### 12.5 Census Data


http://datashine.org.uk/#table=QS605EW&col=QS605EW0004&ramp=RdYlGn&layers=BTTT&zoom=8&lon=-0.8789&lat=51.2172

### 12.6 Technology specific load shapes

In order to generate load profiles for every hour in a year,
different typical load profils for weekdays, weekends and the peak day
are derived from measuremnt trials, i.e. load profiles are
modelled in a bottom-up way. In every case, only the profile (i.e.
the 'shape' of a profile) is read as an input into the model.

For different heating technologies, load shares are derived from the
following sources:


- **Boiler load profile**

   Load profiles for a typicaly working, weekend and peak day
   are derived from data provided by Sansom (2014).


- **Micro-CHP**

   Load profiles for a typicaly working, weekend and peak
   day are derived from data provided by Sansom (2014).


- **Heat pumps load profile**

   Based on nearly 700 domestic heat pump installations,
   Love et al. (2017) provides aggregated profiles for cold
   and medium witer weekdays and weekends. The shape of the
   load profiles is derived for a working, weekend and peak day.


- **Primary and secondary electirc heating**

  The load profiles are based on the Household Electricity
  Survey (HES) by the Department of Energy & 
  Climate Change (DECC, 2014).

Note: In case fuel is switched to another technology, it is assumed that
the load profile looks the same for the new fuel type. If e.g.
a gas boiler is replaced by a hydrogen boiler, the load profiles
are the same for the fueltype hydrogen or oil.

- COOLNIG?
    - **Residential**: Taken from *Denholm, P., Ong, S., & Booten, C. (2012).
        Using Utility Load Data to Estimate Demand for Space Cooling and
        Potential for Shiftable Loads, (May), 23.
        Retrieved from http://www.nrel.gov/docs/fy12osti/54509.pdf*

    - **Service**: *Knight, Dunn, Environments Carbon and Cooling in
        Uk Office Environments*

## Literature

BEIS (2016): Energy consumption in the UK (ECUK). London, UK. Retrieved from: [https://www.gov.uk/government/collections/energy-consumption-in-the-uk](https://www.gov.uk/government/collections/energy-consumption-in-the-uk)

Carbon Trust (2007). Advanced metering for SMEs Carbon and cost savings. Retrieved from
   [https://www.carbontrust.com/media/77244/ctc713_advanced_metering_for_smes.pdf](https://www.carbontrust.com/media/77244/ctc713_advanced_metering_for_smes.pdf)

DECC (2014) Household Electricity Survey. Retrieved from:[https://www.gov.uk/government/collections/household-electricity-survey](https://www.gov.uk/government/collections/household-electricity-survey)

Love, J., Smith, A. Z. P., Watson, S., Oikonomou, E., Summerfield, A., Gleeson, C., … Lowe, R. (2017). The addition of heat pump electricity load profiles to GB electricity demand: Evidence from a heat pump field trial. Applied Energy, 204, 332–342. [https://doi.org/10.1016/j.apenergy.2017.07.026](https://doi.org/10.1016/j.apenergy.2017.07.026)

Petchers, N. (2003) Combined heating, cooling & power handbook: technologies & applications. 2 edition. Lilburn: Fairmont Press.

Sansom, R. (2014). Decarbonising low grade heat for low carbon future. Imperial College London.

UK Met Office (2015): ‘MIDAS: UK hourly weather observation data’. Centre for Environmental Data Analysis. Retrieved from: [http://catalogue.ceda.ac.uk/uuid/916ac4bbc46f7685ae9a5e10451bae7c](http://catalogue.ceda.ac.uk/uuid/916ac4bbc46f7685ae9a5e10451bae7c).


###### Varia
- https://www.codecogs.com/latex/eqneditor.php used for this documentation


