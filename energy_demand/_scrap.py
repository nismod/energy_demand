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
def fit_sigmoid_diffusion(L, x_data, y_data, start_parameters):
    """Fit sigmoid curve based on two points on the diffusion curve

    Parameters
    ----------
    L : float
        The sigmoids curve maximum value (max consumption)
    x_data : array
        X coordinate of two points
    y_data : array
        X coordinate of two points

    Returns
    -------
    popt : dict
        Fitting parameters

    Info
    ----
    The Sigmoid is substacted - 2000 to allow for better fit with low values

    """
    def sigmoid(x, x0, k):
        """Sigmoid function used for fitting
        """
        y = L / (1 + np.exp(-k * ((x - 2000) - x0)))
        return y

    popt, _ = curve_fit(sigmoid, x_data, y_data, p0=start_parameters)

    return popt

import numpy as np
import pylab
from scipy.optimize import curve_fit

def sigmoid(x, x0, k):
     y = 0.9 / (1 + np.exp(-k*((x-2000)-x0)))
     return y

xdata = np.array([2015, 2040])
ydata = np.array([0.5, 0.55])

# FIT
startparameter = [0.1, 1]

popt = fit_sigmoid_diffusion(0.9, xdata, ydata, startparameter)

#popt, pcov = curve_fit(sigmoid, xdata, ydata, startparameter)
print(popt)

x = np.linspace(2015, 2040, 50)


y = sigmoid(x, *popt)

# Plot points
pylab.plot(xdata, ydata, 'o', label='data')

pylab.plot(x, y, label='fit')
pylab.ylim(0, 1.05)
pylab.legend(loc='best')
pylab.show()