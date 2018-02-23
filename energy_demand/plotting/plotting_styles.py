"""Plotting styles
"""
from collections import OrderedDict

def linestyles():
    """
    https://matplotlib.org/gallery/lines_bars_and_markers/linestyles.html

    """

    linestyles = OrderedDict(
        [
            ('solid',               (0, ())),
            ('loosely dotted',      (0, (1, 10))),
            ('dotted',              (0, (1, 5))),
            ('densely dotted',      (0, (1, 1))),

            ('loosely dashed',      (0, (5, 10))),
            ('dashed',              (0, (5, 5))),
            ('densely dashed',      (0, (5, 1))),

            ('loosely dashdotted',  (0, (3, 10, 1, 10))),
            ('dashdotted',          (0, (3, 5, 1, 5))),
            ('densely dashdotted',  (0, (3, 1, 1, 1))),

            ('loosely dashdotdotted', (0, (3, 10, 1, 10, 1, 10))),
            ('dashdotdotted',         (0, (3, 5, 1, 5, 1, 5))),
            ('densely dashdotdotted', (0, (3, 1, 1, 1, 1, 1)))])

    linestyles_out = {}
    for nr, (name, linestyle) in enumerate(linestyles.items()):
        linestyles_out[nr] = linestyle

    return linestyles_out

def color_list():
    """ List with colors
    """
    color_list = [
        'darkturquoise',
        'orange',
        'firebrick',
        'darkviolet',
        'khaki',
        'olive',
        'darkseagreen',
        'darkcyan',
        'indianred',
        'darkblue',
        'orchid',
        'gainsboro',
        'mediumseagreen',
        'lightgray',
        'mediumturquoise',
        'darksage',
        'lemonchiffon',
        'cadetblue',
        'lightyellow',
        'lavenderblush',
        'coral',
        'purple',
        'aqua',
        'mediumslateblue',
        'darkorange',
        'mediumaquamarine',
        'darksalmon',
        'beige']

    return color_list

def color_list_selection():
    """
    """

    color_list_selection = [
        'darkturquoise',
        'orange',
        'firebrick',
        'darkviolet',
        'khaki',
        'olive',
        'darkseagreen',
        'darkcyan',
        'indianred',
        'darkblue']

    return color_list_selection

def font_info():
    """
    """
    font_additional_info = {
        'family': 'arial',
        'color': 'black',
        'weight': 'normal',
        'size': 8}

    return font_additional_info


