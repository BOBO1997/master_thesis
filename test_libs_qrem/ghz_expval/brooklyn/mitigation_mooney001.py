import numpy as np
import matplotlib.pyplot as plt
import pickle
import time
import importlib

import sys
sys.path.append("../../../libs_bell")
from lib_preprocessing import job_ids_to_result, flatten_results_jobs_list, arrange_results_list_tensored3, results_list_to_hist_list

with open("pkls/raw_hist_list.pkl", "rb") as f:
    raw_hist_list = pickle.load(f)
with open("pkls/results_meas_cal.pkl", "rb") as f:
    results_meas_cal = pickle.load(f)

from libs_qrem import MooneyEtalFilter
from qiskit.ignis.mitigation.measurement import TensoredMeasFitter

max_size = 65
max_length = 40
mooney001_mitigator_list = []
for n in range(2, max_size + 1):
    mit_pattern = [[i] for i in range(n)]
    meas_fitter = TensoredMeasFitter(results_meas_cal[n - 1], mit_pattern=mit_pattern)
    mooney001_mitigator_list.append(MooneyEtalFilter(n, meas_fitter.cal_matrices))
    if n % 10 == 0:
        print("size", n, "finished")
print("length of mooney001_mitigator_list: ", len(mooney001_mitigator_list))

for i in range(max_length):
    t1 = time.perf_counter()
    _ = mooney001_mitigator_list[i].apply(raw_hist_list[i + 1], threshold = 0.01)
    t2 = time.perf_counter()
    print(i + 1, "th finished (", i + 2, "qubits,", t2 - t1, "s )")
    

mooney001_mitigator_info = []
for i in range(max_length):
    t1 = time.perf_counter()
    mooney001_mitigator_info.append({# "exact_one_norm_of_reduced_inv_A": mooney001_mitigator_list[i].exact_one_norm_of_reduced_inv_A(),
                                 "mitigated_hist": mooney001_mitigator_list[i].mitigated_hist(),
                                 "x_s": mooney001_mitigator_list[i].x_s(),
                                 # "x_hat": mooney001_mitigator_list[i].x_hat(),
                                 "x_tilde": mooney001_mitigator_list[i].x_tilde(),
                                 "sum_of_x": mooney001_mitigator_list[i].sum_of_x(),
                                 # "sum_of_x_hat": mooney001_mitigator_list[i].sum_of_x_hat(),
                                 "sum_of_x_tilde": mooney001_mitigator_list[i].sum_of_x_tilde(),
                                 "indices_to_keys_vector": mooney001_mitigator_list[i].indices_to_keys_vector(),
                                 "times": mooney001_mitigator_list[i].times(),
                                 "expval": mooney001_mitigator_list[i].expval(),
                                 # "mitigation_stddev": mooney001_mitigator_list[i].mitigation_stddev(norm_type = "exact"),
                                 })
    t2 = time.perf_counter()
    print(i + 1, "th finished (", i + 2, "qubits,", t2 - t1, "s )")
    
with open("./pkls/mooney001_mitigator_info.pkl", "wb") as f:
    pickle.dump(mooney001_mitigator_info, f)