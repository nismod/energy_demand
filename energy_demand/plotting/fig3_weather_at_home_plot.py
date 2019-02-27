import os
import numpy as np
import matplotlib.pyplot as plt

from energy_demand.read_write import read_data, write_data, data_loader
from energy_demand.plotting import basic_plot_functions

print("START")
def plotting_weather_data(path):
    """

    Things to plot

    - annual t_min of all realizations
    - annual t_max of all realizations

    - annual maximum t_max
    - annual minimum t_min
    """
    sim_yrs = range(2015, 2051, 5)
    weather_reationzations = ["NF{}".format(i) for i in range(1, 101,1)]

    container_weather_stations = {}
    container_temp_data = {}

    # All used weather stations from model run
    used_stations = ['station_id_253', 'station_id_252', 'station_id_253', 'station_id_252', 'station_id_252', 'station_id_328', 'station_id_329', 'station_id_305', 'station_id_282', 'station_id_335', 'station_id_335', 'station_id_359', 'station_id_358', 'station_id_309', 'station_id_388', 'station_id_418', 'station_id_420', 'station_id_389', 'station_id_433', 'station_id_385', 'station_id_374', 'station_id_481', 'station_id_481', 'station_id_480', 'station_id_466', 'station_id_531', 'station_id_532', 'station_id_535', 'station_id_535', 'station_id_484', 'station_id_421', 'station_id_472', 'station_id_526', 'station_id_525', 'station_id_526', 'station_id_504', 'station_id_503', 'station_id_504', 'station_id_505', 'station_id_504', 'station_id_504', 'station_id_455', 'station_id_548', 'station_id_546', 'station_id_537', 'station_id_545', 'station_id_236', 'station_id_353', 'station_id_352', 'station_id_384', 'station_id_510', 'station_id_527', 'station_id_550', 'station_id_501', 'station_id_456', 'station_id_472', 'station_id_201', 'station_id_470', 'station_id_487', 'station_id_505', 'station_id_486', 'station_id_457', 'station_id_533', 'station_id_458', 'station_id_441', 'station_id_440', 'station_id_473', 'station_id_217', 'station_id_247', 'station_id_199', 'station_id_232', 'station_id_234', 'station_id_478', 'station_id_248', 'station_id_388', 'station_id_377', 'station_id_376', 'station_id_376', 'station_id_388', 'station_id_354', 'station_id_376', 'station_id_388', 'station_id_515', 'station_id_514', 'station_id_514', 'station_id_531', 'station_id_532', 'station_id_494', 'station_id_512', 'station_id_535', 'station_id_535', 'station_id_517', 'station_id_534', 'station_id_533', 'station_id_549', 'station_id_549', 'station_id_550', 'station_id_549', 'station_id_508', 'station_id_490', 'station_id_507', 'station_id_526', 'station_id_508', 'station_id_491', 'station_id_507', 'station_id_489', 'station_id_509', 'station_id_526', 'station_id_545', 'station_id_492', 'station_id_490', 'station_id_451', 'station_id_467', 'station_id_450', 'station_id_451', 'station_id_466', 'station_id_451', 'station_id_521', 'station_id_538', 'station_id_537', 'station_id_537', 'station_id_522', 'station_id_546', 'station_id_536', 'station_id_522', 'station_id_520', 'station_id_537', 'station_id_488', 'station_id_487', 'station_id_488', 'station_id_472', 'station_id_487', 'station_id_487', 'station_id_551', 'station_id_544', 'station_id_419', 'station_id_525', 'station_id_552', 'station_id_525', 'station_id_543', 'station_id_542', 'station_id_552', 'station_id_543', 'station_id_544', 'station_id_542', 'station_id_542', 'station_id_306', 'station_id_305', 'station_id_282', 'station_id_306', 'station_id_406', 'station_id_264', 'station_id_306', 'station_id_283', 'station_id_284', 'station_id_306', 'station_id_305', 'station_id_304', 'station_id_283', 'station_id_418', 'station_id_403', 'station_id_419', 'station_id_418', 'station_id_403', 'station_id_402', 'station_id_392', 'station_id_379', 'station_id_391', 'station_id_422', 'station_id_404', 'station_id_379', 'station_id_443', 'station_id_444', 'station_id_445', 'station_id_423', 'station_id_469', 'station_id_425', 'station_id_444', 'station_id_461', 'station_id_438', 'station_id_437', 'station_id_439', 'station_id_438', 'station_id_455', 'station_id_454', 'station_id_438', 'station_id_284', 'station_id_268', 'station_id_286', 'station_id_266', 'station_id_288', 'station_id_270', 'station_id_333', 'station_id_389', 'station_id_378', 'station_id_389', 'station_id_389', 'station_id_377', 'station_id_390', 'station_id_403', 'station_id_469', 'station_id_485', 'station_id_484', 'station_id_469', 'station_id_499', 'station_id_498', 'station_id_516', 'station_id_497', 'station_id_479', 'station_id_400', 'station_id_387', 'station_id_401', 'station_id_374', 'station_id_400', 'station_id_386', 'station_id_375', 'station_id_401', 'station_id_491', 'station_id_459', 'station_id_492', 'station_id_476', 'station_id_475', 'station_id_477', 'station_id_462', 'station_id_523', 'station_id_523', 'station_id_522', 'station_id_523', 'station_id_523', 'station_id_523', 'station_id_505', 'station_id_522', 'station_id_541', 'station_id_539', 'station_id_523', 'station_id_417', 'station_id_417', 'station_id_437', 'station_id_436', 'station_id_436', 'station_id_548', 'station_id_547', 'station_id_488', 'station_id_539', 'station_id_540', 'station_id_540', 'station_id_540', 'station_id_547', 'station_id_416', 'station_id_434', 'station_id_435', 'station_id_434', 'station_id_434', 'station_id_415', 'station_id_488', 'station_id_488', 'station_id_489', 'station_id_329', 'station_id_330', 'station_id_330', 'station_id_330', 'station_id_330', 'station_id_329', 'station_id_354', 'station_id_330', 'station_id_329', 'station_id_329', 'station_id_328', 'station_id_328', 'station_id_328', 'station_id_304', 'station_id_327', 'station_id_331', 'station_id_357', 'station_id_356', 'station_id_355', 'station_id_221', 'station_id_221', 'station_id_221', 'station_id_237', 'station_id_416', 'station_id_417', 'station_id_416', 'station_id_416', 'station_id_417', 'station_id_400', 'station_id_400', 'station_id_307', 'station_id_307', 'station_id_331', 'station_id_308', 'station_id_332', 'station_id_221', 'station_id_506', 'station_id_507', 'station_id_506', 'station_id_525', 'station_id_506', 'station_id_524', 'station_id_506', 'station_id_524', 'station_id_505', 'station_id_506', 'station_id_524', 'station_id_506', 'station_id_506', 'station_id_506', 'station_id_505', 'station_id_507', 'station_id_505', 'station_id_505', 'station_id_506', 'station_id_506', 'station_id_523', 'station_id_524', 'station_id_524', 'station_id_524', 'station_id_506', 'station_id_507', 'station_id_505', 'station_id_524', 'station_id_524', 'station_id_506', 'station_id_506', 'station_id_524', 'station_id_506', 'station_id_172', 'station_id_193', 'station_id_173', 'station_id_133', 'station_id_130', 'station_id_168', 'station_id_194', 'station_id_152', 'station_id_170', 'station_id_214', 'station_id_195', 'station_id_103', 'station_id_124', 'station_id_110', 'station_id_176', 'station_id_136', 'station_id_125', 'station_id_121', 'station_id_9', 'station_id_111', 'station_id_105', 'station_id_36', 'station_id_108', 'station_id_52', 'station_id_119', 'station_id_4', 'station_id_94', 'station_id_159', 'station_id_137', 'station_id_102', 'station_id_77', 'station_id_303', 'station_id_2', 'station_id_154', 'station_id_64', 'station_id_89', 'station_id_124', 'station_id_109', 'station_id_109', 'station_id_123', 'station_id_86', 'station_id_105', 'station_id_110', 'station_id_110', 'station_id_448', 'station_id_348', 'station_id_349', 'station_id_350', 'station_id_351', 'station_id_372', 'station_id_394', 'station_id_449', 'station_id_464', 'station_id_407', 'station_id_428', 'station_id_446', 'station_id_446', 'station_id_463', 'station_id_463', 'station_id_464', 'station_id_447', 'station_id_448', 'station_id_448', 'station_id_396', 'station_id_447']

    # Load full data
    for weather_realisation in weather_reationzations:
        print("weather_realisation: " + str(weather_realisation))
        path_weather_data = path

        weather_stations, temp_data = data_loader.load_temp_data(
            {},
            sim_yrs=sim_yrs,
            weather_realisation=weather_realisation,
            path_weather_data=path_weather_data,
            same_base_year_weather=False,
            crit_temp_min_max=True,
            load_np=False,
            load_parquet=False,
            load_csv=True)

        # Load only data from selected weather stations
        temp_data_used = {}
        for year in sim_yrs:
            temp_data_used[year] = {}
            all_station_data = temp_data[year].keys()
            for station in all_station_data:
                if station in used_stations:
                    temp_data_used[year][station] = temp_data[year][station]

        container_weather_stations[weather_realisation] = weather_stations
        container_temp_data[weather_realisation] = temp_data_used

    # Create plot with daily min
    print("... creating min max plot")
    t_min_average_every_day = []
    t_max_average_every_day = []
    t_min_min_every_day = []
    t_max_max_every_day = []
    std_dev_t_min = []
    std_dev_t_max = []
    std_dev_t_min_min = []
    std_dev_t_max_max = []

    for year in sim_yrs:

        for realization in container_weather_stations.keys():
            t_min_average_stations = []
            t_max_average_stations = []
            t_min_min_average_stations = []
            t_max_max_average_stations = []
            stations_data = container_temp_data[realization][year]
            for station in stations_data.keys():
                t_min_annual_average = np.average(stations_data[station]['t_min'])
                t_max_annual_average = np.average(stations_data[station]['t_max'])
                t_min_min_stations = np.min(stations_data[station]['t_min'])
                t_max_max_stations = np.max(stations_data[station]['t_max'])

                t_min_average_stations.append(t_min_annual_average) #average cross all stations
                t_max_average_stations.append(t_max_annual_average) #average cross all stations
                t_min_min_average_stations.append(t_min_min_stations)
                t_max_max_average_stations.append(t_max_max_stations)

        av_t_min = np.average(t_min_average_stations) #average across all realizations
        av_t_max = np.average(t_max_average_stations) #average across all realizations
        av_min_t_min = np.average(t_min_min_average_stations) #average across all realizations
        av_max_t_max = np.average(t_max_max_average_stations) #average across all realizations

        std_t_min = np.std(t_min_average_stations)
        std_t_max = np.std(t_max_average_stations)
        std_t_min_min = np.std(t_min_min_average_stations)
        std_t_max_max = np.std(t_max_max_average_stations)

        t_min_average_every_day.append(av_t_min)
        t_max_average_every_day.append(av_t_max)
        t_min_min_every_day.append(av_min_t_min)
        t_max_max_every_day.append(av_max_t_max)
        
        std_dev_t_min.append(std_t_min)
        std_dev_t_max.append(std_t_max)
        std_dev_t_min_min.append(std_t_min_min)
        std_dev_t_max_max.append(std_t_max_max)

    # Plot variability
    fig = plt.figure(figsize=basic_plot_functions.cm2inch(9, 6)) #width, height

    colors = {
        't_min': 'steelblue',
        't_max': 'tomato',
        't_min_min': 'peru',
        't_max_max': 'r'}

    # plot
    plt.plot(sim_yrs, t_min_average_every_day, color=colors['t_min'], label="t_min")
    plt.plot(sim_yrs, t_max_average_every_day, color=colors['t_max'], label="t_max")
    plt.plot(sim_yrs, t_min_min_every_day, color=colors['t_min_min'], label="t_min_min")
    plt.plot(sim_yrs, t_max_max_every_day, color=colors['t_max_max'], label="t_max_max")

    # Variations
    plt.fill_between(
        sim_yrs,
        list(np.array(t_min_average_every_day) - (2 * np.array(std_dev_t_min))),
        list(np.array(t_min_average_every_day) + (2 * np.array(std_dev_t_min))),
        color=colors['t_min'],
        alpha=0.25)

    plt.fill_between(
        sim_yrs,
        list(np.array(t_max_average_every_day) - (2 * np.array(std_dev_t_max))),
        list(np.array(t_max_average_every_day) + (2 * np.array(std_dev_t_max))),
        color=colors['t_max'],
        alpha=0.25)

    plt.fill_between(
        sim_yrs,
        list(np.array(t_min_min_every_day) - (2 * np.array(std_dev_t_min_min))),
        list(np.array(t_min_min_every_day) + (2 * np.array(std_dev_t_min_min))),
        color=colors['t_min_min'],
        alpha=0.25)

    plt.fill_between(
        sim_yrs,
        list(np.array(t_max_max_every_day) - (2 * np.array(std_dev_t_max_max))),
        list(np.array(t_max_max_every_day) + (2 * np.array(std_dev_t_max_max))),
        color=colors['t_max_max'],
        alpha=0.25)
    
    # Legend
    legend = plt.legend(
        ncol=2,
        prop={'size': 10},
        loc='upper center',
        bbox_to_anchor=(0.5, -0.1),
        frameon=False)
    legend.get_title().set_fontsize(8)

    result_path = "C:/_scrap/"
    seperate_legend = True
    if seperate_legend:
        basic_plot_functions.export_legend(
            legend,
            os.path.join(result_path, "{}__legend.pdf".format(result_path)))
        legend.remove()

    plt.legend(ncol=2)
    plt.xlabel("Year")
    plt.ylabel("Temperature (°C)")
    
    plt.tight_layout()
    plt.margins(x=0)

    fig.savefig(os.path.join(result_path, "test.pdf"))


if __name__ == "__main__":
    """
    """
    plotting_weather_data("//linux-filestore.ouce.ox.ac.uk/mistral/nismod/data/energy_demand/J-MARIUS_data/_weather_realisation")