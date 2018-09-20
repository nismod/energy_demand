"""
"""
import os
import matplotlib.pyplot as plt

def plot_lp_dh(data_dh_modelled, path_plot_fig, fig_name):
    """plot daily profile
    """
    x_values = range(24)

    plt.plot(x_values, list(data_dh_modelled), color='red', label='modelled') #'ro', markersize=1,

    path_fig_name = os.path.join(
        path_plot_fig,
        fig_name)

    # -----------------
    # Axis
    # -----------------
    plt.ylim(0, 30)

    # ------------
    # Plot legend
    # ------------
    plt.legend(ncol=2, loc=2, frameon=False)

    # Tight layout
    plt.tight_layout()
    plt.margins(x=0)

    # Save fig
    plt.savefig(path_fig_name)
    plt.close()

'''def plot_lp_yh(data_dh_modelled, plotshow=False):
    """plot yearly profile
    """
    x_values = range(8760)

    yh_data_dh_modelled = np.reshape(data_dh_modelled, 8760)
    plt.plot(x_values, list(yh_data_dh_modelled), color='red', label='modelled') #'ro', markersize=1,

    # -----------------
    # Axis
    # -----------------
    #plt.ylim(0, 30)

    # ------------
    # Plot legend
    # ------------
    plt.legend(ncol=2, loc=2, frameon=False)

    # Tight layout
    plt.tight_layout()
    plt.margins(x=0)

    if plotshow:
        plt.show()
        plt.close()
    else:
        plt.close()'''

'''def plot_lp_yd(data_dh_modelled, plotshow=False):
    """plot yearly profile
    """
    def close_event():
        """Timer to close window automatically
        """
        plt.close()

    fig = plt.figure()
    x_values = range(365)

    plt.plot(x_values, data_dh_modelled, color='blue', label='modelled') #'ro', markersize=1,

    # -----------
    # Plot legend
    # ------------
    plt.legend(ncol=2, loc=2, frameon=False)

    # Tight layout
    plt.tight_layout()
    plt.margins(x=0)

    if plotshow:
        plt.show()
        plt.close()
    else:
        plt.close()

    #creating a timer object and setting an interval
    timer = fig.canvas.new_timer(interval = 1500)
    timer.add_callback(close_event)'''