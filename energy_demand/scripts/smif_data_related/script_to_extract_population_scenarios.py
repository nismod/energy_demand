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


extrapolate_specific_scenario = True   # 2016-2050
base_year_data = True                  # 2015

if base_year_data:
    """Base year data (no variants, same for all variants)
    """
    npp = NPPData.NPPData()
    snpp = SNPPData.SNPPData()

    year = 2015

    # start with an empty data frame
    result_ppp = pd.DataFrame()

    # loop over all the UK LAD (or LAD-equivalents)
    for lad in snpp.data.GEOGRAPHY_CODE.unique():

        #region_ppp = snpp.create_variant('ppp', npp, lad, year)
        region_ppp = snpp.extrapolagg(["GENDER", "C_AGE"], npp, lad, year) #princiapl

        # aggregate the calculated variants by age and gender
        result_ppp = result_ppp.append(region_ppp, ignore_index=True)

    # write out results
    result_ppp.to_csv("C:/Users/cenv0553/mistral_population/__RESULTS/all_variants_2015.csv", index=False)
    print("Finished writting 2015 data")

if extrapolate_specific_scenario:
    '''
    Get extrapolated data for full time range for different ONS scenarios from 2016 - 2050
    # https://github.com/nismod/population/blob/master/doc/example_variant_ex.py
    '''

    # initialise the population modules
    npp = NPPData.NPPData()
    snpp = SNPPData.SNPPData()

    # 50 years, roughly half is extrapolated
    # Must start with 2015.
    years = range(2016, 2051)

    # start with an empty data frame
    result_ppp = pd.DataFrame()
    result_ppl = pd.DataFrame()
    result_pph = pd.DataFrame()

    # loop over all the UK LAD (or LAD-equivalents)
    for lad in snpp.data.GEOGRAPHY_CODE.unique():
        print("Collection population for region {}".format(lad))

        # Principle variant
        region_ppp = snpp.extrapolagg(["GENDER", "C_AGE"], npp, lad, years)
            
        # calculate the the variants
        #region_ppp = snpp.create_variant("ppp", npp, lad, years)
        region_ppl = snpp.create_variant("ppl", npp, lad, years)
        region_pph = snpp.create_variant("pph", npp, lad, years)

        # aggregate the calculated variants by age and gender
        region_ppl = utils.aggregate(region_ppl, ["GENDER", "C_AGE"])
        region_pph = utils.aggregate(region_pph, ["GENDER", "C_AGE"])

        result_ppp = result_ppp.append(region_ppp, ignore_index=True)
        result_ppl = result_ppl.append(region_ppl, ignore_index=True)
        result_pph = result_pph.append(region_pph, ignore_index=True)

    # write out results
    result_ppp.to_csv("C:/Users/cenv0553/mistral_population/__RESULTS/prinicpal_extrap_2016-2050.csv", index=False)
    result_ppl.to_csv("C:/Users/cenv0553/mistral_population/__RESULTS/lowmigration_extrap_2016-2050.csv", index=False)
    result_pph.to_csv("C:/Users/cenv0553/mistral_population/__RESULTS/highmigration_extrap_2016-2050.csv", index=False)
    print("Finished writting 2016 - 2050 data")
