from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_aer import AerSimulator

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
    qc.x(0) 

    return qc


# Less than oracle function
def less_than_oracle(number, n_qubits):

    qc = QuantumCircuit(n_qubits)
    number_binary = to_binary(number, n_qubits)
    number_binary = number_binary.rstrip('0')

    # Circuit to create "less than" oracle

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

    if number < (2**n_qubits): # if number is not the greater namber that can be represented using nqubits
        number=number+1

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
    qc.append(greater_than.to_gate(), range(0, n_qubits, 1))
    qc.append(less_than.to_gate(), range(0, n_qubits, 1))
    qc.append(pi_phase.to_gate(), range(0, -1, -1))

    return qc


# Range program: Creating a circuit where the range oracle is implemented
def range_of_program(lower_number, higher_number, n_qubits):

    cr = ClassicalRegister(n_qubits)
    qr = QuantumRegister(n_qubits)
    qc = QuantumCircuit(qr, cr)

    qc.h(qr)
    range_of = range_of_oracle(lower_number=lower_number, higher_number=higher_number, n_qubits=n_qubits)
    diffuser = diffuser_circuit(n_qubits)

    qc.append(range_of.to_gate(), range(0, n_qubits, 1))
    qc.append(diffuser.to_gate(), range(0, n_qubits, 1))
    qc.measure(qr,cr)

    return qc


# Simulate and get results for a specific range
sim = AerSimulator(method='statevector')
lower_number = 2
higher_number = 6
number_of_qubits = 4
print(f"\nRange between {lower_number} ({to_binary(lower_number, number_of_qubits)}) and {higher_number} ({to_binary(higher_number, number_of_qubits)})\n")


# Display numbers within the range by simulating the circuit with 200 shots
q_program = range_of_program(lower_number, higher_number, number_of_qubits) # "Create a circuit with amplitudes only in numbers between 2 and 6"
transpiled_program = transpile(q_program, backend = sim)
n_shots = 200
sim_run = sim.run(transpiled_program, shots = n_shots)
sim_result=sim_run.result()
counts_result = sim_result.get_counts()
# Display histogram as ASCII in terminal for the range of numbers
print("\nHistogram of random number results for 200 shots:")
max_count = max(counts_result.values())
for state, count in sorted(counts_result.items(), key=lambda x: int(x[0], 2)):
    bar = '█' * int((count / max_count) * 50)
    print(f"{state}: {bar} ({count})")
print("\n")

# Get a random number from the range
q_program = range_of_program(2,6,4)
transpiled_program = transpile(q_program, backend = sim)
n_shots = 1
sim_run = sim.run(transpiled_program, shots = n_shots)
sim_result=sim_run.result()
counts_result = sim_result.get_counts()
qrng = int(list(counts_result.keys())[0], 2)

print(f"Quantum random number generated: {qrng}\n")