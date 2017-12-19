"""Weather Station location
"""
from haversine import haversine # Package to calculate distance between two long/lat points

def calc_distance_two_points(long_from, lat_from, long_to, lat_to):
    """Calculate distance between two points

    Arguments
    ----------
    long_from : float
        Longitute coordinate from point
    lat_from : float
        Latitute coordinate from point
    long_to : float
        Longitute coordinate to point
    lat_to : float
        Latitue coordinate to point

    Return
    ------
    distance : float
        Distance
    """
    distance_in_km = haversine(
        (long_from, lat_from),
        (long_to, lat_to),
        miles=False)

    return distance_in_km

def get_closest_station(longitude_reg, latitude_reg, weather_stations):
    """Search ID of closest weater station

    Arguments
    ----------
    longitude_reg : float
        Longitute coordinate of Region Object
    latitude_reg : float
        Latitute coordinate of Region Object
    weather_stations : dict
        Weater station data

    Return
    ------
    closest_id : int
        ID of closest weather station
    """
    closest_dist = 99999999999

    for station_id in weather_stations:
        dist_to_station = calc_distance_two_points(
            longitude_reg,
            latitude_reg,
            weather_stations[station_id]['station_longitude'],
            weather_stations[station_id]['station_latitude'])

        if dist_to_station < closest_dist:
            closest_dist = dist_to_station
            closest_id = station_id

    return closest_id
