from typing import List
import time
import numpy as np
from scipy import optimize

from qiskit import ClassicalRegister, QuantumRegister, QuantumCircuit
from qiskit import execute

### ============================================ pre-processing =========================================== ###

# OK
def P(qc, qx, nbit):
    """
        Generating uniform probability distribution
            qc: quantum circuit
            qx: quantum register
            nbit: number of qubits
        The inverse of P = P
    """
    qc.h(qx)

# OK
def R(qc, qx, qx_measure, nbit, b_max):
    """
        Computing the integral function f()
            qc: quantum circuit
            qx: quantum register
            qx_measure: quantum register for measurement
            nbit: number of qubits
            b_max: upper limit of integral            
    """
    qc.ry(b_max / 2**nbit * 2 * 0.5, qx_measure)
    for i in range(nbit):
        qc.cu3(2**i * b_max / 2**nbit * 2, 0, 0, qx[i], qx_measure[0])

# OK
def Rinv(qc, qx, qx_measure, nbit, b_max):
    """3
        The inverse of R
            qc: quantum circuit
            qx: quantum register
            qx_measure : quantum register for measurement
            nbit: number of qubits
            b_max: upper limit of integral
    """
    for i in range(nbit)[::-1]:
        qc.cu3(-2**i * b_max / 2**nbit * 2, 0, 0, qx[i], qx_measure[0])
    qc.ry(-b_max / 2**nbit * 2 * 0.5, qx_measure)

# OK
def reflect(qc, qx, qx_measure, qx_ancilla, nbit, b_max, barrier=False):
    """
        Computing reflection operator (I - 2|0><0|)
            qc: quantum circuit
            qx: quantum register
            qx_measure: quantum register for measurement
            qx_ancilla: temporal quantum register for decomposing multi controlled NOT gate
            nbit: number of qubits
            b_max: upper limit of integral
    """
    for i in range(nbit):
        qc.x(qx[i])
    qc.x(qx_measure[0])
    if barrier:
        qc.barrier()  # format the circuits visualization
    # multi_control_NOT(qc, qx, qx_measure, qx_ancilla, nbit, b_max)
    qc.h(qx_measure)
    qc.mcx(qx, qx_measure)
    qc.h(qx_measure)
    if barrier:
        qc.barrier()  # format the circuits visualization
    qc.x(qx_measure[0])
    for i in range(nbit):
        qc.x(qx[i])


# OK
# This is to implement Grover Operator
def Q_grover(qc, qx, qx_measure, qx_ancilla, nbit, b_max, barrier=False):
    """
        The Grover operator: R P (I - 2|0><0|) P^+ R^+ U_psi_0 
            qc: quantum circuit
            qx: quantum register
            qx_measure: quantum register for measurement
            qx_ancilla: temporal quantum register for decomposing multi controlled NOT gate
            nbit: number of qubits
            b_max: upper limit of integral
    """
    P(qc, qx, nbit)
    if barrier:
        qc.barrier()  # format the circuits visualization
    R(qc, qx, qx_measure, nbit, b_max)
    qc.z(qx_measure[0])
    Rinv(qc, qx, qx_measure, nbit, b_max)
    if barrier:
        qc.barrier()  # format the circuits visualization
    P(qc, qx, nbit)
    if barrier:
        qc.barrier()  # format the circuits visualization
    reflect(qc, qx, qx_measure, qx_ancilla, nbit, b_max, barrier)
    if barrier:
        qc.barrier()  # format the circuits visualization


# OK
def create_grover_circuit(numebr_grover_list, nbit, b_max, barrier=False):
    """
        To generate quantum circuits running Grover operators with number of iterations in number_grover_list
            numebr_grover_list: list of number of Grover operators
            nbit: number of qubits (2**nbit = ndiv is the number of discretization in the Monte Carlo integration)
            b_max: upper limit of integral
        Return:
            qc_list: quantum circuits with Grover operators as in number_grover_list
    """
    qc_list = []
    for igrover in range(len(numebr_grover_list)):
        qx = QuantumRegister(nbit)
        qx_measure = QuantumRegister(1)
        cr = ClassicalRegister(nbit + 1)  # modified grover
        qc = QuantumCircuit(qx, qx_measure, cr)
        qx_ancilla = QuantumRegister(1)
        for ikAA in range(numebr_grover_list[igrover]):
            Q_grover(qc, qx, qx_measure, qx_ancilla, nbit, b_max, barrier)
        qc.measure(qx, cr[:-1])  # modified grover
        qc.measure(qx_measure, cr[-1])  # modified grover
        qc_list.append(qc)
    return qc_list



