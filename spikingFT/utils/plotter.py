#!/usr/bin/env python3
"""
Module with functions for generating different experiment plots
"""
# Standard libraries
from abc import ABC, abstractmethod
import matplotlib.pyplot as plt
import numpy as np

plt.style.use('ggplot')


class Plotter(ABC):
    """
    Abstract class for defining structure of plotters

    Any plot that has to be run in the library shall be created as
    an instance of this class
    """
    def __init__(self, style="classic", **kwargs):
        """
        Initialize plotter

        Paramters:
            plot_names: List with the names of all plots
            data: List with the data corresponding with the plot names
            show: Bool indicating whether to show the resulting plots
        """
        self.plot_names = kwargs.get("plot_names")
        self.data = kwargs.get("data")
        self.show = kwargs.get("show", True)
        self.figsize = kwargs.get("figsize")
        self.tight_layout = kwargs.get("tight_layout", True)
        self.style = style
        if len(self.plot_names) != len(self.data):
            raise ValueError("Sizes of names and data lists do not match")
        self.nplots = len(self.plot_names)
        self.fig = None
        self.axis = []

    def formatter(self):
        plt.rcParams['font.size'] = 18
        #    plt.rcParams['font.family'] = 'Times New Roman'
        plt.rcParams['axes.labelsize'] = plt.rcParams['font.size']
        plt.rcParams['axes.titlesize'] = 1.1*plt.rcParams['font.size']
        plt.rcParams['figure.titlesize'] = 1.3*plt.rcParams['font.size']
        plt.rcParams['legend.fontsize'] = plt.rcParams['font.size']
        plt.rcParams['xtick.labelsize'] = plt.rcParams['font.size']
        plt.rcParams['ytick.labelsize'] = plt.rcParams['font.size']
        plt.rcParams['xtick.major.size'] = 3
        plt.rcParams['xtick.minor.size'] = 3
        plt.rcParams['xtick.major.width'] = 1
        plt.rcParams['xtick.minor.width'] = 1
        plt.rcParams['ytick.major.size'] = 3
        plt.rcParams['ytick.minor.size'] = 3
        plt.rcParams['ytick.major.width'] = 1
        plt.rcParams['ytick.minor.width'] = 1
        plt.rcParams['legend.frameon'] = True
        plt.rcParams['legend.loc'] = 'upper right'
        plt.rcParams['axes.linewidth'] = 1
        plt.rcParams['lines.linewidth'] = 1
        plt.rcParams['lines.markersize'] = 3
        plt.rcParams['axes.grid'] = False
        plt.rcParams['grid.color'] = "lightgrey"
        if self.style=="classic":
            plt.rcParams['axes.facecolor'] = "white"
            plt.rcParams['axes.edgecolor'] = "black"
        elif self.style=="ggplot":
            plt.rcParams['axes.facecolor'] = "lightgrey"
            plt.rcParams['axes.edgecolor'] = "white"
        for ax in self.axis:
            ax.spines['right'].set_visible(False)
            ax.spines['top'].set_visible(False)
        return

    @abstractmethod
    def plot(self, plot_name, i):
        return

    def run(self):
        self.formatter()
        self.fig, self.axis = plt.subplots(self.nplots, figsize=self.figsize)
        if type(self.axis) is not np.ndarray:
            self.axis = np.array(self.axis).reshape((1,))
        for i, plot_name in enumerate(self.plot_names):
            self.plot(plot_name, i)
        if self.tight_layout:
            plt.tight_layout()
        if self.show:
            plt.show()
        return self.fig

    def __call__(self):
        return self.run()


