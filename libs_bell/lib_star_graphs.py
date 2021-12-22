import numpy as np

from qiskit import QuantumCircuit, QuantumRegister
from qiskit import execute
from qiskit.compiler import transpile
import qiskit.ignis.mitigation as mit

############# job casting ############

def prepare_star_graph_qcs(qc,
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

    # first term: XZZ...Z ( == uniform ) <- measurement grouping
    new_qc1 = qc.copy("X" + "Z" * (n - 1))
    new_qc1 += QuantumCircuit(n, n)
    new_qc1.h(0)  # focus on the vertex measured by stabilizer "X"
    new_qc1.barrier()
    new_qc1.measure(range(n), range(n)[::-1])  # measure all
    new_qc1 = transpile(new_qc1, backend=backend, basis_gates=['sx', 'rz', 'cx'],
                        optimization_level=optimization_level,
                        initial_layout=initial_layout, seed_transpiler=42)

    # second term: ZXX...X ( == GHZ ) <- measurement grouping
    new_qc2 = qc.copy("Z" + "X" * (n - 1))
    new_qc2 += QuantumCircuit(n, n)
    new_qc2.h(range(1, n))  # ZXX...X
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


def prepare_star_graph_qcs_list(qc_graphs,  # list of qiskit.QuantumCircuit
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
    for qc, initial_layout in zip(qc_graphs, initial_layouts):
        qcs, nums_divide, nums_meas_cal, initial_layouts_ = \
            prepare_star_graph_qcs(qc,
                                   backend,
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
        jobs.append(execute(qcs[i:i + max_experiments], 
                            backend=backend,
                            shots=shots, 
                            optimization_level=optimization_level))
        print("circuits from", i, "to", min(i + max_experiments -
              1, len(qcs)), "are put on the real device.")
        i += max_experiments
    return jobs

############# analysis ############

def extract_two_qubit_hist(hist, pos1, pos2):
    ret_hist = {"00": 0, "01": 0, "10": 0, "11": 0}
    for k, v in hist.items():
        ret_hist[k[pos1] + k[pos2]] += v
    return ret_hist

def compute_stddev_of_grouping(stddevs):
    return np.sqrt(sum([stddev ** 2 for stddev in stddevs]))


def correlations_of_star_graphs(adj_lists, hist_list):
    """
    Input
        adj_lists         : list of adjacency list
        hist_list  : list of int list (list of hist)
    Output
        expval_all_list : list of float (correlation of each graph)
        stddev_all_list : list of float (standard deviation of each graph)
        Es_all_list     : list of list (term-wise correlation of each graph)
        Ds_all_list     : list of list (term-wise stddev of each graph)
    """
    expval_all_list, stddev_all_list, Es_all_list, Ds_all_list = [], [], [], []
    for adj_list in adj_lists:
        n = len(adj_list)
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
        hist = hist_list[2 * (n - 2)]
        expval1, stddev1 = mit.expectation_value(hist,
                                                 qubits=range(n),
                                                 clbits=range(n),
                                                 meas_mitigator=None)
        Es_1, Ds_1 = [expval1], [stddev1]

        # for the second term
        print("second term")
        Es_2, Ds_2 = [], []
        sum_expval2, sum_stddev2 = 0, 0
        hist = hist_list[2 * (n - 2) + 1]
        for pos in range(1, n):  # recover the two qubit expectation values
            expval2, stddev2 = mit.expectation_value(extract_two_qubit_hist(hist, 0, pos),
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
        print("total correlation:", sum_expval, "\n")
    return expval_all_list, stddev_all_list, Es_all_list, Ds_all_list
