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

def multi_control_z(n_qubits):

    qc = QuantumCircuit(n_qubits)
    qc.h(n_qubits - 1)
    qc.mcx(n_qubits - 1)
    qc.h(n_qubits - 1)
    
    return qc


circuit = multi_control_z(6)
circuit.draw()


