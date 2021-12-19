import numpy as np
import time
import qiskit.ignis.mitigation as mit

def extract_two_qubit_counts(counts, pos1, pos2):
    ret_counts = {"00": 0, "01": 0, "10": 0, "11": 0}
    for k, v in counts.items():
        ret_counts[k[pos1] + k[pos2]] += v
    return ret_counts

def compute_stddev_of_grouping(stddevs):
    return np.sqrt(sum([stddev ** 2 for stddev in stddevs]))


def analyze_circuits_tensored(adj_lists, counts_dict_list, tensored_meas_mitigator_list=None, limit=100):
    """
    Input
        adj_lists         : list of adjacency list
        counts_dict_list  : list of int list (list of counts)
        tensored_meas_mitigator_list : measurement mitigator list
    Output
        expval_all_list : list of float (correlation of each graph)
        stddev_all_list : list of float (standard deviation of each graph)
        Es_all_list     : list of list (term-wise correlation of each graph)
        Ds_all_list     : list of list (term-wise stddev of each graph)
    """
    expval_all_list, stddev_all_list, Es_all_list, Ds_all_list = [], [], [], []
    for adj_list in adj_lists:
        t1 = time.time()
        n = len(adj_list)
        if n > limit:
            break
        print("graph size:", n)
        if n <= 1:
            print("skipped\n")
            expval_all_list.append(0)
            stddev_all_list.append(0)
            Es_all_list.append([])
            Ds_all_list.append([])
            continue

        # for the first term
        print("first term")
        tt1 = time.time()
        if tensored_meas_mitigator_list is not None:
            # n = 2 -> 0, n = 10 -> 16
            counts = tensored_meas_mitigator_list[n - 2].apply(counts_dict_list[2 * (n - 2)])
        else:
            counts = counts_dict_list[2 * (n - 2)]
        tt2 = time.time()
        print(tt2 - tt1, "s")
        expval1, stddev1 = mit.expectation_value(counts,
                                                 qubits=range(n),
                                                 clbits=range(n),
                                                 meas_mitigator=None)
        Es_1, Ds_1 = [expval1], [stddev1]

        # for the second term
        print("second term")
        Es_2, Ds_2 = [], []
        sum_expval2, sum_stddev2 = 0, 0
        tt1 = time.time()
        if tensored_meas_mitigator_list is not None:
            # n = 2 -> 1, n = 10 -> 17
            counts = tensored_meas_mitigator_list[n - 2].apply(counts_dict_list[2 * (n - 2) + 1])
        else:
            counts = counts_dict_list[2 * (n - 2) + 1]
        tt2 = time.time()
        print(tt2 - tt1, "s")
        for pos in range(1, n):  # recover the two qubit expectation values
            expval2, stddev2 = mit.expectation_value(extract_two_qubit_counts(counts, 0, pos),
                                                     qubits=[0, pos],
                                                     clbits=[0, pos],
                                                     meas_mitigator=None)
            Es_2.append(expval2)
            Ds_2.append(stddev2)
        sum_stddev2 = compute_stddev_of_grouping(Ds_2)

        sum_expval = np.sqrt(2) * ((n - 1) * sum(Es_1) + sum(Es_2))
        sum_stddev = np.sqrt(2 * ((stddev1 * (n - 1)) ** 2 + sum_stddev2 ** 2))
        Es = [Es_1, Es_2]
        Ds = [Ds_1, Ds_2]

        expval_all_list.append(sum_expval)
        stddev_all_list.append(sum_stddev)
        Es_all_list.append(Es)
        Ds_all_list.append(Ds)
        t2 = time.time()
        print("time:", t2 - t1)
        print("total correlation:", sum_expval, "\n\n\n")
    return expval_all_list, stddev_all_list, Es_all_list, Ds_all_list