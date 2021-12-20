import numpy as np
import time
import qiskit.ignis.mitigation as mit

def remaining_vertices(adj_list, n, F):
    remaining = set(range(n)) - set(F)
    for m in F:
        for v in adj_list[m]:
            remaining.discard(v)
    return list(remaining)


def extract_two_qubit_counts(counts, pos1, pos2):
    ret_counts = {"00": 0, "01": 0, "10": 0, "11": 0}
    for k, v in counts.items():
        ret_counts[k[pos1] + k[pos2]] += v
    return ret_counts


def extract_three_qubit_counts(counts, pos1, pos2, pos3):
    ret_counts = {"000": 0, "001": 0, "010": 0, "011": 0,
                  "100": 0, "101": 0, "110": 0, "111": 0}
    for k, v in counts.items():
        ret_counts[k[pos1] + k[pos2] + k[pos3]] += v
    return ret_counts


def extract_sub_counts(counts_xz, counts_zx, center, n):
    if center & 1:
        if center == n - 1:
            return extract_two_qubit_counts(counts_zx, n - 2, n - 1), [n - 2, n - 1]
        else:
            return extract_three_qubit_counts(counts_zx, center - 1, center, center + 1), [center - 1, center, center + 1]
    else:
        if center == n - 1:
            return extract_two_qubit_counts(counts_xz, n - 2, n - 1), [n - 2, n - 1]
        elif center == 0:
            return extract_two_qubit_counts(counts_xz, 0, 1), [0, 1]
        else:
            return extract_three_qubit_counts(counts_xz, center - 1, center, center + 1), [center - 1, center, center + 1]


def compute_stddev_of_grouping(stddevs):
    return np.sqrt(sum([stddev ** 2 for stddev in stddevs]))

def mitigate_counts(counts_dict_list, meas_fitter_list, limit=100):
    times = []
    mitigated_counts_dict_list = []
    for counts_dict in counts_dict_list:
        n = len(list(counts_dict.keys())[0])
        if n <= 1:
            print("skipped\n")
        counts_xz = meas_fitter_list[n - 2].apply(counts_dict_list[2 * (n - 2)])
        counts_zx = meas_fitter_list[n - 2].apply(counts_dict_list[2 * (n - 2) + 1])
        mitigated_counts_dict_list += [counts_xz, counts_zx]
    return mitigated_counts_dict_list, times



def analyze_circuits_tensored(adj_lists, Fs, counts_dict_list, limit = 100):
    """
    Input
        adj_lists         : list of adjacency list
        Fs                : list of vertex subset
        counts_dict_list  : list of int list (list of counts)
        tensored_meas_mitigator_list : measurement mitigator list
    Output
        expval_all_list : list of float (correlation of each graph)
        stddev_all_list : list of float (standard deviation of each graph)
        Es_all_list     : list of list (term-wise correlation of each graph)
        Ds_all_list     : list of list (term-wise stddev of each graph)
    """
    assert len(adj_lists) == len(Fs)
    corr_all_list, stddev_all_list, Es_all_list, Ds_all_list = [], [], [], []

    for adj_list, F in zip(adj_lists, Fs):
        n = len(adj_list)
        if n > limit:
            break
        print("graph size:", len(adj_list))
        if n <= 1:
            print("skipped\n")
            corr_all_list.append(0)
            stddev_all_list.append(0)
            Es_all_list.append([])
            Ds_all_list.append([])
            continue

        # XZXZXZXZ
        counts_xz = counts_dict_list[2 * (n - 2)]
        # ZXZXZXZX
        counts_zx = counts_dict_list[2 * (n - 2) + 1]

        Es_F, Ds_F, corr_F = [], [], 0
        remaining = remaining_vertices(adj_list, n, F)

        for m in F:
            counts, poses = extract_sub_counts(counts_xz, counts_zx, m, n)
            corr_itself, stddev_itself = mit.expectation_value(
                counts, qubits=poses, clbits=poses, meas_mitigator=None)
            corr_deg = corr_itself * len(adj_list[m])
            Es_m, Ds_m = [corr_itself], [stddev_itself * len(adj_list[m])]
            for j, _ in enumerate(adj_list[m]):
                counts, poses = extract_sub_counts(counts_xz, counts_zx, j, n)
                expval, stddev = mit.expectation_value(counts, qubits=poses, clbits=poses, meas_mitigator=None)
                Es_m.append(expval)
                Ds_m.append(stddev)
            sum_corr = corr_deg + sum(Es_m[1:])
            print("correlation on n[", m, "]:", sum_corr)
            corr_F += sum_corr
            Es_F.append(Es_m)
            Ds_F.append(Ds_m)

        # remainig part
        Es_R, Ds_R = [], []
        for i, _ in enumerate(remaining):
            counts, poses = extract_sub_counts(counts_xz, counts_zx, i, n)
            expval, stddev = mit.expectation_value(counts, qubits=poses, clbits=poses, meas_mitigator=None)
            Es_R.append(expval)
            Ds_R.append(stddev)
        corr_R = sum(Es_R)
        print("correlation on remaining vertices:", corr_R)

        corr_F *= np.sqrt(2)
        corr_all = corr_F + corr_R
        corr_all_list.append(corr_all)
        stddev_all_list.append(np.sqrt(2 * sum([dev ** 2 for Ds_m in Ds_F for dev in Ds_m]) + sum([dev ** 2 for dev in Ds_R])))
        Es_all_list.append([Es_F, Es_R])
        Ds_all_list.append([Ds_F, Ds_R])
        print("total correlation:", corr_all, "\n")
    return corr_all_list, stddev_all_list, Es_all_list, Ds_all_list
