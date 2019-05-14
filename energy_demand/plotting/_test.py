
from smif.data_layer import Results
import matplotlib.pyplot as plt
import os
import seaborn as sbn
import geopandas as gpd
import pandas as pd

'''path = "C:/Users/cenv0553/nismod2/results/electricworld/energy_demand_constrained/decision_0"
a = os.listdir(path)
for i in a:
    print(i)'''

path = 'C:/Users/cenv0553/nismod2'
'''
results = Results({'interface': 'local_csv', 'dir': path})
df = results.read(['energy_sd_optimised'], ['energy_demand_constrained'], ['service_gas']).drop(columns='decision')
agg = df.groupby(by=['model_run', 'timestep', 'lad_uk_2016'], squeeze=True, sort=False).sum().drop(columns='hourly')
agg = agg.reset_index()
plot_lads(agg, 'service_gas')'''

results = Results({'interface': 'local_csv','dir': path})

print("--------")
model_runs = results.list_model_runs()

for i in model_runs:
    print(i)

filenames = [
    'industry_biomass_boiler_biomass',
    'industry_biomass_district_heating_biomass',
    'industry_biomass_non_heating',
    'industry_electricity_boiler_electricity',
    'industry_electricity_district_heating_electricity',
    'industry_electricity_heat_pumps_electricity',
    'industry_electricity_non_heating',
    'industry_gas_boiler_gas',
    'industry_gas_district_heating_CHP_gas',
    'industry_gas_non_heating',
    'industry_hydrogen_boiler_hydrogen',
    'industry_hydrogen_district_heating_fuel_cell',
    'industry_hydrogen_fuel_cell_hydrogen',
    'industry_hydrogen_heat_pumps_hydrogen',
    'industry_hydrogen_non_heating',
    'industry_oil_boiler_oil',
    'industry_oil_non_heating',
    'industry_solid_fuel_boiler_solid_fuel',
    'industry_solid_fuel_non_heating',
    'residential_biomass_boiler_biomass',
    'residential_biomass_district_heating_biomass',
    'residential_biomass_non_heating',
    'residential_electricity_boiler_electricity',
    'residential_electricity_district_heating_electricity',
    'residential_electricity_heat_pumps_electricity',
    'residential_electricity_non_heating',
    'residential_gas_boiler_gas',
    'residential_gas_district_heating_CHP_gas',
    'residential_gas_non_heating',
    'residential_hydrogen_boiler_hydrogen',
    'residential_hydrogen_district_heating_fuel_cell',
    'residential_hydrogen_fuel_cell_hydrogen',
    'residential_hydrogen_heat_pumps_hydrogen',
    'residential_hydrogen_non_heating',
    'residential_oil_boiler_oil',
    'residential_oil_non_heating',
    'residential_solid_fuel_boiler_solid_fuel',
    'residential_solid_fuel_non_heating',
    'service_biomass_boiler_biomass',
    'service_biomass_district_heating_biomass',
    'service_biomass_non_heating',
    'service_electricity_boiler_electricity',
    'service_electricity_district_heating_electricity',
    'service_electricity_heat_pumps_electricity',
    'service_electricity_non_heating',
    'service_gas_boiler_gas',
    'service_gas_district_heating_CHP_gas',
    'service_gas_non_heating',
    'service_hydrogen_boiler_hydrogen',
    'service_hydrogen_district_heating_fuel_cell',
    'service_hydrogen_fuel_cell_hydrogen',
    'service_hydrogen_heat_pumps_hydrogen',
    'service_hydrogen_non_heating',
    'service_oil_boiler_oil',
    'service_oil_non_heating',
    'service_solid_fuel_boiler_solid_fuel',
    'service_solid_fuel_non_heating',
    'service_solid_fuel_non_heating'
]

filenames = [
    'industry_electricity_boiler_electricity',
    'industry_electricity_district_heating_electricity',
    'industry_electricity_heat_pumps_electricity',
    'industry_electricity_non_heating',
    'residential_electricity_boiler_electricity',
    'residential_electricity_district_heating_electricity',
    'residential_electricity_heat_pumps_electricity',
    'residential_electricity_non_heating',
    'service_electricity_boiler_electricity',
    'service_electricity_district_heating_electricity',
    'service_electricity_heat_pumps_electricity',
    'service_electricity_non_heating',
]

