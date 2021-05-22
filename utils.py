import pyabf
import pandas as pd
import numpy as np


def read_sweep(
    abf,
    sweep: int,
    channel: int
):
    abf.setSweep(sweep, channel=channel)
    return pd.Series(abf.sweepY, index=abf.sweepX)

def sample_series(
    series: pd.Series,
    sampling_rate: int = 10
):
    ind = np.where(np.arange(len(series))%sampling_rate == 0)[0]
    return series.iloc[ind]
