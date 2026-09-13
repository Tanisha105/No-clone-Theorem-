"""
teleportation_demo.py

The no-cloning theorem forbids COPYING an unknown quantum state, but it
does not forbid MOVING one. Quantum teleportation is the standard proof
that transport is possible: it consumes one shared Bell pair and two
classical bits, ends with Bob holding a state identical to Alice's
original, and — critically — destroys Alice's original in the process
of measuring it. Zero copies ever exist at once, so no-cloning is never
violated.

This script builds the textbook 3-qubit teleportation circuit:
  q0 = the unknown state |psi> Alice wants to send
  q1 = Alice's half of a shared Bell pair
  q2 = Bob's half of that same Bell pair

and verifies, over many random |psi>, that Bob's qubit ends up in exactly
|psi> (fidelity 1.0) after Alice's Bell measurement and the corresponding
classical-controlled correction -- while Alice's own qubit q0 has been
irreversibly measured/destroyed along the way.

Run directly:
    python src/teleportation_demo.py
"""

from __future__ import annotations

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector, random_statevector, state_fidelity
from qiskit_aer import AerSimulator


def build_teleportation_circuit(psi: Statevector) -> QuantumCircuit:
    """
    3 qubits: q0 = Alice's unknown state, q1 = Alice's half of the Bell
    pair, q2 = Bob's half. 2 classical bits carry Alice's measurement
    results to Bob over what the lecture calls "the classical channel" --
    without them Bob cannot recover |psi>, which is also why teleportation
    never sends information faster than light.
    """
    qc = QuantumCircuit(3, 2, name="teleport")
    qc.prepare_state(psi, [0])  # Alice's unknown qubit to be sent

    # Shared Bell pair between Alice (q1) and Bob (q2)
    qc.h(1)
    qc.cx(1, 2)
    qc.barrier()

    # Alice's Bell-basis measurement on her two qubits (q0, q1)
    qc.cx(0, 1)
    qc.h(0)
    qc.measure(0, 0)
    qc.measure(1, 1)
    qc.barrier()

    # Bob applies the correction implied by Alice's two classical bits
    # (modern Qiskit dynamic-circuit syntax; c_if was removed in Qiskit 1.0+)
    with qc.if_test((qc.clbits[1], 1)):
        qc.x(2)
    with qc.if_test((qc.clbits[0], 1)):
        qc.z(2)
    return qc


def run_teleportation(psi: Statevector, shots: int = 1) -> Statevector:
    """Simulate the circuit and return Bob's final single-qubit state."""
    qc = build_teleportation_circuit(psi)
    qc.save_statevector()
    sim = AerSimulator(method="statevector")
    qc = transpile(qc, sim)  # decompose state_preparation into simulator-native gates
    result = sim.run(qc, shots=shots).result()
    full_state = result.get_statevector(qc)
    # Bob's qubit is index 2; qiskit orders statevector qubits little-endian,
    # so we extract q2's marginal via a partial trace over q0, q1.
    from qiskit.quantum_info import DensityMatrix, partial_trace

    rho_bob = partial_trace(DensityMatrix(full_state), [0, 1])
    return rho_bob


def main() -> None:
    print("=" * 78)
    print("Quantum teleportation: transport without cloning")
    print("=" * 78)

    rng = np.random.default_rng(42)
    n_trials = 5
    fidelities = []
    for i in range(n_trials):
        psi = random_statevector(2, seed=int(rng.integers(0, 1_000_000)))
        rho_bob = run_teleportation(psi)
        fid = state_fidelity(rho_bob, psi)
        fidelities.append(fid)
        print(f"Trial {i + 1}: random |psi> teleported with fidelity = {fid:.6f}")

    print()
    print(f"Average fidelity over {n_trials} random states: {np.mean(fidelities):.6f}")
    print()
    print("Bob recovers |psi> exactly (fidelity ~1.0) every time, but only")
    print("after Alice measures her qubits -- which destroys her copy of")
    print("|psi> and collapses it to one of four Bell outcomes. At no point")
    print("do two copies of |psi> exist simultaneously, so this transports")
    print("information without ever cloning it.")


if __name__ == "__main__":
    main()
