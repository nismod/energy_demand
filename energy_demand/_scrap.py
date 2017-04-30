





'''


def sigmoid_diffusion(base_yr, curr_yr, year_end, sig_midpoint, sig_steeppness, saturation_yr, invention_yr):
    """ Saturation level needs to be defined
    Always return 1 if saturated --> but satured may be any share of the technology or fuel enduse"""
    # Year invention can't be before base year --> if technology existist, put invention year as model base year

    if curr_yr < invention_yr or curr_yr == base_yr:
        return 0 #Technology has not been invented, 0 penetration

    if curr_yr >= saturation_yr: #Technology is saturated
        return 1
    else:
        
        
        if curr_yr >= saturation_yr: # After saturation
            #years_availalbe = saturation_yr - base_yr # Number of years --> saturation point - base year --> Saturation == 100*
            return 1
        else:
            years_availalbe = curr_yr - invention_yr
            
            y_trans = -6.0 + (12.0 / (saturation_yr - invention_yr)) * years_availalbe

            # Get a value between 0 and 1 (sigmoid curve ranging vrom 0 to 1)
            cy_p = 1 / (1 + m.exp(-1 * sig_steeppness * (y_trans - sig_midpoint)))

            return cy_p




    # CONSUMPTION REPLACED
    switch_list = []
    switch_list.append(
        {
            'enduse': 'space_heating',
            'fueltype': 1,
            'tech_remove': 'gas_tech',  # 'average_mode', 'lowest_mode', 'average_all_except_to_be_replaced?
            'tech_install': 'heat_pump',
            'fuel_share': 0.5
            }
        )

    switch_list.append( # Replacing 60% of electricity with fluorescent_strip_lightinging
        {
            'enduse': 'lighting',
            'fueltype': 2,
            'tech_remove': 'lowest_mode', # 'average_mode', 'lowest_mode',
            switches: [
                {
                    'tech_install': 'fluorescent_strip_lightinging',
                    'fuel_share': 0.6
                },
                {
                    'tech_install': 'othertech',
                    'fuel_share': 0.4
                },

                ]
            
            'fuel_share': 0.6
            }
        )

'''




# -----------------
def sigmoid_diffusion(base_yr, curr_yr, year_end, sig_midpoint, sig_steeppness, saturation_yr, invention_yr):
    """ Saturation level needs to be defined
    Always return 1 if saturated --> but satured may be any share of the technology or fuel enduse"""
    # Year invention can't be before base year --> if technology existist, put invention year as model base year

    if curr_yr < invention_yr or curr_yr == base_yr:
        return 0 #Technology has not been invented, 0 penetration

    if curr_yr >= saturation_yr: #Technology is saturated
        return 1
    else:
        
        
        if curr_yr >= saturation_yr: # After saturation
            #years_availalbe = saturation_yr - base_yr # Number of years --> saturation point - base year --> Saturation == 100*
            return 1
        else:
            years_availalbe = curr_yr - invention_yr
            
            y_trans = -6.0 + (12.0 / (saturation_yr - invention_yr)) * years_availalbe

            # Get a value between 0 and 1 (sigmoid curve ranging vrom 0 to 1)
            cy_p = 1 / (1 + m.exp(-1 * sig_steeppness * (y_trans - sig_midpoint)))

            return cy_p


def sigmoidfuel_enduse_switchdiffusion(base_yr, curr_yr, saturate_year, year_invention):
    # Check how many years fuel_enduse_switch in the market
    if curr_yr < year_invention:
        val_yr = 0
        return val_yr
    else:
        if curr_yr >= saturate_year:
            years_availalbe = saturate_year - base_yr
        else:
            years_availalbe = curr_yr - year_invention

    # Translates simulation year on the sigmoid graph reaching from -6 to +6 (x-value)
    year_translated = -6 + ((12 / (saturate_year - year_invention)) * years_availalbe)

    # Convert x-value into y value on sigmoid curve reaching from -6 to 6
    sig_midpoint = 0  # Can be used to shift curve to the left or right (standard value: 0)
    sig_steeppness = 1 # The steepness of the sigmoid curve (standard value: 1)

    # Get a value between 0 and 1 (sigmoid curve ranging vrom 0 to 1)
    val_yr = 1 / (1 + m.exp(-1 * sig_steeppness * (year_translated - sig_midpoint)))

    return val_yr

















def frac_sy_sigm_new_fuel_enduse_switch(base_yr, curr_yr, year_end, assumptions, fuel_enduse_switch):
    """ Calculate share of a fuel_enduse_switch in a year based on assumptions

    """
    fract_by = assumptions['p_tech_by'][fuel_enduse_switch]
    fract_ey = assumptions['p_tech_ey'][fuel_enduse_switch]
    market_year = assumptions['tech_market_year'][fuel_enduse_switch]
    saturation_year = assumptions['tech_saturation_year'][fuel_enduse_switch]
    # EV: MAX_SHARE POSSIBLE
    #max_possible
    # How far the fuel_enduse_switch has diffused
    p_of_diffusion = round(sigmoidfuel_enduse_switchdiffusion(base_yr, curr_yr, saturation_year, market_year), 2)
    print("p_of_diffusion: " + str(p_of_diffusion))
    #fract_cy = p_of_diffusion * max_possible
    return p_of_diffusion




'''
1. Calculate fraction without fuel switch (assumption about internal shift between technologies)
2. Caclulate fuel switches: I. Amount of new fuel sigmoid
                            II. Update shares of technologies witihn fuel shares of existing technology (save fuels of internal fuel switches)
                            III. Calc Fuel of each technology: Share & eff 

                            Total fuel = (shareA* effA) + (shareB * effB) + fuelswtichesFuelTechA + fuelsWitch TechB

                            IV. Update cy technology shares including switch

          '''

import numpy as np
import matplotlib.pyplot as plt



a = [1,1,1,1,1]
b = [2,2,2,2,2]

y = np.row_stack((a,b))
x = [1,2,3,4,5]

#bin = np.arange(5) 
#plt.xlim([0,bin.size])

fig, ax = plt.subplots()
ax.stackplot(x, y)
plt.show()

"""A one-line summary that does not use variable names or the
    function name.
    Several sentences providing an extended description. Refer to
    variables using back-ticks, e.g. `var`.

    Parameters
    ----------
    var1 : array_like
        Array_like means all those objects -- lists, nested lists, etc. --
        that can be converted to an array.  We can also refer to
        variables like `var1`.
    var2 : int
        The type above can either refer to an actual Python type
        (e.g. ``int``), or describe the type of the variable in more
        detail, e.g. ``(N,) ndarray`` or ``array_like``.
    long_var_name : {'hi', 'ho'}, optional
        Choices in brackets, default first when optional.

    Returns
    -------
    type
        Explanation of anonymous return value of type ``type``.
    describe : type
        Explanation of return value named `describe`.
    out : type
        Explanation of `out`.

    Other Parameters
    ----------------
    only_seldom_used_keywords : type
        Explanation
    common_parameters_listed_above : type
        Explanation

    Raises
    ------
    BadException
        Because you shouldn't have done that.

    See Also
    --------
    otherfunc : relationship (optional)
    newfunc : Relationship (optional), which could be fairly long, in which
              case the line wraps here.
    thirdfunc, fourthfunc, fifthfunc

    Notes
    -----
    Notes about the implementation algorithm (if needed).
    This can have multiple paragraphs.
    You may include some math:

"""