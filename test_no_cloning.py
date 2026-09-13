"""
Automated checks for the claims made in src/no_cloning_demo.py and
src/teleportation_demo.py.

Run with:
    pytest -v
"""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from no_cloning_demo import analytic_fidelity, cloning_fidelity, is_entangled  # noqa: E402
from teleportation_demo import run_teleportation  # noqa: E402
from qiskit.quantum_info import random_statevector, state_fidelity  # noqa: E402


BASIS_STATES = [0.0, np.pi]  # |0> and |1>
SUPERPOSITIONS = [np.pi / 2, np.pi / 4, 2 * np.pi / 3, np.pi / 6]


@pytest.mark.parametrize("theta", BASIS_STATES)
def test_basis_states_are_cloned_perfectly(theta):
    """CNOT should reproduce |0> and |1> with fidelity 1 and no entanglement."""
    assert cloning_fidelity(theta) == pytest.approx(1.0, abs=1e-9)
    assert is_entangled(theta) is False


@pytest.mark.parametrize("theta", SUPERPOSITIONS)
def test_superpositions_cannot_be_cloned(theta):
    """
    Any genuine superposition must come out with fidelity strictly less
    than 1, and the two qubits must end up entangled -- direct evidence
    that no independent second copy was produced.
    """
    fid = cloning_fidelity(theta)
    assert fid < 1.0 - 1e-9
    assert is_entangled(theta) is True


@pytest.mark.parametrize("theta", BASIS_STATES + SUPERPOSITIONS)
def test_simulated_fidelity_matches_closed_form(theta):
    """Cross-check the Qiskit simulation against the hand-derived formula."""
    assert cloning_fidelity(theta) == pytest.approx(analytic_fidelity(theta), abs=1e-9)


def test_equatorial_state_hits_the_known_worst_case():
    """
    |+> = (|0>+|1>)/sqrt(2) is the standard worst case quoted for a naive
    CNOT 'cloner': fidelity should land at exactly 0.5 (Qiskit's squared-
    overlap convention), i.e. no better than a random guess between the
    two basis states.
    """
    assert cloning_fidelity(np.pi / 2) == pytest.approx(0.5, abs=1e-9)


@pytest.mark.parametrize("seed", [1, 2, 3, 4, 5])
def test_teleportation_transports_arbitrary_states_perfectly(seed):
    """
    Unlike cloning, teleportation must recover ANY random unknown state
    with fidelity 1 -- it moves information rather than copying it.
    """
    psi = random_statevector(2, seed=seed)
    rho_bob = run_teleportation(psi)
    assert state_fidelity(rho_bob, psi) == pytest.approx(1.0, abs=1e-6)
