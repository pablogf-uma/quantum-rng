from qiskit import QuantumCircuit
import matplotlib.pyplot as plt

# Binary function:
def to_binary(number, nbits = None):
    output = bin(number)[2:]
    if nbits == None:
        return output # Array indexing to delete "0b"
    elif nbits > len(output):
        while nbits > len(output):
            output = '0' + output
        return output
    else:
        return output


# Multi-Control-Z function
def multi_control_z(n_qubits):
    qc = QuantumCircuit(n_qubits)
    qc.h(n_qubits - 1)
    qc.mcx(list(range(n_qubits - 1)), n_qubits - 1) # 1st parameter: list of controlling qubits | 2nd parameter: target qubit
    qc.h(n_qubits - 1)
    return qc


# Diffuser
def diffuser_circuit(n_qubits):
    qc = QuantumCircuit(n_qubits)
    for qb in range (n_qubits):
        qc.h(qb)
    for qb in range (n_qubits):
        qc.x(qb)
    multi_z = multi_control_z(n_qubits)
    qc.append(multi_z.to_gate(),  range(n_qubits-1, -1, -1))  
    for qb in range (n_qubits):
        qc.x(qb)
    for qb in range (n_qubits):
        qc.h(qb)
    return qc