'''def linear_gradient(hexList, nColors):
    """
    Given a list of hexcode values, will return a list of length
    nColors where the colors are linearly interpolated between the
    (r, g, b) tuples that are given.

    Examples
    --------
    >>> linear_gradient([(0, 0, 0), (255, 0, 0), (255, 255, 0)], 100)

    Source
    -------
    https://github.com/python-visualization/folium/blob/v0.2.0/folium/utilities.py#L104
    """
    def _scale(start, finish, length, i):
        """
        Return the value correct value of a number that is in between start
        and finish, for use in a loop of length *length*.
        """
        base = 16

        fraction = float(i) / (length - 1)
        raynge = int(finish, base) - int(start, base)
        thex = hex(int(int(start, base) + fraction * raynge)).split('x')[-1]
        if len(thex) != 2:
            thex = '0' + thex

        return thex

    allColors = []
    # Separate (R, G, B) pairs.
    for start, end in zip(hexList[:-1], hexList[1:]):
        # Linearly intepolate between pair of hex ###### values and
        # add to list.
        nInterpolate = 765
        for index in range(nInterpolate):
            r = _scale(start[1:3], end[1:3], nInterpolate, index)
            g = _scale(start[3:5], end[3:5], nInterpolate, index)
            b = _scale(start[5:7], end[5:7], nInterpolate, index)
            allColors.append(''.join(['#', r, g, b]))

    # Pick only nColors colors from the total list.
    result = []
    for counter in range(nColors):
        fraction = float(counter) / (nColors - 1)
        index = int(fraction * (len(allColors) - 1))
        result.append(allColors[index])

    return result

def color_brewer(color_code, n=6):
    """
    Generate a colorbrewer color scheme of length 'len', type 'scheme.
    Live examples can be seen at http://colorbrewer2.org/

    Arguments
    ---------
    color_code : str
        Color Code Set Name
    n : int
        Number of classes

    Returns
    -------
    color_scheme : list
        Color schema

    Source
    ------
    https://github.com/python-visualization/folium/blob/v0.2.0/folium/utilities.py#L104
    """
    maximum_n = 253

    scheme_info = {'BuGn': 'Sequential',
                   'BuPu': 'Sequential',
                   'GnBu': 'Sequential',
                   'OrRd': 'Sequential',
                   'PuBu': 'Sequential',
                   'PuBuGn': 'Sequential',
                   'PuRd': 'Sequential',
                   'RdPu': 'Sequential',
                   'YlGn': 'Sequential',
                   'YlGnBu': 'Sequential',
                   'YlOrBr': 'Sequential',
                   'YlOrRd': 'Sequential',
                   'BrBg': 'Diverging',
                   'PiYG': 'Diverging',
                   'PRGn': 'Diverging',
                   'PuOr': 'Diverging',
                   'RdBu': 'Diverging',
                   'RdGy': 'Diverging',
                   'RdYlBu': 'Diverging',
                   'RdYlGn': 'Diverging',
                   'Spectral': 'Diverging',
                   'Accent': 'Qualitative',
                   'Dark2': 'Qualitative',
                   'Paired': 'Qualitative',
                   'Pastel1': 'Qualitative',
                   'Pastel2': 'Qualitative',
                   'Set1': 'Qualitative',
                   'Set2': 'Qualitative',
                   'Set3': 'Qualitative',
                   }

    schemes = {'BuGn': ['#EDF8FB', '#CCECE6', '#CCECE6',
                        '#66C2A4', '#41AE76', '#238B45', '#005824'],
               'BuPu': ['#EDF8FB', '#BFD3E6', '#9EBCDA',
                        '#8C96C6', '#8C6BB1', '#88419D', '#6E016B'],
               'GnBu': ['#F0F9E8', '#CCEBC5', '#A8DDB5',
                        '#7BCCC4', '#4EB3D3', '#2B8CBE', '#08589E'],
               'OrRd': ['#FEF0D9', '#FDD49E', '#FDBB84',
                        '#FC8D59', '#EF6548', '#D7301F', '#990000'],
               'PuBu': ['#F1EEF6', '#D0D1E6', '#A6BDDB',
                        '#74A9CF', '#3690C0', '#0570B0', '#034E7B'],
               'PuBuGn': ['#F6EFF7', '#D0D1E6', '#A6BDDB',
                          '#67A9CF', '#3690C0', '#02818A', '#016450'],
               'PuRd': ['#F1EEF6', '#D4B9DA', '#C994C7',
                        '#DF65B0', '#E7298A', '#CE1256', '#91003F'],
               'RdPu': ['#FEEBE2', '#FCC5C0', '#FA9FB5',
                        '#F768A1', '#DD3497', '#AE017E', '#7A0177'],
               'YlGn': ['#FFFFCC', '#D9F0A3', '#ADDD8E',
                        '#78C679', '#41AB5D', '#238443', '#005A32'],
               'YlGnBu': ['#FFFFCC', '#C7E9B4', '#7FCDBB',
                          '#41B6C4', '#1D91C0', '#225EA8', '#0C2C84'],
               'YlOrBr': ['#FFFFD4', '#FEE391', '#FEC44F',
                          '#FE9929', '#EC7014', '#CC4C02', '#8C2D04'],
               'YlOrRd': ['#FFFFB2', '#FED976', '#FEB24C',
                          '#FD8D3C', '#FC4E2A', '#E31A1C', '#B10026'],
               'BrBg': ['#8c510a', '#d8b365', '#f6e8c3',
                        '#c7eae5', '#5ab4ac', '#01665e'],
               'PiYG': ['#c51b7d', '#e9a3c9', '#fde0ef',
                        '#e6f5d0', '#a1d76a', '#4d9221'],
               'PRGn': ['#762a83', '#af8dc3', '#e7d4e8',
                        '#d9f0d3', '#7fbf7b', '#1b7837'],
               'PuOr': ['#b35806', '#f1a340', '#fee0b6',
                        '#d8daeb', '#998ec3', '#542788'],
               'RdBu': ['#b2182b', '#ef8a62', '#fddbc7',
                        '#d1e5f0', '#67a9cf', '#2166ac'],
               'RdGy': ['#b2182b', '#ef8a62', '#fddbc7',
                        '#e0e0e0', '#999999', '#4d4d4d'],
               'RdYlBu': ['#d73027', '#fc8d59', '#fee090',
                          '#e0f3f8', '#91bfdb', '#4575b4'],
               'RdYlGn': ['#d73027', '#fc8d59', '#fee08b',
                          '#d9ef8b', '#91cf60', '#1a9850'],
               'Spectral': ['#d53e4f', '#fc8d59', '#fee08b',
                            '#e6f598', '#99d594', '#3288bd'],
               'Accent': ['#7fc97f', '#beaed4', '#fdc086',
                          '#ffff99', '#386cb0', '#f0027f'],
               'Dark2': ['#1b9e77', '#d95f02', '#7570b3',
                         '#e7298a', '#66a61e', '#e6ab02'],
               'Paired': ['#a6cee3', '#1f78b4', '#b2df8a',
                          '#33a02c', '#fb9a99', '#e31a1c'],
               'Pastel1': ['#fbb4ae', '#b3cde3', '#ccebc5',
                           '#decbe4', '#fed9a6', '#ffffcc'],
               'Pastel2': ['#b3e2cd', '#fdcdac', '#cbd5e8',
                           '#f4cae4', '#e6f5c9', '#fff2ae'],
               'Set1': ['#e41a1c', '#377eb8', '#4daf4a',
                        '#984ea3', '#ff7f00', '#ffff33'],
               'Set2': ['#66c2a5', '#fc8d62', '#8da0cb',
                        '#e78ac3', '#a6d854', '#ffd92f'],
               'Set3': ['#8dd3c7', '#ffffb3', '#bebada',
                        '#fb8072', '#80b1d3', '#fdb462'],
               }

    # Raise an error if the n requested is greater than the maximum.
    if n > maximum_n:
        raise ValueError("The maximum number of colors in a"
                         " ColorBrewer sequential color series is 253")

    # Only if n is greater than six do we interpolate values.
    if n > 6:
        if color_code not in schemes:
            color_scheme = None
        else:
            # Check to make sure that it is not a qualitative scheme.
            if scheme_info[color_code] == 'Qualitative':
                raise ValueError("Expanded color support is not available"
                                 " for Qualitative schemes, restrict"
                                 " number of colors to 6")
            else:
                color_scheme = linear_gradient(schemes.get(color_code), n)
    else:
        color_scheme = schemes.get(color_code, None)

    return color_scheme
'''
