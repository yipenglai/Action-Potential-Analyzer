import pyabf
import pandas as pd
import numpy as np
import utils


class APAnalyzer:
    def __init__(
        self,
        file_path: str,
        sampling_rate: int = None,
        trace_threshold: float = 0,
        rate_threshold: float = 5
    ):
        self.file_path = file_path
        self.sampling_rate = sampling_rate
        self.trace_threshold = trace_threshold
        self.rate_threshold = rate_threshold

        # Read abf file
        self.abf = pyabf.ABF(file_path)
        self.sweep_list = self.abf.sweepList
        self.sweep_count = len(self.sweep_list)

    def get_trace(
        self,
        sweep: int
    ):
        # Read trace from abf
        trace = utils.read_sweep(
            abf=self.abf,
            sweep=sweep,
            channel=0
        )
        # Sample trace if required
        if self.sampling_rate:
            trace = utils.sample_series(trace, self.sampling_rate)
        return trace


    def get_current(
        self,
        sweep: int
    ):
        # Read current from abf
        current = utils.read_sweep(
            abf=self.abf,
            sweep=sweep,
            channel=1
        )
        # Sample trace if required
        if self.sampling_rate:
            current = utils.sample_series(current, self.sampling_rate)
        return current

    def get_rate(
        self,
        sweep
    ):
        trace = self.get_trace(sweep)
        # Compute time derivative in mV/ms
        rate = np.gradient(
            trace,
            1000*trace.index # Convert s to ms
        )
        return pd.Series(rate, trace.index)

    def get_shape(
        self,
        sweep
    ):
        rate = self.get_rate(sweep)
        # Compute time derivative in mV/ms^2
        shape = np.gradient(
            rate,
            1000*rate.index # Convert s to ms
        )
        return pd.Series(shape, rate.index)

    def find_ap(
        self,
        sweep: int
    ):
        # Get trace
        trace = self.get_trace(sweep)

        # Compute rate (i.e, first-order time derivative)
        rate = self.get_rate(sweep)

        # Find action potential segment
        # 1) rate higher than the rate threshold
        # 2) amplitude higher than the trace threshold
        segments = rate[(rate >= self.rate_threshold) & 
                        (trace >= self.trace_threshold)]

        # Find action potential spikes
        amplitude = []
        time = []
        if len(segments) == 1:
            # Find the time when rate first crosses zero
            # after the segment identified
            segment_end = segments.index[-1]
            ap_time = rate[(rate.index > segment_end) & 
                           (rate < 0)].index[0]
            time.append(ap_time)
            amplitude.append(trace[ap_time])

        if len(segments) > 1:
            all_ind = [np.where(trace.index == i)[0][0] for i in segments.index]
            for i in range(1, len(segments)):
                if all_ind[i] != all_ind[i-1]+1:
                    segment_end = trace.index[all_ind[i-1]]
                elif i == len(segments)-1:
                    segment_end = trace.index[all_ind[-1]]
                else:
                    continue
                ap_time = rate[(rate.index > segment_end) & 
                               (rate < 0)].index[0]
                time.append(ap_time)
                amplitude.append(trace[ap_time])
        return pd.Series(data=amplitude, index=time)

    def find_rheobase(self):
        for sweep in self.sweep_list:
            aps = self.find_ap(sweep)
            if len(aps) > 0:
                return sweep, self.measure_current(sweep)
            else:
                continue
                
    def find_ap_threshold(
        self,
        sweep
    ):
        trace = self.get_trace(sweep)
        rate = self.get_rate(sweep)
        trace_ = trace[rate >= self.rate_threshold]
        if len(trace_) == 0:
            raise ValueError("No action potential found. Please choose a different sweep.")
        else:
            ap_threshold = trace_.values[0]
            return ap_threshold
    
    def find_half_width(
        self,
        sweep
    ):
        trace = self.get_trace(sweep)
        rate = self.get_rate(sweep)
        ap_threshold = self.find_ap_threshold(sweep)
        aps = self.find_ap(sweep)
        # Difference between the first action potential
        # maplitude and threshold
        half_way = 0.5*(aps.iloc[0]+ap_threshold)
        # Find start and end of half-width duration
        start = trace[(rate >= self.rate_threshold) &
                      (trace >= half_way)].index[0]
        end = trace[(trace.index >= aps.index[0]) &
                    (trace < half_way)].index[0]
        half_width = end-start
        return half_width

    def find_current_step(
        self,
        sweep
    ):
        # Get current
        current = self.get_current(sweep)

        # Find current step defined as the period of time
        # when the current is higher than the average of max and min
        # current amplitude
        avg = (max(current)+min(current))*0.5
        current_step = current[current >= avg]
        return current_step

    def measure_current(
        self,
        sweep: int
    ):
        # Get current and current step
        current = self.get_current(sweep)
        current_step = self.find_current_step(sweep)

        if len(current_step) == 0:
            amplitude = 0
        else:
            start, end = current_step.index[0], current_step.index[-1]
            # Find baseline value
            baseline = np.median(
                current[(current.index >= start-0.04) & 
                        (current.index <= start-0.02)]
            )
            # Find stimulus value
            stimulus = np.median(
                current[(current.index >= start+0.05) &
                        (current.index <= end-0.05)]
            )
            # Compute amplitude
            amplitude = round((stimulus-baseline)/10)*10

        return amplitude
