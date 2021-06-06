import pandas as pd
import numpy as np
from apanalyzer import APAnalyzer


def ap_count(
    file_names: list = None,
    sampling_rate: int = None,
    trace_threshold: float = 0,
    rate_threshold: float = 5
):  
    ap_count = []
    valid_files = []
    for file in file_names:
        try:
            analyzer = APAnalyzer(
                file_path=file,
                sampling_rate=sampling_rate,
                trace_threshold=trace_threshold,
                rate_threshold=rate_threshold
            )
            valid_files.append(file)
            ap_count.append([len(analyzer.find_ap(sweep)) for sweep in analyzer.sweep_list])
            print(f"Finished processing {file}.")
        except ValueError:
            print(f"{file} not found!")
            continue 
    return pd.DataFrame(ap_count, index=valid_files)


def rheobase_stat(
    file_names: list = None,
    sampling_rate: int = None,
    trace_threshold: float = 0,
    rate_threshold: float = 5
):
    rheobase_current = []
    rheobase_threshold = []
    valid_files = []
    for file in file_names:
        try:
            analyzer = APAnalyzer(
                file_path=file,
                sampling_rate=sampling_rate,
                trace_threshold=trace_threshold,
                rate_threshold=rate_threshold
            )
            valid_files.append(file)
            rheobase = analyzer.find_rheobase()
            rheobase_current.append(rheobase[1])
            rheobase_threshold.append(analyzer.find_ap_threshold(rheobase[0]))
            print(f"Finished processing {file}.")
        except ValueError:
            print(f"{file} not found!")
            continue
    return pd.DataFrame({
        "rheobase_current":rheobase_current,
        "rheobase_threshold": rheobase_threshold
    }, index=valid_files)
