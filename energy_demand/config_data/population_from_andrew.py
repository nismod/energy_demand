"""Download population projections from https://github.com/nismod/population/blob/master/README.md


Info
-----

https://github.com/virgesmith/UKCensusAPI
https://www.nomisweb.co.uk/myaccount/webservice.asp
https://github.com/nismod/population
https://github.com/virgesmith/UKCensusAPI

Steps
------
1. optain nomis key
2. in cmd line: set NOMIS_API_KEY=XXX
3. ./setup.py install
4. run python script from command line

https://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/populationprojections/bulletins/nationalpopulationprojections/2015-10-29

Potential variants
-------------------
hhh: High population,
hpp: High fertility,
lll: Low population,
lpp: Low fertility,
php: High life expectancy,
pjp: Moderately high life expectancy,
pkp: Moderately low life expectancy,
plp: Low life expectancy,
pph: High migration,
ppl: Low migration,
ppp: Principal,
ppq: 0% future EU migration (non-ONS),
ppr: 50% future EU migration (non-ONS),
pps: 150% future EU migration (non-ONS),
ppz: Zero net migration

Select for paper I
-------------------
Prinicpal projection    ppp
Low mnigration          ppl
High migration          pph
"""
import pandas as pd
import population.nppdata as NPPData
import population.snppdata as SNPPData
import population.utils as utils

reg_pop = True
extrapolate_pop = False
extrapolate_specific_scenario = True

if extrapolate_specific_scenario:
    '''
    Get extrapolated data for full time range for different ONS scenarios from 2015 - 2050
    # https://github.com/nismod/population/blob/master/doc/example_variant_ex.py
    '''

    # initialise the population modules
    npp = NPPData.NPPData()
    snpp = SNPPData.SNPPData()

    # 50 years, roughly half is extrapolated
    years = range(2015, 2051)

    # start with an empty data frame
    result_ppp = pd.DataFrame()
    result_ppl = pd.DataFrame()
    result_pph = pd.DataFrame()

    # loop over all the UK LAD (or LAD-equivalents)
    for lad in snpp.data.GEOGRAPHY_CODE.unique():
        print("Collection population for region {}".format(lad))

        # calculate the the variants
        region_ppp = snpp.create_variant("ppp", npp, lad, years)
        region_ppl = snpp.create_variant("ppl", npp, lad, years)
        region_pph = snpp.create_variant("pph", npp, lad, years)

        # aggregate the calculated variants by age and gender
        region_ppp = utils.aggregate(region_ppp, ["GENDER", "C_AGE"])
        region_ppl = utils.aggregate(region_ppl, ["GENDER", "C_AGE"])
        region_pph = utils.aggregate(region_pph, ["GENDER", "C_AGE"])

        result_ppp.append(region_ppp, ignore_index=True)
        result_ppl.append(region_ppl, ignore_index=True)
        result_pph.append(region_pph, ignore_index=True)

        break
    print("tt")

    # write out results
    result_ppp.to_csv("C:/Users/cenv0553/mistral_population/__RESULTS/prinicpal_extrap_2050.csv", index=False)
    result_ppl.to_csv("C:/Users/cenv0553/mistral_population/__RESULTS/lowmigration_extrap_2050.csv", index=False)
    result_pph.to_csv("C:/Users/cenv0553/mistral_population/__RESULTS/highmigration_extrap_2050.csv", index=False)
    print("FINISHED")
'''
if extrapolate_pop:

    # ===================
    # Extrapolating SNPP for 2040 - 2050
    #https://github.com/nismod/population
    # ===================

    # initialise the population modules
    npp = NPPData.NPPData()
    snpp = SNPPData.SNPPData()

    # get the first year where extrapolation is necessary
    ex_start = snpp.max_year() + 1

    # we extrapolate to 2050
    ex_end = 2050

    # start with an empty data frame
    result = pd.DataFrame()

    # loop over all the UK LAD (or LAD-equivalents)
    for lad in snpp.data.GEOGRAPHY_CODE.unique():

        # extrapolate
        lad_ex = snpp.extrapolagg("GEOGRAPHY_CODE", npp, lad, range(ex_start, ex_end + 1))

        # append to data
        result = result.append(lad_ex, ignore_index=True)

    # write out results
    result.to_csv("C:/Users/cenv0553/mistral_population/population/__RESULTS/snpp_extrap_2050.csv")

if reg_pop:

    # initialise the population modules
    npp = NPPData.NPPData()
    snpp = SNPPData.SNPPData()

    # get the first year where extrapolation is necessary
    ex_start = snpp.max_year() + 1

    # we extrapolate to 2050
    ex_end = 2050 

    # start with an empty data frame
    result = pd.DataFrame()

    # loop over all the UK LAD (or LAD-equivalents)
    for lad in snpp.data.GEOGRAPHY_CODE.unique():

        # get the total projected population for newcastle up to the SNPP horizon (2039)
        lad_non_ex = snpp.aggregate("GEOGRAPHY_CODE", lad, range(2015, ex_start))

        # extrapolate for another 25 years
        lad_ex = snpp.extrapolagg("GEOGRAPHY_CODE", npp, lad, range(ex_end))

        # append to data
        result = result.append(lad_non_ex, ignore_index=True)
        result = result.append(lad_ex, ignore_index=True)

    # write out results
    result.to_csv("C:/Users/cenv0553/mistral_population/population/__RESULTS/snpp_extrap_2015_2050_ppp.csv")
'''