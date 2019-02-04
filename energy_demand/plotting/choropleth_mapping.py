"""Plot map of shapefile
"""
# pylint: disable=C0103
import argparse
import os

import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import matplotlib.pyplot as plt

def plot_shapes(path):
    plt.figure(figsize=(6, 6), dpi=150)
    proj = ccrs.OSGB()
    ax = plt.axes(projection=proj)
    ax.outline_patch.set_visible(False)

    geoms = []
    for record in shpreader.Reader(path).records():
        geoms.append(record.geometry)

    ax.add_geometries(geoms, crs=proj, edgecolor='white', facecolor='#efefef')

    output_filename = os.path.join(
        os.getcwd(),
        'map.png'
    )
    plt.savefig(output_filename)


def add_geoms_by_attribute(path, ax):
    """Example adding geometries with categorical color
    """
    # set up a dict to hold geometries keyed by our key
    geoms_by_key = defaultdict(list)
    # here we hardcode colors by key - could use other methods (interpolation, lookup...)
    colors_by_key = {
        'a': '#ff0000',
        'b': '#00ff00',
        'c': '#0000ff'
    }

    # for each records, pick out our key's value from the record
    # and store the geometry in the relevant list under geoms_by_key
    for record in shpreader.Reader(path).records():
        key = record.attributes['key']
        geoms_by_key[key].append(record.geometry)

    # now we have all the geometries in lists for each value of our key
    # add them to the axis, using the relevant color as facecolor
    for key, geoms in geoms_by_key:
        color = colors_by_key[key]
        ax.add_geometries(geoms, crs=proj, edgecolor='white', facecolor=color)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plot a shapefile.')
    parser.add_argument('path', help='path to the shapefile to plot')
    args = parser.parse_args()

    plot_shapes(args.path)