import numpy as np
from math import sqrt
import random as rd
import math
import sys
# Imports
from qiskit import QuantumCircuit, transpile, ClassicalRegister, QuantumRegister
from qiskit import execute, IBMQ, transpile
from qiskit.circuit.library import MCXGate
from qiskit.extensions import UnitaryGate
from qiskit_aer import AerSimulator




def to_binary(number, nbits=None):
    
    '''
    This fucntion transforms an integer to its binary form (string).
    If a determined number of bits is required (more than the needed ones),
    it can be passed as a parameter too, nbits, None by default.
    It is needed that the number of bits passed as a parameter is larger
    than the number of bits needed to write the number in binary. 

    Input:
    number: integer (int).
    nbits: integer (int), None by default

    Output:
    binary: string (str) containing the number in its binary form.
    It writes 0s in front if nbits is larger than the number of bits needed
    to write the binary form.
    '''

    if nbits is None:
        return bin(number)[2:]
    else:
        binary = bin(number)[2:]
        if nbits < len(binary):
            print('Error, nbits must be larger than %d.'%(len(binary)))
        else:
            return '0' * (nbits - len(binary)) + binary
        




def multi_control_z(nqubits):
  '''
  Function to create a multi-controlled Z gate.

  Input:
  nqubits: Integer (int) of the number of qubits in the gate (controls and target)
      This means that the gate has nqubits-1 controls and 1 target.

  Output:
  circuit: QuantumCircuit containing a multi-controlled Z gate.
    It has to be transformed with method .to_gate() to append to a QuantumCircuit larger.

  Example:

  main_circuit = QuantumCircuit(nqubits)

  gate_multi_z = multi_control_z(nqubits)

  main_circuit.append(gate_multi_z.to_gate(), range(nqubits))
  '''
  circuit=QuantumCircuit(nqubits,name=' CZ (%d)' %(nqubits))
  circuit.h(nqubits-1)
  gate = MCXGate(nqubits-1)
  circuit.append(gate, range(nqubits))
  circuit.h(nqubits-1)
  return circuit


def diffuser_circuit(nqubits):
  '''
  Function to create the GROVER's diffuser circuit.

  Input:
  nqubits: Integer (int) of the number of qubits fo the circuit
  for wich the diffuser will be created.

  Output:
  circuit: QuantumCircuit containing the diffuser.
  It has to be transformed with method .to_gate() to append to a QuantumCircuit larger.

  Example:

  main_circuit = QuantumCircuit(nqubits)

  diffuser = difusser(nqubits)

  main_circuit.append(diffuser.to_gate(), range(nqubits-1, -1, -1))
  '''

  circuit=QuantumCircuit(nqubits,name=' Diffuser (%d)'%(nqubits))

  for qb in range (nqubits):
    circuit.h(qb)
  for qb in range (nqubits):
    circuit.x(qb)
  multi_z = multi_control_z(nqubits)
  circuit.append(multi_z.to_gate(),  range(nqubits-1, -1, -1))  
  for qb in range (nqubits):
    circuit.x(qb)
  for qb in range (nqubits):
    circuit.h(qb)
  return circuit



def globalphase():
    '''
    Function to create a gate the puts a global phase of Pi.
    The global phase can be applied afterwards to any qbit of a circuit

    Input:


    Output:
    circuit: QuantumCircuit containing the a sequence of gates that applied to any qbit of a circuit provides a 
    global phase of Pi to it
    It has to be transformed with method .to_gate() to append to a QuantumCircuit larger.

    Example:

    main_circuit = QuantumCircuit(nqubits)

    dg = globalphase(nqubits)

    main_circuit.append(globalphase.to_gate(), 0)
    '''
    circuit=QuantumCircuit(1,name=' GlobalPhase (%d)')

    circuit.z(0)
    circuit.x(0)
    circuit.z(0)
    circuit.x(0)
    

    return circuit


def oracle_less_than(number, nqubits, name=None):

    '''
    This function builds a quantum circuit, an oracle, which marks with a pi-phase
    those states which represent numbers strictly smaler than the number given by parameter.

    The procedure is almost the same for all numbers, with the only exception of a difference
    if the first bit of the number in binary is 1 or 0.

    Input:
    number: integer (int) containing the objective number,
       or a string (str) with the binary representation of such number.
    nqubits: integer (int) number of qubits of the circuit.
       It must be larger than the number of digits of the binary representation of number.
    name: string (str), default None, name of the circuit.

    Output:
    circuit: QuantumCircuit which marks with fase pi the states which
    represent in binary the numbers strictly smaller than number.
    '''

    # Construction of the circuit
    if name:# If name is provided give such name to the circuit
        circuit = QuantumCircuit(nqubits, name=name)
    else: # Otherwise, the name is just " < number"
        circuit = QuantumCircuit(nqubits, name = ' < %d '%number)

    # Binary representation of the number
    num_binary = to_binary(number, nqubits)
    
    # Discard the 0s at the end, as they will not be used and save
    # unnecessary X gates
    num_binary = num_binary.rstrip('0')

    
    if num_binary[0] == '1':
        # If the first digit is 1
        # Mark all the states of the form |0q1...>
        circuit.x(nqubits-1)
        circuit.z(nqubits-1)
        circuit.x(nqubits-1)
    else:
        # If first digit is 0
        # Apply X gate to first qubit
        circuit.x(nqubits-1)
    
    # For loop on the remaining digits
    for position1, value in enumerate(num_binary[1:]):
        # Rename the position as it starts with 0 in the second bit and
        # we want it to be 1.
        position = position1 + 1
        #for nq in range(nqubits):
        #    circuit.barrier(nq)

        if value == '0':
            # If the digit is 0
            # Just apply a X gate
            circuit.x(nqubits-position-1)
        else:
            # If the digit bi is 1
            # Apply a multi-controlled Z gate to mark states of the shape:
            # |bn...bi+1 0 qi-1...q1>
            # where bn,...,bi+1 are the first n-i bits of m, which is of the shape bn...bi+1 1 bi-1...b1
            # because we just checked that bi is 1.
            # Hence, the numbers of the form bn...bi+1 0 qi-1...q1 are smaller than m.
            circuit.x(nqubits-position-1)
            multi_z = multi_control_z(position + 1)
            circuit.append(multi_z.to_gate(), range(nqubits-1, nqubits-position-2, -1))
            circuit.x(nqubits-position-1)
    
    for position, value in enumerate(num_binary):
        # Apply X gates to qubits in position of bits with a 0 value
        #for nq in range(nqubits):
        #    circuit.barrier(nq)
        if value == '0':
            circuit.x(nqubits-position-1)
        else:
            pass
    
    return circuit



