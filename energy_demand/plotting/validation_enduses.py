"""Validation plots
"""
# print dataframe
import matplotlib.pyplot as plt

def plot_dataframe_function(
        my_df,
        x_column_name,
        y_column_names,
        from_to_value_to_plot=[],
        plot_kind='line'):
    """
    """
    if from_to_value_to_plot == []:

        result_to_plot = my_df.plot(
            x=x_column_name,
            y=y_column_names,
            kind=plot_kind)
    else:
        from_value = from_to_value_to_plot[0]
        to_value = from_to_value_to_plot[1]

        result_to_plot = my_df[from_value:to_value].plot(
            x=x_column_name,
            y=y_column_names,
            kind=plot_kind)

    # ------------------------------------- 
    # Legend
    # -------------------------------------
    if type(y_column_names) is list:
        legend_entries = y_column_names
    else:
        legend_entries = [y_column_names]

    plt.legend(
        legend_entries,
        ncol=1,
        frameon=False,
        prop={
            'family': 'arial',
            'size': 15})
    
    plt.axis('tight')

    #plt.show()

    print("finished plotting")

    #plt.ylabel("GW")
    #plt.xlabel("day")
    #plt.title("tot annual ED, all enduses, fueltype {}".format(year_to_plot + 2050))
    #plt.savefig(fig_name)
    #plt.close()

'''
# Sum across all regions
    sum_across_regions = results_unconstrained.sum(axis=1)

    rows = []

    for hour in range(8760):

        # Get day and hour
        day_year, hour_day_year = date_prop.convert_h_to_day_year_and_h(hour)

        # Start row
        row = {'year': year, 'hour': hour}

        for submodel_nr, submodel in enumerate(submodels):

            # Total energy demand
            ed_submodel_h = sum_across_regions[submodel_nr][fuelype_nr][hour]

            # Space heating related demand for sector
            if submodel_nr == 0:
                space_heating_demand = enduse_specific_results['rs_space_heating'][fuelype_nr][day_year][hour_day_year]
            elif submodel_nr == 1:
                space_heating_demand = enduse_specific_results['ss_space_heating'][fuelype_nr][day_year][hour_day_year]
            else:
                space_heating_demand = enduse_specific_results['is_space_heating'][fuelype_nr][day_year][hour_day_year]

            ed_submodel_heating_h = space_heating_demand
            str_name_heat = "{}_heat".format(submodel)
            row[str_name_heat] = ed_submodel_heating_h

            # Non-heating related demand
            ed_submodel_non_heating_h = ed_submodel_h - space_heating_demand

            str_name_non_heat = "{}_non_heat".format(submodel)

            row[str_name_non_heat] = ed_submodel_non_heating_h

        rows.append(row)

    # Create dataframe
    col_names = [
        'year',
        'hour',
        'residential_non_heat',
        'residential_heat',
        'service_non_heat',
        'service_heat',
        'industry_non_heat',
        'industry_heat']

    my_df = pd.DataFrame(rows, columns=col_names)
    my_df.to_csv(path, index=False) #Index prevents writing index rows

'''