class SNNSimulationPlotter(Plotter):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def plot_voltages(self, data, ax):
        nsamples = data.shape[1]
        for sample in range(1, nsamples):
            ax.plot(data[:, sample, 0], linewidth=.5)
            ax.plot(data[:, sample, 1], linewidth=.5)
        ax.set_xlabel("Time step")
        # ax.set_ylabel(r'$V_m$ (mV)')
        ax.spines['left'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.set_yticks([])
        ax.set_title("Membrane voltages")

    def plot_spikes(self, data, ax):
        nsamples = data[0].size
        for sample_n in range(nsamples):
            ax.scatter(data[0][sample_n], sample_n,  s=4, c="#1f77b4")
            ax.scatter(data[1][sample_n], sample_n+nsamples,  s=4, c="#1f77b4")
        ax.set_xlim(0, data[2])
        ax.set_xlabel("simulation time")
        # ax.set_ylabel("Neuron")
        ax.spines['left'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.set_yticks([])
        ax.set_title("Output scatter plot")
        return
    
    def plot_spectrum(self, data, ax):
        ax.plot(data[0], linewidth=.5)
        ax.plot(data[1], linewidth=.5)
        ax.set_xlabel("FT bin nº")
        # ax.set_ylabel(r'S-FT $t_s$')
        ax.spines['left'].set_visible(False)
        ax.set_yticks([])
        ax.set_title("FT modulus")

    def plot(self, plot_name, plot_n):
        ax = self.axis[plot_n]
        if plot_name == "voltages": 
            self.plot_voltages(self.data[plot_n], ax)
        elif plot_name == "spikes": 
            self.plot_spikes(self.data[plot_n], ax)
        elif plot_name == "FT": 
            self.plot_spectrum(self.data[plot_n], ax)
        else:
            raise ValueError("Invalid plot name: {}".format(plot_name))


class SNNLayersPlotter(Plotter):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sim_time = kwargs.get("sim_time")
        self.time_step = kwargs.get("time_step")
        self.nlayers = kwargs.get("nlayers", 1)

    def plot_voltages(self, data, ax, layern=1):
        nsamples = data.shape[1]
        for sample in range(1, nsamples):
            t = np.linspace(0, data.shape[0], data.shape[0])
            ax.plot(t, data[:, sample, 0], linewidth=.5)
            ax.plot(t, data[:, sample, 1], linewidth=.5)
        ax.set_yticks([])
        ax.set_xticks([])
        ax.set_xlim(0, data.shape[0])
        ax.set_ylabel(f'$V_{{{layern}}}$', rotation=0, labelpad=10)
        for n in range(self.nlayers+1):
            ax.axvline(
                x=self.sim_time*(n+1)/self.time_step,
                linestyle=":",
                linewidth=".7",
                color="grey"
            )
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_position('zero')
        ax.spines['left'].set_position('zero')
        if self.style == "classic":
            ax.plot((1), (0), ls="", marker=">", ms=2, color="k",
                transform=ax.get_yaxis_transform(), clip_on=False)
            ax.plot((0), (1), ls="", marker="^", ms=2, color="k",
                    transform=ax.get_xaxis_transform(), clip_on=False)

    def plot_spikes(self, data, ax, color="#1f77b4", layern=1):
        nsamples = data[0].size
        for sample_n in range(nsamples):
            ax.scatter(data[0][sample_n], sample_n,  s=4, c=color)
            ax.scatter(data[1][sample_n], sample_n+nsamples,  s=4, c=color)
        ax.set_xlim(0, data[-1])
        ax.set_yticks([])
        ax.set_xticks([])
        if layern:
            ylabel = f'$S_{{{layern}}}$'
        else:
            ylabel = "I"
        ax.set_ylabel(ylabel, rotation=0, labelpad=10)
        for n in range(self.nlayers+1):
            ax.axvline(
                x=self.sim_time*(n+1),
                linestyle=":",
                linewidth=".7",
                color="grey"
            )
        ax.spines['left'].set_position('zero')
        ax.spines['bottom'].set_position('zero')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        if self.style == "ggplot":
            ax.spines['bottom'].set_visible(False)
        elif self.style == "classic":
            ax.plot((1), (0), ls="", marker=">", ms=2, color="k",
                transform=ax.get_yaxis_transform(), clip_on=False)
            ax.plot((0), (1), ls="", marker="^", ms=2, color="k",
                    transform=ax.get_xaxis_transform(), clip_on=False)

    def plot(self, plot_name, plot_n):
        layer_n = (plot_n+1) // 2
        ax = self.axis[plot_n]
        if plot_name == "voltages":
            self.plot_voltages(self.data[plot_n], ax, layern=layer_n)
        elif plot_name == "spikes":
            if plot_n == 0:
                color = "#E24A33"
            else:
                color = "#1f77b4"
            self.plot_spikes(self.data[plot_n], ax, color, layern=layer_n)
        else:
            raise ValueError("Invalid plot name: {}".format(plot_name))
        self.fig.subplots_adjust(left=0.1,
                    bottom=0.1,
                    right=0.9,
                    top=0.9,
                    wspace=0.001,
                    hspace=0.1)


class RelErrorPlotter(Plotter):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.source = kwargs.get("source", "ref")
        self.chirp_n = 0

    def plot_component(self,
                       data,
                       ax_left,
                       component="",
                       legend=False,
                       xlabel=False,
                      ):
        ax_right = ax_left.twinx()
        l1 = ax_left.plot(data[0], label="S-FT", color='#348ABD',
                          linewidth=.1)
        l2 = ax_left.plot(data[1], label=self.source, color='#E24A33',
                          linewidth=.1)
        ax_right.set_ylim([0., 0.1])
        if component=="Magnitude":
            ax_left.set_ylim([0, 1])
        else:
            ax_left.set_ylim([-1., 1])
        ax_left.set_ylabel("y", rotation=0, labelpad=15)
        lines = l1 + l2
        labels = [l.get_label() for l in lines]
        if legend:
            ax_left.legend(lines, labels, bbox_to_anchor=(0.0, 0.9, 1., .102),
                           loc='upper right', ncol=3)
        if xlabel:
            ax_left.set_xlabel("Bin Nº")
        ax_left.set_title("{}".format(component))
        for ax in (ax_right, ax_left):
            ax.spines['top'].set_visible(False)
            ax.spines['left'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.tick_params(axis="y", which="both",length=0)
        # Align right and left ticks
        if component=="Magnitude":
            ax_left.set_yticks(np.arange(0, 1.1, 0.5))
        else:
            ax_left.set_yticks(np.arange(-1, 2, 1.0))
        ax_right.set_yticks([])
        ax.grid(axis='y')

    def plot(self, plot_name, plot_n):
        ax = self.axis[plot_n]
        if plot_name == "real_spectrum":
            self.plot_component(self.data[plot_n], ax, "Real", legend=True)
        elif plot_name == "imag_spectrum":
            self.plot_component(self.data[plot_n], ax, "Imaginary")
        elif plot_name == "modulus":
            self.plot_component(self.data[plot_n], ax, "Magnitude", xlabel=True)
        else:
            raise ValueError("Invalid plot name: {}".format(plot_name))
        self.fig.suptitle("Scenario {}".format(self.chirp_n+1))
        self.fig.set_size_inches(8, 12)


class RMSEPlotter(Plotter):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def plot_single_line(self, data, ax):
        """
        Plot RMSE evolution for a single nsamples batch
        """
        ax.plot(data[1], data[0], c="red")
        ax.set_title("RMSE over different sim times")
        ax.set_ylabel("RMSE")
        ax.set_xlabel("Nº simulation steps")
        ax.spines['left'].set_visible(False)
        ax.grid(axis='y')
        ax.tick_params(axis="y", which="both",length=0)
        ax.set_ylim(0, 0.25)
        ax.locator_params(axis='x', nbins=5)
        return

    def plot_multiple_lines(self, data, ax):
        """
        Plot RMSE evolution for a single nsamples batch
        """
        for i, data_stream in enumerate(data[0]):
            tsteps = data[1]
            nbins = data[2][i]
            ax.plot(tsteps, data_stream, label="{} bins".format(nbins))
        ax.set_title("RMSE over different sim times")
        ax.set_ylabel("RMSE")
        ax.set_xlabel("Nº simulation steps")
        ax.spines['left'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.grid(axis='y')
        ax.tick_params(axis="y", which="both",length=0)
        ax.set_ylim(0, 0.25)
        ax.locator_params(axis='x', nbins=5)
        ax.legend()
        return

    def plot(self, plot_name, plot_n):
        ax = self.axis[plot_n]
        if plot_name == "single_line":
            self.plot_single_line(self.data[plot_n], ax)
        elif plot_name == "multiple_lines":
            self.plot_multiple_lines(self.data[plot_n], ax)
        else:
            raise ValueError("Invalid plot name: {}".format(plot_name))


def plot_snn_diagram(recorded_z, ylim, vth, sim_time=1, show=False):
    """
    Plot the evolution of the membrane voltage of given neurons
    """
    plt.rcParams['axes.facecolor'] = "white"
    plt.rcParams['axes.edgecolor'] = "black"
    nplots = 1
    time_step = 2*sim_time/len(recorded_z)
    fig, ax = plt.subplots(nrows=nplots, ncols=1, figsize=(20, 5*nplots))
    tsi = sim_time - time_step
    ax.plot(np.arange(0, sim_time*2, time_step), recorded_z, color="lightsteelblue")
    ax.set_ylim(-0.15, ylim)
    # Plot lines marking different neuron parameters
    ax.axhline(y=0, xmax=0.05, color="grey", linestyle="--", linewidth=.5)
    ax.axhline(y=vth, color="grey", linestyle="--", linewidth=.5)
    ax.axvline(x=0, color="red", linestyle="--", linewidth=1)
    ax.axvline(x=tsi, color="red", linestyle="--", linewidth=1)
    ax.axvline(x=sim_time*2, color="red", linestyle="--", linewidth=1)
    # Keep only two labels on the yticks, indicating rest and threshold V
    ax.set_yticks([0, vth])
    y_labels = ["" for item in ax.get_yticklabels()]
    y_labels[0] = r"$u_{r}$"
    y_labels[1] = r"$u_{th}$"
    ax.set_yticklabels(y_labels, fontdict={"fontsize": 18})
    # Set x axis ticks and labels
    ax.set_xticks([0, tsi, sim_time*2])
    x_labels = [r"$t_0$", r"$t_{si}$", r"$t_T$"]
    ax.set_xticklabels(x_labels, fontdict={"fontsize": 18})

    plt.tight_layout()
    # Annotate the two different stages of the simulation
    ax.annotate("Silent stage", xy=(0, -0.1), xytext=(0.5, -0.1),
        size=18, va="center", ha="center",
        arrowprops=dict(arrowstyle="-|>", connectionstyle="arc3", color="k")
    )
    ax.annotate("Silent stage", xy=(tsi, -0.1), xytext=(0.5, -0.1),
        size=18, va="center", ha="center",
        arrowprops=dict(arrowstyle="-|>", connectionstyle="arc3", color="k")
    )
    ax.annotate("Spiking stage", xy=(tsi, -0.1), xytext=(1.5, -0.1),
        size=18, va="center", ha="center",
        arrowprops=dict(arrowstyle="-|>", connectionstyle="arc3", color="k")
    )
    ax.annotate("Spiking stage", xy=(2, -0.1), xytext=(1.5, -0.1),
        size=18, va="center", ha="center",
        arrowprops=dict(arrowstyle="-|>", connectionstyle="arc3", color="k")
    )
    # Annotate the spiking time of the neuron
    ax.annotate("", xy=(tsi, 0.005), xytext=(1.25, 0.005),
        size=15, va="center", ha="center",
        arrowprops=dict(arrowstyle="<|-", connectionstyle="arc3", color="k")
    )
    ax.annotate(r"$t_i$", xy=(1.144, 0.0062), xytext=(1.11, 0.02),
        size=15, va="center", ha="center",
    )
    # Add membrane update equations
    ax.annotate(r"$u_i(t) = \sum_j{w_{ij}(t-t_j)}$", xy=(0.24, 0.06),
        xytext=(0.25, 0.2), size=15, va="center", ha="center",
        bbox=dict(boxstyle="round", fc="w", color="tab:blue"),
        arrowprops=dict(arrowstyle="-|>", connectionstyle="arc3,rad=0.2", color="black"),
    )
    ax.annotate(r"$\dfrac{u_i(t) - u_i(t-1)}{\Delta t} = I_{ext}$", xy=(1.12, 0.3),
        xytext=(1.4, 0.2), size=15, va="center", ha="center",
        bbox=dict(boxstyle="round", fc="w", color="tab:blue"),
        arrowprops=dict(arrowstyle="-|>", connectionstyle="arc3,rad=-0.2", color="black"),
    )
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    if show:
        plt.show()

    return fig