def oracle_greater_than(number, nqubits, name=None):

    '''
    This function builds a quantum circuit, an oracle, which marks with a pi-phase
    those states which represent numbers strictly grater than the number given by parameter.

    The procedure is almost the same for all numbers, with the only exception of a difference
    if the first bit of the number in binary is 1 or 0.

    Input:
    number: integer (int) containing the objective number,
       or a string (str) with the binary representation of such number.
    nqubits: integer (int) number of qubits of the circuit.
       It must be larger than the number of digits of the binary representation of number.
    name: string (str), default None, name of the circuit.

    Output:
    circuit: QuantumCircuit which marks with fase pi the states which
    represent in binary the numbers strictly greatersmaller than number.

    This oracle relais on the use of the less_tan oracle levaraging the propertry:
    gretar_than (x) = less_than (x+1) + globelphase
    '''

    # Construction of the circuit
    if name:# If name is provided give such name to the circuit
        circuit = QuantumCircuit(nqubits, name=name)
    else: # Otherwise, the name is just " < number"
        circuit = QuantumCircuit(nqubits, name = ' > %d '%number)

    if number < (2**nqubits): # if number is not the greater namber that can be represented using nqubits
        number=number+1

    less_than = oracle_less_than(number=number, nqubits=nqubits)
    gp = globalphase()
    circuit.append(less_than.to_gate(),  range(0,nqubits, 1))
    #circuit.append(less_than.to_gate(),  range(nqubits-1, -1, -1))  
    circuit.append(gp.to_gate(), range(0, -1, -1))
    return circuit




def oracle_range_of(lower,upper, nqubits, name=None):

    '''
    This function builds a quantum circuit, an oracle, which marks with a pi-phase
    those states which represent numbers strictly grater than lower and stricly less than upper.

    This oracle relais on the use of the less_than and greater_than oracles

    Input:
    lower: lower limit of the range.
    upper: upper limet of the range
    nqubits: integer (int) number of qubits of the circuit.
       It must be larger than the number of digits of the binary representation of number.
    name: string (str), default None, name of the circuit.

    Output:
    circuit: QuantumCircuit which marks with fase pi the states which
    represent in binary the numbers strictly greater and less than lower and upper respectively.

    '''

    # Construction of the circuit
    if name:# If name is provided give such name to the circuit
        circuit = QuantumCircuit(nqubits, name=name)
    else: 
        circuit = QuantumCircuit(nqubits, name = ' range_of  ')
    less=oracle_less_than(upper,nqubits)
    greater=oracle_greater_than(lower,nqubits)
    gp = globalphase()
    circuit.append(greater.to_gate(),  range(0, nqubits, 1)) 
    circuit.append(less.to_gate(),  range(0, nqubits, 1)) 
    #range(nqubits-1, -1, -1)
    circuit.append(gp.to_gate(), range(0, -1, -1))
    return circuit





def program_range_of (nqubits,number_lower,number_upper):
  # This program creates the circuit of a qiskit program that produces a quantum states of nqubits qbits
  # where all the values of the state less than number_less_than have the greater amplitude
  qreg = QuantumRegister(nqubits)
  creg = ClassicalRegister(nqubits)
  qprogram = QuantumCircuit(qreg,creg)
  qprogram.h(qreg)
  diffuser = diffuser_circuit(nqubits)
  range_of_oracle = oracle_range_of(lower=number_lower, upper=number_upper, nqubits=nqubits)

  sq = 2**nqubits
  fr=sq/(number_upper-number_lower)
  numit=round(fr)+1
  if numit == 0:
    numit=1
  #numit=6
  print (numit)
  for i in range(numit):
    qprogram.append(range_of_oracle.to_gate(), range(0, nqubits, 1))
    qprogram.append(diffuser.to_gate(), range(0, nqubits, 1))
  qprogram.measure(qreg,creg)
  return qprogram






nqubits = 4
number_lower = 1
number_upper = 4

method = "statevector"
sim = AerSimulator(method = method)


qp = program_range_of(nqubits, number_lower, number_upper)
qp.draw()

transpiled_circuit = transpile(qp, backend = sim)

nshots = 200
sim_run = sim.run(transpiled_circuit, shots = nshots)
sim_result=sim_run.result()
counts_result = sim_result.get_counts(qp)

print('''Printing the various results followed by how many times they happened (out of the {} cases):\n'''.format(nshots), flush = True)
for i in range(len(counts_result)):
  print('-> Result \"{0}\" happened {1} times out of {2}'.format(
  list(sim_result.get_counts().keys())[i],
  list(sim_result.get_counts().values())[i],nshots), 
  flush = True)
qp.draw()