# OK
def run_grover(qc_list, number_grover_list, shots_list, backend, noise_model=None, seed_transpiler=None, seed_simulator=None):
    """
        Run the quantum circuits returned by create_grover_circuit()
            qc_list: list of quantum circuits
            numebr_grover_list: list of number of Grover operators
            shots_list:  list of number of shots
            backend: name of backends
        
        Return:
            hit_list: list of count of obserbving "1" for qc_list
    """
    counts_list = []
    for k in range(len(number_grover_list)):
        t1 = time.time()
        print(k, "th round with", number_grover_list[k], "oracles")
        job = execute(qc_list[k], backend=backend, shots=shots_list[k], noise_model=noise_model, seed_transpiler=seed_transpiler, seed_simulator=seed_simulator)
        lapse = 0
        interval = 0.00001
        time.sleep(interval)
        while job.status().name != 'DONE':
            time.sleep(interval)
            lapse += 1
        counts_list.append(job.result().get_counts(qc_list[k]))
        t2 = time.time()
        print(t2 - t1, "s")
    return counts_list

### ============================================ post-processing =========================================== ###

# OK
def make_hit_list(counts_list: List[dict]):
    hit_list = []
    strlen = len(list(counts_list[0].keys())[0])
    for k in range(len(counts_list)):
        hits = counts_list[k].get("0"*strlen, 0)
        hit_list.append(hits)
    return hit_list

# OK
def CalcErrorCramérRao(M, shots_list, p0, number_grover_list):
    """
        calculate Cramér-Rao lower bound
            M: upper limit of the sum in Fisher information 
            shots_list:  list of number of shots
            p0: the true parameter value to be estimated
            numebr_grover_list: list of number of Grover operators        

        Return:
            square root of Cramér-Rao lower bound:  lower bound on the standard deviation of unbiased estimators
    """
    FisherInfo = 0
    for k in range(M + 1):
        Nk = shots_list[k]
        mk = number_grover_list[k]
        FisherInfo += Nk / (p0 * (1 - p0)) * (2 * mk + 1)**2
    return np.sqrt(1 / FisherInfo)

# OK
def CalcNumberOracleCalls(M, shots_list, number_grover_list):
    """
        calculate the total number of oracle calls
            M: upper limit of the sum in Fisher information 
            shots_list:  list of number of shots
            numebr_grover_list: list of number of Grover operators        

        Return:
            Norac: the total number of oracle calls
    """
    Norac = 0
    for k in range(M + 1):
        Nk = shots_list[k]
        mk = number_grover_list[k]
        Norac += Nk * (2 * mk + 1)
    return Norac

# OK
def calculate_theta(hit_list, number_grover_list, shots_list):
    """
        calculate optimal theta values
            hit_list: list of count of obserbving "1" for qc_list
            numebr_grover_list: list of number of Grover operators        
            shots_list: list of number of shots

        Return:
            thetaCandidate_list: list of optimal theta
    """

    small = 1.e-15  # small valued parameter to avoid zero division
    confidenceLevel = 5  # confidence level to determine the search range

    thetaCandidate_list = []
    rangeMin = 0.0 + small
    rangeMax = 1.0 - small
    for igrover in range(len(number_grover_list)):

        def loglikelihood(p):  # search value
            ret = np.zeros_like(p)
            theta = np.arcsin(np.sqrt(p))  # search theta
            for n in range(igrover + 1):
                ihit = hit_list[n]  # empirical value
                arg = (2 * number_grover_list[n] + 1) * theta  # search angle
                ret = ret + 2 * ihit * np.log(np.abs(np.sin(arg))) + 2 * (
                    shots_list[n] - ihit) * np.log(np.abs(np.cos(arg)))  # search log likelihood
            return -ret

        searchRange = (rangeMin, rangeMax)
        searchResult = optimize.brute(loglikelihood, [searchRange])
        pCandidate = searchResult[0]
        thetaCandidate_list.append(np.arcsin(np.sqrt(pCandidate)))
        perror = CalcErrorCramérRao(
            igrover, shots_list, pCandidate, number_grover_list)
        rangeMax = min(pCandidate+confidenceLevel*perror, 1.0 - small)
        rangeMin = max(pCandidate-confidenceLevel*perror, 0.0 + small)
    return thetaCandidate_list
