import pickle
import time
import gc

max_size = 65

from libs_qrem import DeltaFilter
from qiskit.ignis.mitigation.measurement import TensoredMeasFitter

def get_info(mitigator):
    return {"exact_one_norm_of_reduced_inv_A": mitigator.exact_one_norm_of_reduced_inv_A(),
            "mitigated_hist": mitigator.mitigated_hist(),
            "times": mitigator.times(),
            "mitigation_stddev": mitigator.mitigation_stddev(norm_type = "exact"),
            }

def results_to_info(n):
    print("start", n, "qubits")
    delta_ghz_mqc_info = {}

    with open("pkls/raw_results/results_" + str(n) + "-qubit.pkl", "rb") as f:
        results = pickle.load(f)
        f.close()

    mitigator = DeltaFilter(n, TensoredMeasFitter(results["mit"], mit_pattern=[[j] for j in range(n)]).cal_matrices)
    delta_ghz_mqc_info["ghz"] = get_info(mitigator)
    print("mitigated ghz hist")

    delta_ghz_mqc_info["mqc"] = []
    for i, mqc_hist in enumerate( results["mqc"].get_counts() ):
        print(i + 1, "th mqc")
        delta_ghz_mqc_info["mqc"].append( get_info(mitigator) )
    print("mitigated mqc hists")

    with open("pkls/delta/info_" + str(n) + "-qubit.pkl", "wb") as f:
        pickle.dump(delta_ghz_mqc_info, f)
        f.close()

    print("finished", n, "qubits")
    print()
    del delta_ghz_mqc_info, results, mitigator
    gc.collect()
    
for n in range(1, max_size + 1):
    results_to_info(n)