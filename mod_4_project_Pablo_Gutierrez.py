from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_aer import AerSimulator
from IPython.display import display

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


# Single qubit pi phase adder function
def pi_phase_adder():

    qc = QuantumCircuit(1)
    qc.z(0)
    qc.x(0)
    qc.z(0)
    qc.h(0) 

    return qc


# Less than oracle function
def less_than_oracle(number, n_qubits):

    # Convert "number" to binary depending on data type input
    if isinstance(number, int):
        number_binary = to_binary(number)
    elif set(str(number)).issubset({'0', '1'}) == True:
        number_binary = str(number)
    else:
        return "Invalid number input."

    # Make sure "number" can be represented with the number of qubits input
    if n_qubits >= len(number_binary):
        qc = QuantumCircuit(n_qubits)
    else:
        return "Number input is not consistent with the number of qubits input."

    # Circuit to create "less than" oracle
    qc.h(range(n_qubits)) # Create superposition of all possible states

    # If the most significant qubit is 1, apply Z (not controlled)
    if number_binary[0] == '1':
        qc.x(n_qubits - 1)
        qc.z(n_qubits - 1)
        qc.x(n_qubits - 1)
    else:
        qc.x(n_qubits - 1)

    # Add a multicontrol z to all qubits that have 1 as input
    for index, i in enumerate(number_binary):
        
        if i == '0' and index != 0:
            qc.x(n_qubits - index - 1)
        elif i == '1' and index != 0:
            qc.x(n_qubits - index - 1)
            multi_z = multi_control_z(index + 1)
            qc.append(multi_z.to_gate(), range(n_qubits - 1, n_qubits - index - 2, -1))
            qc.x(n_qubits - index - 1)
        #qc.barrier()  # Add barrier to separate all qubits

    # Add CNOTS to qubits with 0 as input
    for index, i in enumerate(number_binary):
        if i == '0':
            qc.x(n_qubits - index - 1)
        else:
            pass
    
    return qc


# Greater than oracle function
def greater_than_oracle(number, n_qubits):

    qc = QuantumCircuit(n_qubits)

    # Create less than and global pi phase adder circuits
    less_than = less_than_oracle(number=number, n_qubits=n_qubits)
    pi_phase = pi_phase_adder()

    # Append them to the general circuit
    qc.append(less_than.to_gate(),  range(0,n_qubits, 1))
    qc.append(pi_phase.to_gate(), range(0, -1, -1)) # This range is only outputting 0, so the pi phase is only added to the LSQubit

    return qc


# Range fuction
def range_of_oracle(lower_number, higher_number, n_qubits):

    qc = QuantumCircuit(n_qubits)

    # Create greater and less than oracles based on the numbers input
    less_than = less_than_oracle(higher_number, n_qubits)
    greater_than = greater_than_oracle(lower_number, n_qubits)
    pi_phase = pi_phase_adder()

    # Append them to the general circuit
    qc.append(less_than.to_gate(), range(0, n_qubits, 1))
    qc.append(greater_than.to_gate(), range(0, n_qubits, 1))
    qc.append(pi_phase.to_gate(), range(0, -1, -1))

    return qc


# Range program: Creating a circuit where the range oracle is implemented and simulated
def range_of_program(lower_number, higher_number, n_qubits):

    cr = ClassicalRegister(n_qubits)
    qr = QuantumRegister(n_qubits)
    qc = QuantumCircuit(qr, cr)

    range_of = range_of_oracle(lower_number, higher_number, n_qubits)
    diffuser = diffuser_circuit(n_qubits)

    qc.append(range_of.to_gate(), range(0, n_qubits, 1))
    qc.append(diffuser.to_gate(), range(0, n_qubits, 1))

    return qc

sim = AerSimulator(method='statevector')

q_program = range_of_program(3, 8, 4)

transpiled_program = transpile(q_program, backend = sim)
shots = 200
sim_run = sim.run(transpiled_program, shots)
result = sim_run.result()
counts = result.get_counts(q_program)

# Print the circuit
display(q_program.draw('mpl'))

# This outputs how many times the numbers within the range were outputted
print(counts)