filenames = [
    'industry_electricity_boiler_electricity',
    'industry_electricity_district_heating_electricity']
# ['model_run', 'timestep', 'decision', 'lad_uk_2016', 'hourly', filenames...]

model_runs = ['electricworld', 'multivector']
timesteps = [2015, 2020, 2030, 2050]
select_arc_regions = True

df = results.read(
    model_run_names=model_runs,
    model_names=['energy_demand_constrained'],
    output_names=filenames,
    timesteps=timesteps)


print(df.columns.tolist())

# Selet model run
#df.loc[df['model_run'] == model_runs[0]]

# Select regions
if select_arc_regions:
    arc_regions = [
        "E07000008", "E07000012", "E07000009", "E07000011", "E07000099", "E07000242", "E07000243",
        "E07000178", "E07000180", "E07000179", "E07000181", "E07000177", "E06000030", "E06000042",
        "E06000055", "E07000004", "E06000032", "E06000056", "E07000154", "E07000151", "E07000156",
        "E07000155"]

    df = df.loc[df['lad_uk_2016'].isin(arc_regions)]

# Drop columns
print(" ")
print("-----------ungrouped-------------")
print(df.sample(n=3))
df = df.drop(columns=['decision'])

df_grouped = df.groupby(
    by=['model_run', 'lad_uk_2016', 'timestep', 'hourly'],
    as_index=False).sum()

print("-----------grouped-------------")
print(type(df_grouped))
print(df.columns.tolist())
print(df.sample(n=3).values)

df_empty = pd.DataFrame(columns=model_runs, index=timesteps)

for model_run in model_runs:
    for timestep in timesteps:
        print("aaaaaa")
        print(df_grouped.columns.tolist())
        annual_all_reg_all_hourly = df_grouped[(
            df_grouped['model_run'] == model_run) & (
                df_grouped['timestep'] == timestep)]

        print("ddd " + str(annual_all_reg_all_hourly.shape))
        annual_all_reg_all_hourly = annual_all_reg_all_hourly.drop(columns=['model_run', 'timestep', 'lad_uk_2016', 'hourly'])
        annual_all_reg_all_hourly = annual_all_reg_all_hourly.sum().sum()
        print("annual_all_reg_all_hourly")
        print(annual_all_reg_all_hourly)
        df_empty[model_run][timestep] = annual_all_reg_all_hourly

print("===========")
print(df_empty)
df_empty.plot()
plt.show()
raise Exception("tt")

for model_run in model_runs:
    df_modelrun = df[df['model_run'] == model_run]
    df_modelrun = df_modelrun.drop(columns='model_run')

    for timestep in timesteps:
        df_modelrun_year = df_modelrun[df_modelrun['timestep'] == timestep]
        df_modelrun = df_modelrun.drop(columns='timestep')

        df_modelrun_year = df_modelrun_year.groupby(by=['lad_uk_2016', 'hourly'], as_index=False).sum()
        df_modelrun_year = df_modelrun_year.drop(columns=['lad_uk_2016', 'hourly'])

        # Sum demand across timesteps and regions
        df_modelrun_year = df_modelrun_year.sum()
        print("...")
        print(df_modelrun_year)
        df_empty[model_run][timestep] = df_modelrun_year



#'model_run', 'timestep', 'seasonal_week
df = df.groupby(by=['model_run', 'lad_uk_2016', 'timestep', 'hourly']).sum()
print(" ")
print("A ==================")
print(df.columns.tolist())
print(df.shape)
print(df.sample(n=3))

print("Sum annual across all filenames")
df = df.sum(axis=1).to_frame()
print(" ")
print("B ==================")
print(df.shape)
print(df.sample(n=3))

# Sum across all regions
df = df.sum().to_frame()
print("___3_______")
print(df.shape)
print(df)
# Sum all filenames
#df = df.sum(axis=1)
df.plot()
#print(df.columns.tolist())
#print(df['residential_electricity_non_heating'].shape)
#df = df.reset_index()
#df['residential_electricity_non_heating'].plot()
#df.plot_lads('residential_electricity_non_heating')
plt.show()