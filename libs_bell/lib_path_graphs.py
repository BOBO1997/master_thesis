import numpy as np

from qiskit import QuantumCircuit, QuantumRegister
from qiskit import execute
from qiskit.compiler import transpile
import qiskit.ignis.mitigation as mit
from qiskit.providers import backend


############# job casting ############


def prepare_path_graph_qcs(qc,
                           backend,
                           optimization_level=0,
                           initial_layout=None):
    """
    Return
        qcs: quantum circuits to be implemented
        nums_divide: numbers of how many the quantum circuits are prepared for one graph
        nums_meas_cal: numbers of measurement calibration circuits
        initial_layouts_: 
    """
    n = qc.num_qubits
    qcs, nums_meas_cal, initial_layouts_ = [], [], []

    if n <= 1:
        return [], [], [], []

    # first term: XZXZ...ZXZXZ <- measurement grouping
    new_qc1 = qc.copy("XZ pattern")
    new_qc1 += QuantumCircuit(n, n)
    new_qc1.h(range(n)[::2])
    new_qc1.barrier()
    new_qc1.measure(range(n), range(n)[::-1])  # measure all
    new_qc1 = transpile(new_qc1, backend=backend, basis_gates=['sx', 'rz', 'cx'],
                        optimization_level=optimization_level,
                        initial_layout=initial_layout, seed_transpiler=42)

    # second term: ZXZX...XZXZX <- measurement grouping
    new_qc2 = qc.copy("ZX pattern")
    new_qc2 += QuantumCircuit(n, n)
    new_qc2.h(range(n)[1::2])
    new_qc2.barrier()
    new_qc2.measure(range(n), range(n)[::-1])  # measure all
    new_qc2 = transpile(new_qc2, backend=backend, basis_gates=['sx', 'rz', 'cx'],
                        optimization_level=optimization_level,
                        initial_layout=initial_layout, seed_transpiler=42)

    # for mitigation circuits
    qr = QuantumRegister(n)
    meas_cal_circuits, _ = mit.tensored_meas_cal(
        mit_pattern=[[i] for i in range(n)], qr=qr, circlabel='mcal')
    for i, meas_cal_circuit in enumerate(meas_cal_circuits):
        meas_cal_circuits[i] = transpile(meas_cal_circuit, backend=backend, basis_gates=['sx', 'rz', 'cx'],
                                         optimization_level=optimization_level,
                                         initial_layout=initial_layout, seed_transpiler=42)
    nums_meas_cal.append(len(meas_cal_circuits))

    qcs += ([new_qc1, new_qc2] + meas_cal_circuits)
    initial_layouts_ += ([initial_layout, initial_layout] +
                         [initial_layout] * len(meas_cal_circuits))

    return qcs, [1, 1], nums_meas_cal, initial_layouts_


def prepare_path_graph_qcs_list(qc_graphs,  # list of qiskit.QuantumCircuit
                                adj_lists,             # list of adjacency list
                                backend,
                                optimization_level=0,  # int
                                initial_layouts=None):
    """
    qcs_list :                   circuits to be executed on the real device
    nums_divide_list :      the information of how I divided a large shots to several circuits
    nums_meas_cal_list : the information of how I prepared the measurement_circuits for CTMP calibration
    initial_layouts_list :     used in execute_circuits function
    """
    qcs_list, nums_divide_list, nums_meas_cal_list, initial_layouts_list = [], [], [], []
    if initial_layouts == None:
        initial_layouts = [list(range(len(adj_list))) for adj_list in adj_lists]
    for qc, initial_layout in zip(qc_graphs, initial_layouts):
        qcs, nums_divide, nums_meas_cal, initial_layouts_ = \
            prepare_path_graph_qcs(qc,
                                   backend=backend,
                                   optimization_level=optimization_level,
                                   initial_layout=initial_layout)
        nums_meas_cal_list.append(nums_meas_cal)
        initial_layouts_list += initial_layouts_
        qcs_list += qcs
        nums_divide_list.append(nums_divide)
    return qcs_list, nums_divide_list, nums_meas_cal_list, initial_layouts_list


def execute_circuits(qcs,
                     backend,
                     shots=8192,
                     max_experiments=900,
                     optimization_level=0):
    print("running on", backend)
    jobs, i = [], 0
    while i < len(qcs):
        jobs.append(execute(qcs[i:i + max_experiments], backend=backend,
                    shots=shots, optimization_level=optimization_level))
        print("circuits from", i, "to", min(i + max_experiments -
              1, len(qcs)), "are put on the real device.")
        i += max_experiments
    return jobs

############# analysis ############

def remaining_vertices(adj_list, n, F):
    remaining = set(range(n)) - set(F)
    for m in F:
        for v in adj_list[m]:
            remaining.discard(v)
    return list(remaining)


def extract_two_qubit_hist(hist, pos1, pos2):
    ret_hist = {"00": 0, "01": 0, "10": 0, "11": 0}
    for k, v in hist.items():
        ret_hist[k[pos1] + k[pos2]] += v
    return ret_hist


