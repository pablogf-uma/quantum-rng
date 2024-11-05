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

from qiskit import QuantumCircuit
import matplotlib.pyplot as plt

def multi_control_z(n_qubits):

    qc = QuantumCircuit(n_qubits)
    qc.h(n_qubits - 1)
    qc.mcx(list(range(n_qubits - 1)), n_qubits - 1) # 1st parameter: list of controlling qubits | 2nd parameter: target qubit
    qc.h(n_qubits - 1)
    
    return qc