from qiskit import QuantumCircuit

def adjacency_list_for_path_graph(n):
    """
    Input
        n : int, size of the path graph
    Output
        graph : list of list, adjacency list of the path graph
    """
    graph = []
    if n == 1:
        graph.append([])
    else:
        graph.append([1])
        for j in range(1, n - 1):
            graph.append([j - 1, j + 1])
        graph.append([n - 2])
    return graph


def adjacency_list_for_star_graph(n):
    """
    Input
        n : int, size of the star graph
    Output
        graph : list of list, adjacency list of the star graph
    """
    graph = []
    if n == 1:
        graph.append([])
    else:
        graph.append(list(range(1, n)))
        for j in range(1, n):
            graph.append([0])
    return graph


def list_to_matrix(graph):
    """
    Input
        graph : list of list (adjacency matrix)
    Output
        adj_matrix : 2d matrix (n * n)
        
    -> time complexity : O(n^2)
    """
    n = len(graph)
    adj_mat = []
    for i in range(n):
        row = [0] * n
        for j in graph[i]:
            row[j] = 1
        adj_mat.append(row)
    return adj_mat


def star_graph_state(size, order):
    if size <= 1:
        qc = QuantumCircuit(size)
        return qc
    qc = QuantumCircuit(size)
    qc.h(0)
    for i, j in order:
        qc.cx(i, j)
    qc.h(range(1, size))
    return qc


def path_graph_state(size, barrier=False):
    if size <= 1:
        qc = QuantumCircuit(size)
        return qc
    graph_state = QuantumCircuit(size)
    graph_state.h(range(size))
    if barrier:
        graph_state.barrier()
    for i in [i for i in range(size) if i % 2 == 0][:-1]:
        graph_state.cz(i, i + 1)
    if size % 2 == 0:
        graph_state.cz(size - 2, size - 1)
    for i in [i for i in range(size) if i % 2 == 1][:-1]:
        graph_state.cz(i, i + 1)
    if size % 2 == 1:
        graph_state.cz(size - 2, size - 1)
    return graph_state
