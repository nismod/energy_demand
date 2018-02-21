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

def font_info():
    """
    """
    font_additional_info = {
        'family': 'arial',
        'color': 'black',
        'weight': 'normal',
        'size': 8}

    return font_additional_info
