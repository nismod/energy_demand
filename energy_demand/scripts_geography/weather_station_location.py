"""Weather data manipulation
"""
from haversine import haversine # Package to calculate distance between two long/lat points

def calc_distance_two_points(long_from, lat_from, long_to, lat_to):
    """Calculate distance between two points

    Parameters
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
    from_pnt = (long_from, lat_from)
    to_pnt = (long_to, lat_to)
    distance = haversine(from_pnt, to_pnt, miles=False)

    return distance

def get_closest_station(longitude_reg, latitue_reg, weather_stations):
    """Search ID of closest weater station

    Parameters
    ----------
    longitude_reg : float
        Longitute coordinate of Region Object
    latitue_reg : float
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
            latitue_reg,
            weather_stations[station_id]['station_latitude'],
            weather_stations[station_id]['station_longitude']
        )

        if dist_to_station < closest_dist:
            closest_dist = dist_to_station
            closest_id = station_id

    return closest_id
