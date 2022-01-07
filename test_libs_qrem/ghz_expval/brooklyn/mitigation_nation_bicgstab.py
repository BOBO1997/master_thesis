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
    
from libs_qrem import NationEtalFilter
from qiskit.ignis.mitigation.measurement import TensoredMeasFitter

"""
max_size = 65
max_length = 40
nation_bicgstab_mitigator_list = []
for n in range(2, max_size + 1):
    mit_pattern = [[i] for i in range(n)]
    meas_fitter = TensoredMeasFitter(results_meas_cal[n - 1], mit_pattern=mit_pattern)
    nation_bicgstab_mitigator_list.append(NationEtalFilter(n, meas_fitter.cal_matrices))
    if n % 10 == 0:
        print("size", n, "finished")
print("length of nation_bicgstab_mitigator_list: ", len(nation_bicgstab_mitigator_list))
"""

# print(raw_hist_list[50 - 2 + 1])
print(len(raw_hist_list[50 - 2 + 1]))

"""
for i in range(max_length):
    t1 = time.perf_counter()
    _ = nation_bicgstab_mitigator_list[i].apply(raw_hist_list[i + 1], method="bicgstab")
    t2 = time.perf_counter()
    print(i + 1, "th finished (", i + 2, "qubits,", t2 - t1, "s )")
"""
# print(raw_hist_list[50 + 1])
# print(nation_bicgstab_mitigator_list[50].num_clbits())
# nation_bicgstab_mitigator_list[50].apply(raw_hist_list[50 + 1], method="bicgstab")

with open("raw_hist_50qubit", "w") as f:
    for key, value in raw_hist_list[50 - 1].items():
        f.write(key)
        f.write(" ")
        f.write(str(value))
        f.write("\n")
f.close()

"""
nation_bicgstab_mitigator_info = []
for i in range(max_length):
    nation_bicgstab_mitigator_info.append({"exact_one_norm_of_inv_reduced_A": nation_bicgstab_mitigator_list[i].exact_one_norm_of_inv_reduced_A(),
                                           "iterative_one_norm_of_inv_reduced_A": nation_bicgstab_mitigator_list[i].iterative_one_norm_of_inv_reduced_A(method="iterative"),
                                           "mitigated_hist": nation_bicgstab_mitigator_list[i].mitigated_hist(),
                                           "x_s": nation_bicgstab_mitigator_list[i].x_s(),
                                           "x_hat": nation_bicgstab_mitigator_list[i].x_hat(),
                                           "x_tilde": nation_bicgstab_mitigator_list[i].x_tilde(),
                                           "sum_of_x": nation_bicgstab_mitigator_list[i].sum_of_x(),
                                           "sum_of_x_hat": nation_bicgstab_mitigator_list[i].sum_of_x_hat(),
                                           "sum_of_x_tilde": nation_bicgstab_mitigator_list[i].sum_of_x_tilde(),
                                           "indices_to_keys_vector": nation_bicgstab_mitigator_list[i].indices_to_keys_vector(),
                                           "times": nation_bicgstab_mitigator_list[i].times(),
                                           "expval": nation_bicgstab_mitigator_list[i].expval(),
                                           "mitigation_stddev": nation_bicgstab_mitigator_list[i].mitigation_stddev(norm_type = "exact"),
                                 })
    print(i + 1, "th finished (", i + 2, "qubits,", t2 - t1, "s )")

with open("./pkls/nation_bicgstab_mitigator_info.pkl", "wb") as f:
    pickle.dump(nation_bicgstab_mitigator_info, f)
"""