def extract_three_qubit_hist(hist, pos1, pos2, pos3):
    ret_hist = {"000": 0, "001": 0, "010": 0, "011": 0,
                  "100": 0, "101": 0, "110": 0, "111": 0}
    for k, v in hist.items():
        ret_hist[k[pos1] + k[pos2] + k[pos3]] += v
    return ret_hist


def extract_sub_hist(hist_xz, hist_zx, center, n):
    if center & 1:
        if center == n - 1:
            return extract_two_qubit_hist(hist_zx, n - 2, n - 1), [n - 2, n - 1]
        else:
            return extract_three_qubit_hist(hist_zx, center - 1, center, center + 1), [center - 1, center, center + 1]
    else:
        if center == n - 1:
            return extract_two_qubit_hist(hist_xz, n - 2, n - 1), [n - 2, n - 1]
        elif center == 0:
            return extract_two_qubit_hist(hist_xz, 0, 1), [0, 1]
        else:
            return extract_three_qubit_hist(hist_xz, center - 1, center, center + 1), [center - 1, center, center + 1]


def compute_stddev_of_grouping(stddevs):
    return np.sqrt(sum([stddev ** 2 for stddev in stddevs]))

def mitigate_hist(hist_list, meas_fitter_list, limit=100):
    times = []
    mitigated_hist_list = []
    for hist in hist_list:
        n = len(list(hist.keys())[0])
        if n <= 1:
            print("skipped\n")
        hist_xz = meas_fitter_list[n - 2].apply(hist_list[2 * (n - 2)])
        hist_zx = meas_fitter_list[n - 2].apply(hist_list[2 * (n - 2) + 1])
        mitigated_hist_list += [hist_xz, hist_zx]
    return mitigated_hist_list, times



def correlations_of_path_graphs(adj_lists, Fs, hist_list, silent = True):
    """
    Input
        adj_lists         : list of adjacency list
        Fs                : list of vertex subset
        hist_list  : list of int list (list of hist)
    Output
        expval_all_list : list of float (correlation of each graph)
        stddev_all_list : list of float (standard deviation of each graph)
        Es_all_list     : list of list (term-wise correlation of each graph)
        Ds_all_list     : list of list (term-wise stddev of each graph)
    """
    corr_all_list, stddev_all_list, Es_all_list, Ds_all_list = [], [], [], []

    assert len(hist_list) % 2 == 0

    for i in range(len(hist_list) // 2):
        adj_list = adj_lists[i]
        F = Fs[i]
        n = len(adj_list)
        print("graph size:", n)
        if n <= 1:
            print("skipped\n")
            corr_all_list.append(0)
            stddev_all_list.append(0)
            Es_all_list.append([])
            Ds_all_list.append([])
            continue

        # XZXZXZXZ
        hist_xz = hist_list[2 * (n - 2)]
        # ZXZXZXZX
        hist_zx = hist_list[2 * (n - 2) + 1]

        Es_F, Ds_F, corr_F = [], [], 0
        remaining = remaining_vertices(adj_list, n, F)

        for m in F:
            hist, poses = extract_sub_hist(hist_xz, hist_zx, m, n)
            corr_itself, stddev_itself = mit.expectation_value(
                hist, qubits=poses, clbits=poses, meas_mitigator=None)
            corr_deg = corr_itself * len(adj_list[m])
            Es_m, Ds_m = [corr_itself], [stddev_itself * len(adj_list[m])]
            for j, _ in enumerate(adj_list[m]):
                hist, poses = extract_sub_hist(hist_xz, hist_zx, j, n)
                expval, stddev = mit.expectation_value(hist, qubits=poses, clbits=poses, meas_mitigator=None)
                Es_m.append(expval)
                Ds_m.append(stddev)
            sum_corr = corr_deg + sum(Es_m[1:])
            if not silent:
                print("correlation on n[", m, "]:", sum_corr)
            corr_F += sum_corr
            Es_F.append(Es_m)
            Ds_F.append(Ds_m)

        # remainig part
        Es_R, Ds_R = [], []
        for i, _ in enumerate(remaining):
            hist, poses = extract_sub_hist(hist_xz, hist_zx, i, n)
            expval, stddev = mit.expectation_value(hist, qubits=poses, clbits=poses, meas_mitigator=None)
            Es_R.append(expval)
            Ds_R.append(stddev)
        corr_R = sum(Es_R)
        if not silent:
            print("correlation on remaining vertices:", corr_R)

        corr_F *= np.sqrt(2)
        corr_all = corr_F + corr_R
        corr_all_list.append(corr_all)
        stddev_all_list.append(np.sqrt(2 * sum([dev ** 2 for Ds_m in Ds_F for dev in Ds_m]) + sum([dev ** 2 for dev in Ds_R])))
        Es_all_list.append([Es_F, Es_R])
        Ds_all_list.append([Ds_F, Ds_R])
        print("total correlation:", corr_all, "\n")
    return corr_all_list, stddev_all_list, Es_all_list, Ds_all_list
