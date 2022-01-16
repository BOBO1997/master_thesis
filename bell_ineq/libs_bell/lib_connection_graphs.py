import numpy as np

from qiskit import QuantumCircuit, QuantumRegister
from qiskit import execute
from qiskit.compiler import transpile
import qiskit.ignis.mitigation as mit


def prepare_connection_graph_qcs(qc, base_type1, base_type2, backend, optimization_level = 1, initial_layout = None):
    
    n = qc.num_qubits
    qcs = []

    new_qc1 = qc.copy("XZ pattern")
    new_qc1 += QuantumCircuit(n, n)
    new_qc1.h(base_type1)
    new_qc1.barrier()
    new_qc1.measure(range(n), range(n)[::-1])  # measure all
    new_qc1 = transpile(new_qc1, backend=backend, basis_gates=['sx', 'rz', 'cx'],
                        optimization_level=optimization_level,
                        initial_layout=initial_layout, seed_transpiler=42)

    # second term: ZXZX...XZXZX <- measurement grouping
    new_qc2 = qc.copy("ZX pattern")
    new_qc2 += QuantumCircuit(n, n)
    new_qc2.h(base_type2)
    new_qc2.barrier()
    new_qc2.measure(range(n), range(n)[::-1])  # measure all
    new_qc2 = transpile(new_qc2, backend=backend, basis_gates=['sx', 'rz', 'cx'],
                        optimization_level=optimization_level,
                        initial_layout=initial_layout, seed_transpiler=42)
    
    # for mitigation circuits
    qr = QuantumRegister(n)
    meas_cal_circuits, _ = mit.tensored_meas_cal(mit_pattern=[[i] for i in range(n)], qr=qr, circlabel='mcal')
    for i, meas_cal_circuit in enumerate(meas_cal_circuits):
        meas_cal_circuits[i] = transpile(meas_cal_circuit, backend=backend, basis_gates=['sx', 'rz', 'cx'],
                                         optimization_level=optimization_level,
                                         initial_layout=initial_layout, seed_transpiler=42)
    qcs += ([new_qc1, new_qc2] + meas_cal_circuits)

    return qcs


def remaining_vertices(adj_list, n, F):
    remaining = set(range(n)) - set(F)
    for m in F:
        for v in adj_list[m]:
            remaining.discard(v)
    return list(remaining)


def extract_two_qubit_hist(hist, pos1, pos2):
    ret_hist = {format(i, "02b"): 0 for i in range(2 ** 2)}
    for k, v in hist.items():
        ret_hist[k[pos1] + k[pos2]] += v
    return ret_hist


def extract_three_qubit_hist(hist, pos1, pos2, pos3):
    ret_hist = {format(i, "03b"): 0 for i in range(2 ** 3)}
    for k, v in hist.items():
        ret_hist[k[pos1] + k[pos2] + k[pos3]] += v
    return ret_hist


def extract_four_qubit_hist(hist, pos1, pos2, pos3, pos4):
    ret_hist = {format(i, "04b"): 0 for i in range(2 ** 4)}
    for k, v in hist.items():
        ret_hist[k[pos1] + k[pos2] + k[pos3] + k[pos4]] += v
    return ret_hist

def extract_sub_hist(hist_xz, hist_zx, center, adj_list, base_type1, base_type2):

    n = len(adj_list)
    if center in base_type1: # xz
        if len(adj_list[center]) == 1:
            return extract_two_qubit_hist(hist_xz, center, adj_list[center][0]), [center] + adj_list[center]
        elif len(adj_list[center]) == 2:
            return extract_three_qubit_hist(hist_xz, center, adj_list[center][0], adj_list[center][1]), [center] + adj_list[center]
        elif len(adj_list[center]) == 3:
            return extract_four_qubit_hist(hist_xz, center, adj_list[center][0], adj_list[center][1], adj_list[center][2]), [center] + adj_list[center]
        else:
            raise Exception
    elif center in base_type2: # zx
        if len(adj_list[center]) == 1:
            return extract_two_qubit_hist(hist_zx, center, adj_list[center][0]), [center] + adj_list[center]
        elif len(adj_list[center]) == 2:
            return extract_three_qubit_hist(hist_zx, center, adj_list[center][0], adj_list[center][1]), [center] + adj_list[center]
        elif len(adj_list[center]) == 3:
            return extract_four_qubit_hist(hist_zx, center, adj_list[center][0], adj_list[center][1], adj_list[center][2]), [center] + adj_list[center]
        else:
            raise Exception
    else:
        raise Exception


def correlation_of_connection_graphs(adj_list, F, hist_list, base_type1, base_type2, silent = True):
    
    assert len(hist_list) % 2 == 0

    n = len(adj_list)
    print("graph size:", n)

    # XZ type
    hist_xz = hist_list[0]
    # ZX type
    hist_zx = hist_list[1]

    Es_F, Ds_F, corr_F = [], [], 0
    remaining = remaining_vertices(adj_list, n, F)

    for m in F:
        hist, _ = extract_sub_hist(hist_xz, hist_zx, m, adj_list, base_type1, base_type2)
        corr_itself, stddev_itself = mit.expectation_value(hist, meas_mitigator=None)
        corr_deg = corr_itself * len(adj_list[m])
        Es_m, Ds_m = [corr_itself], [stddev_itself * len(adj_list[m])]
        for j, _ in enumerate(adj_list[m]):
            hist, _ = extract_sub_hist(hist_xz, hist_zx, j, adj_list, base_type1, base_type2)
            expval, stddev = mit.expectation_value(hist, meas_mitigator=None)
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
        hist, _ = extract_sub_hist(hist_xz, hist_zx, i, adj_list, base_type1, base_type2)
        expval, stddev = mit.expectation_value(hist, meas_mitigator=None)
        Es_R.append(expval)
        Ds_R.append(stddev)
    corr_R = sum(Es_R)
    if not silent:
        print("correlation on remaining vertices:", corr_R)

    corr_F *= np.sqrt(2)
    corr_all = corr_F + corr_R
    stddev_all = np.sqrt(2 * sum([dev ** 2 for Ds_m in Ds_F for dev in Ds_m]) + sum([dev ** 2 for dev in Ds_R]))
    Es_all = [Es_F, Es_R]
    Ds_all = [Ds_F, Ds_R]
    print("total correlation:", corr_all, "\n")
    return corr_all, stddev_all, Es_all, Ds_all
