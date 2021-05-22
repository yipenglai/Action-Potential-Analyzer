import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def single_sweep(
    analyzer,
    sweep: int = 1,
    trace: bool = True,
    current: bool = False,
    output_path: str = None
    ):
    # Create visualization
    param_sum = sum([trace, current])
    if param_sum == 0:
        raise ValueError("Please set at least one parameter as True: voltage, current")
    elif param_sum == 1:
        _, axs = plt.subplots()
        axs = [axs]
    else:
        _, axs = plt.subplots(param_sum)

    i = 0
    # Get current amplitude
    current_amplitude = analyzer.measure_current(sweep)
    # Plot trace (voltage)
    if trace:
        axs[i].plot(analyzer.get_trace(sweep))
        axs[i].set_xlabel("Time (s)")
        axs[i].set_ylabel("Voltage (mV)")
        axs[i].set_title("{} pA".format(current_amplitude))
        i += 1
    # Plot current
    if current:
        axs[i].plot(analyzer.get_current(sweep))
        axs[i].set_xlabel("Time (s)")
        axs[i].set_ylabel("Current (pA)")

    # Save plot
    if output_path:
        plt.savefig(output_path)


def multiple_sweeps(
    analyzer,
    sweep_list: list = None,
    offset: int = 0,
    output_path: str = None,
):
    # Check sweep list
    if not sweep_list:
        sweep_list = analyzer.sweep_list

    _, ax = plt.subplots()
    for i in range(len(sweep_list)):
        sweep = sweep_list[i]
        current_amplitude = analyzer.measure_current(sweep)
        if offset == 0:
            ax.plot(analyzer.get_trace(sweep), 
                    label="{} pA".format(current_amplitude))
            ax.set_xlabel("Time (s)")
            ax.set_ylabel("Voltage (mV)")
            plt.legend(loc="upper right")
        else:
            ax.plot(analyzer.get_trace(sweep)+offset*i, color="C0")
            ax.axes.get_xaxis().set_visible(False)

    # Save plot
    if output_path:
        plt.savefig(output_path)


def ap_count(
    analyzer,
    sweep_list: list = None,
    output_path: str = None
):
    # Check sweep list
    if not sweep_list:
        sweep_list = analyzer.sweep_list

    ap_count = []
    current_amplitudes = []
    for sweep in sweep_list:
        aps = analyzer.find_ap(sweep=sweep)
        ap_count.append(len(aps))
        current_amplitudes.append(analyzer.measure_current(sweep))

    plt.plot(current_amplitudes, ap_count, "-o")
    plt.grid(True, alpha=0.6)
    plt.xlabel("Voltage (pA)")
    plt.ylabel("Action Potential Count")

    # Save plot
    if output_path:
        plt.savefig(output_path)


def plot_ap(
    analyzer,
    sweep: int,
    ap_list: list = [0, -1],
    trace: bool = True,
    rate: bool = True,
    shape: bool = True,
    output_path: str = None
):
    # Create visualization
    param_sum = sum([trace, rate, shape])
    if param_sum == 0:
        raise ValueError("Please set at least one parameter as True: trace, rate, shape")
    elif param_sum == 1:
        _, axs = plt.subplots()
        axs = [axs]
    else:
        _, axs = plt.subplots(param_sum)
    
    
    # Get time indices
    time = analyzer.get_trace(sweep).index
    # Find action potentials
    aps = analyzer.find_ap(sweep)
    if len(aps) == 0:
        raise ValueError("No action potentials found in the current sweep.")
    else:
        i = 0
        for ap in ap_list:
            # Find action potential time
            ap_time = aps.index[ap]
            # Select time indices
            time_ = time[(time >= ap_time - 0.005) &
                        (time <= ap_time + 0.005)]
            ind = np.arange(len(time_))

            if trace:
                axs[i].plot(ind, analyzer.get_trace(sweep)[time_])
                axs[i].set_ylabel("Voltage (mV)")
                axs[i].axes.get_xaxis().set_visible(False)
                i += 1
            if rate:
                axs[i].plot(ind, analyzer.get_rate(sweep)[time_])
                axs[i].set_ylabel("dV/dt (mV/ms)")
                axs[i].axes.get_xaxis().set_visible(False)
                i += 1
            if shape:
                axs[i].plot(ind, analyzer.get_shape(sweep)[time_])
                axs[i].set_ylabel("$d^2V/dt^2$ (mV/$ms^2$)")
                axs[i].axes.get_xaxis().set_visible(False)
            i = 0
        
        # Save plot
        if output_path:
            plt.savefig(output_path)


def phase(
    analyzer,
    sweep: int,
    ap_list: list = [0, -1],
    output_path: str = None
):
    # Get trace and rate
    trace = analyzer.get_trace(sweep)
    rate = analyzer.get_rate(sweep)
    # Get time dices
    time = trace.index
    # Find action potentials
    aps = analyzer.find_ap(sweep)
    if len(aps) == 0:
        raise ValueError("No action potentials found in the current sweep.")
    else:
        for ap in ap_list:
            # Find action potential time
            ap_time = aps.index[ap]
            # Select time indices
            time_ = time[(time >= ap_time - 0.005) &
                        (time <= ap_time + 0.005)]
            plt.plot(trace[time_], rate[time_])
        plt.xlabel("Voltage (mV)")
        plt.ylabel("dv/dt (mV/ms)")

        # Save plot
        if output_path:
            plt.savefig(output_path)
