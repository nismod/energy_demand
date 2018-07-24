"""Plotting styles
"""
from collections import OrderedDict
import palettable

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

def marker_list():
    """markers
    """

    markers = [
        "o",	# circle
        "o",	# circle
        "o",	# circle
        "o",	# circle
        "*",	# star
        "+",	# plus
        ".",	# point
        "o",	# circle
        ",",	# pixel
        "P",	# plus (filled)
        
        "x",	# x
        "v",	# triangle_down
        "^",	# triangle_up
        "<",	# triangle_left
        ">",	# triangle_right
        "1",	# tri_down
        "2",	# tri_up
        "3",	# tri_left
        "4",	# tri_right
        "8",	# octagon
        "s",	# square
        "p",	# pentagon

        "h",	# hexagon1
        "H",	# hexagon2
       
       
        "X",	# x (filled)
        "D",	# diamond
        "d",	# thin_diamond
        "|",	# vline
    ]
    return markers

def color_list_resilience():
    """
    """
    color_list = [
        #'darkturquoise',
        #'orange',
        #'firebrick',
        #'darkviolet',
        #'khaki',
        #'olive',
        #'darkseagreen',
        #'darkcyan',
        #'indianred',
        #'darkblue',
        'tomato',
        #'gainsboro',
        #'mediumseagreen',
        #'lightgray',
        'forestgreen', #'purple',
        'sandybrown',
        #'lemonchiffon',
        #'cadetblue',
        #'lightyellow',
        #'lavenderblush',
        'coral',
        
        'aqua',
        'mediumslateblue',
        'darkorange',
        'mediumaquamarine',
        'darksalmon',
        'beige']

    return color_list

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

def get_colorbrewer_color(color_prop, color_palette, inverse=False):
    """
    Get hex color from colorbrewer

    Arguments
    ----------
    color_prop : str
        Sequential or qualitative color criteria
    color_palette : str
        Name of colorbrewer palette
    invers : default (False)
        Invert color criteria
    """
    if color_prop == 'sequential':
        color_list = getattr(palettable.colorbrewer.sequential, color_palette).hex_colors
    if color_prop == 'qualitative':
        color_list = getattr(palettable.colorbrewer.qualitative, color_palette).hex_colors

    if inverse:
        color_list = color_list[::-1]
    else:
        pass

    return color_list

def color_list_selection():
    """
    """
    color_list_selection = [
        'seagreen',
        'slateblue', #'silver',
        #'coral',

        'dimgray',
        'gray',
        'darkgray',
        'livghray',
        'silver',
        'gainsboro',
        'whitesmoke',

        'steelblue',
        'tomato',
        'slateblue',
        'moccasin', #darkturquoise',
        'khaki',
        'orange',
        'firebrick',
        'darkviolet',
        'olive',
        'darkseagreen',
        'darkcyan',
        'indianred',
        'darkblue'
        ]

    return color_list_selection

def rs_color_list_selection():
    """
    """
    color_list_selection = [
        'seagreen',
        'slateblue', #'silver',
        #'coral',

        'dimgray',
        'gray',
        'darkgray',
        'lightgray',
        'silver',
        'gainsboro',
        'whitesmoke',

        'steelblue',
        'tomato',
        #'slateblue',
        'moccasin', #darkturquoise',
        'khaki',
        'orange'
        ]

    return color_list_selection

def ss_color_list_selection():
    """
    """
    color_list_selection = [
        'seagreen',
        'slateblue', #'silver',
        #'coral',

        #'lightslategrey',
        'dimgray',
        'gray',
        #'azure',
        'darkgray',
        'lightgray',
        'silver',
        'gainsboro',
        'whitesmoke',
        'gainsboro',
        'lightgray',
        


        'firebrick',
        'darkviolet',
        'olive',
        'darkseagreen',
        'darkcyan',
        'indianred',
        'darkblue',
        'slategrey'
        ]

    return color_list_selection

def is_color_list_selection():
    """
    """
    color_list_selection = [
        'seagreen',
        'slateblue',

        'dimgray',
        'gray',
        'darkgray',
        'lightgray',
        'silver',
        'whitesmoke',
        'gainsboro',
        

        'saddlebrown',
        'indigo',
        'cadetblue',
        'yellowgreen',
        'peachpuff',
        'tan',
        'pink']

    return color_list_selection

def color_list_selection_dm():
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

def color_list_scenarios():
    """
    """
    color_list_selection = get_colorbrewer_color(
        color_prop='qualitative', #sequential
        color_palette='Accent_6', #'Set3_12',
        inverse=False) # #https://jiffyclub.github.io/palettable/colorbrewer/sequential/'''

    color_list_selection = [
        '#7FC97F', #green
        'darkolivegreen', #'#BEAED4', #violet
        '#386CB0', #blue
        '#FDC086', #orange
        '#F0027F', #pink
        '#FFFF99'  #yello
        ]

    '''# Set3_12
    color_list_selection = [
        'darkolivegreen',
        'blue',
        '#B3DE69', #'#FCCDE5',
        '#FB8072',  #'#FDB462',
        '#BEBADA', #blue #'#80B1D3',
        '#BC80BD', #pink
        '#8DD3C7',
        '#FFED6F', #yellow
        '#FFFFB3', #yellow
        '#D9D9D9', #grey
        '#BEBADA', #blue
        '#CCEBC5',
        'forestgreen',
        'rosybrown',
        'blue',
        'firebrick']
    '''
    return color_list_selection

def font_info(
        family='arial',
        color='black',
        weight='normal',
        size=8
    ):
    """
    """
    font_additional_info = {
        'family': 'arial',
        'color': 'black',
        'weight': 'normal',
        'size': size}

    return font_additional_info
