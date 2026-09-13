"""
no_cloning_demo.py

A computational demonstration of the quantum no-cloning theorem.

The no-cloning theorem states that there is no unitary operation U such
that U(|psi> tensor |0>) = |psi> tensor |psi> for an ARBITRARY, unknown
input state |psi>. Cloning is only possible for a fixed, known set of
mutually orthogonal states (like the computational basis |0>/|1>).

This script builds the simplest candidate "cloning machine" available in
Qiskit -- a single CNOT gate -- which perfectly "clones" the computational
basis states |0> and |1>, and shows it fails for any genuine superposition,
exactly as the theorem predicts. It quantifies the failure with quantum
state fidelity, and shows that what comes out of the attempt is not two
independent copies at all, but a single entangled two-qubit state.

Run directly:
    python src/no_cloning_demo.py
"""

from __future__ import annotations

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import DensityMatrix, Statevector, partial_trace, state_fidelity


def build_cnot_cloner(theta: float, phi: float = 0.0) -> QuantumCircuit:
    """
    Prepare qubit 0 in |psi> = cos(theta/2)|0> + e^(i*phi) sin(theta/2)|1>,
    leave qubit 1 in |0>, then attempt to copy |psi> onto qubit 1 with a
    single CNOT(control=0, target=1).

    A CNOT is the natural first guess for a "cloning machine": it is exactly
    the reversible copy operation classical computing relies on, and it does
    perfectly copy the two computational basis states. The question this
    module answers is what it does to everything in between.
    """
    qc = QuantumCircuit(2, name="cnot_cloner")
    qc.ry(theta, 0)  # prepare the state to be "cloned" on qubit 0
    qc.rz(phi, 0)
    qc.cx(0, 1)      # the naive "copy" operation
    return qc


def target_state(theta: float, phi: float = 0.0) -> Statevector:
    """The single-qubit state we WANT qubit 1 to end up in if cloning worked."""
    qc = QuantumCircuit(1)
    qc.ry(theta, 0)
    qc.rz(phi, 0)
    return Statevector(qc)


def cloning_fidelity(theta: float, phi: float = 0.0) -> float:
    """
    Run the CNOT cloner and measure how close qubit 1 ends up to the
    original |psi>, via the fidelity between qubit 1's REDUCED density
    matrix (qubit 0 traced out) and the ideal target state.

    Fidelity 1.0 -> perfect clone. Fidelity < 1.0 -> cloning failed.
    """
    full_state = Statevector(build_cnot_cloner(theta, phi))
    rho1 = partial_trace(DensityMatrix(full_state), [0])
    return state_fidelity(rho1, target_state(theta, phi))


def is_entangled(theta: float, phi: float = 0.0, tol: float = 1e-9) -> bool:
    """
    A genuine clone would leave qubits 0 and 1 in an UNENTANGLED product
    state |psi> tensor |psi>. Detect entanglement by checking whether
    qubit 1's reduced state is mixed: purity = Tr(rho^2) < 1 means mixed,
    which is only possible if qubit 1 is entangled with qubit 0.
    """
    full_state = Statevector(build_cnot_cloner(theta, phi))
    rho1 = partial_trace(DensityMatrix(full_state), [0])
    purity = np.real(np.trace(rho1.data @ rho1.data))
    return bool(purity < 1 - tol)


def analytic_fidelity(theta: float) -> float:
    """
    Closed-form check (real amplitudes, phi=0): after CNOT, qubit 1's
    reduced state is diagonal with populations cos^2(theta/2), sin^2(theta/2).
    Qiskit's state_fidelity(rho, |psi>), for a pure target, reduces to
    <psi|rho|psi> = cos^4(theta/2) + sin^4(theta/2). This is used only to
    cross-check the simulator result -- see tests/test_no_cloning.py.
    """
    c, s = np.cos(theta / 2) ** 2, np.sin(theta / 2) ** 2
    return float(c**2 + s**2)


def main() -> None:
    print("=" * 78)
    print("No-Cloning Theorem check: can a CNOT gate clone an arbitrary qubit?")
    print("=" * 78)

    cases = [
        ("|0>", 0.0, 0.0),
        ("|1>", np.pi, 0.0),
        ("|+> = (|0> + |1>)/sqrt(2)", np.pi / 2, 0.0),
        ("|i> = (|0> + i|1>)/sqrt(2)", np.pi / 2, np.pi / 2),
        ("theta = pi/4 (generic superposition)", np.pi / 4, 0.0),
        ("theta = 2*pi/3 (generic superposition)", 2 * np.pi / 3, 0.0),
    ]

    header = f"{'State':40s}{'Fidelity':>12s}{'Entangled?':>14s}"
    print(header)
    print("-" * len(header))
    for label, theta, phi in cases:
        fid = cloning_fidelity(theta, phi)
        ent = is_entangled(theta, phi)
        print(f"{label:40s}{fid:12.6f}{str(ent):>14s}")

    print()
    print("Basis states |0> and |1> come out with fidelity = 1.000000 and no")
    print("entanglement -- CNOT really does copy them, because they're the")
    print("classical-reversible inputs it was built for.")
    print()
    print("Every genuine superposition comes out with fidelity < 1 AND")
    print("entangled with the source qubit: the circuit did not produce two")
    print("independent copies of |psi>. It produced one shared, correlated")
    print("two-qubit state instead. That gap is the no-cloning theorem,")
    print("made concrete: no unitary can copy an unknown quantum state.")


if __name__ == "__main__":
    main()
