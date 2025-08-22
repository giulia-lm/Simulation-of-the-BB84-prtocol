import pennylane as qml
import random

dev = qml.device("default.mixed", wires=1, shots=1)

@qml.qnode(dev)
def alice_eve_circuit(alice_bit, aliceBasis, eveBasis, p):
    #alice prepares her bits
    if alice_bit == 1:
        qml.PauliX(wires=0)
    if aliceBasis == 'x':
        qml.Hadamard(wires=0)

    # introducing noise into the channel with probability p
    qml.DepolarizingChannel(p ,wires =0)
    qml.BitFlip(p ,wires =0)

    # eve measures 
    if eveBasis == 'x':
        qml.Hadamard(wires=0)

    eve_bit = qml.sample(wires=0)

    return eve_bit

@qml.qnode(dev)
def eve_bob_circuit(eve_bit, eveBasis, bobBasis, p):
   # eve reprepares according to what she measured
    if eve_bit == 1:
        qml.PauliX(wires=0)
    if eveBasis == 'x':
        qml.Hadamard(wires=0)

    qml.DepolarizingChannel(p ,wires =0)
    qml.BitFlip(p ,wires =0)

    # bob measures
    if bobBasis == 'x':
        qml.Hadamard(wires=0)
    return qml.sample(wires=0)

def bb84(n, p, p_range=[0.6,0.4], sample=True):
    bob_bits = []
    eve_bits = []
    bob_sifted = []
    alice_sifted = []
    
    alice_bits = [random.choices([0, 1], weights=p_range)[0] for _ in range(n)]
    aliceBasis = [random.choices(['+', 'x'], weights=p_range)[0] for _ in range(n)]
    bobBasis = [random.choices(['+', 'x'], weights=p_range)[0] for _ in range(n)]
    eveBasis = [random.choices(['+', 'x'], weights=p_range)[0] for _ in range(n)]

    for i in range(n):
        eve_bit = int(alice_eve_circuit(alice_bits[i], aliceBasis[i], eveBasis[i], p))
        bob_bit = int(eve_bob_circuit(eve_bit, eveBasis[i], bobBasis[i], p))
        eve_bits.append(eve_bit)
        bob_bits.append(bob_bit)

    for i in range(n):
        if aliceBasis[i] == bobBasis[i]:
            bob_sifted.append(bob_bits[i])
            alice_sifted.append(alice_bits[i])


    return alice_sifted, bob_sifted, eve_bits

def is_secure(threshold, alice_final_key, bob_final_key):
    error = sum(e != k for e,k in zip(alice_final_key, bob_final_key))/len(alice_final_key)
    if error < threshold:
        return True
    else:
        return False
    
if __name__=="__main__":
    print("="*50)
    print("           BB84 Protocol Key Generation Demo")
    print("="*50)
    
    while True:
        try:
            n = int(input("Enter the desired key length (e.g., 32): "))
            if n <= 0:
                print("Please enter a positive integer.")
                continue
            break
        except ValueError:
            print("Invalid input. Please enter an integer.")

    i = 0
    secure = False
    while(not secure):
        alice_sifted, bob_sifted, eve_bits = bb84(n, p=0, p_range=[0.5,0.5])

        secure = is_secure(0.1, alice_sifted, bob_sifted)
        if secure:
            final_key = "".join(str(b) for b in alice_sifted)
            print("\n" + "="*60)
            print("Secure key generated!")
            print(f"The key is: {final_key}")
            print("\n" + "="*60)
            secure = True
        else:
            print(f"No matching bases, retrying... (Iteration #{i})")
        i += 1

