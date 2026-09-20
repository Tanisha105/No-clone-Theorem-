

A small, tested Qiskit project that makes the quantum no-cloning theorem
concrete: it builds the simplest possible "cloning machine," shows exactly
where and why it fails, and contrasts that failure with quantum
teleportation — the theorem-respecting way to move quantum information
from one place to another.

![Cloning fidelity vs. input state](assets/fidelity_vs_theta.png)

## The theorem, in plain terms

**No-cloning theorem:** there is no unitary operation `U` that takes an
*arbitrary, unknown* quantum state `|ψ⟩` and a blank qubit `|0⟩` and produces
two independent copies of `|ψ⟩`:

```
U ( |ψ⟩ ⊗ |0⟩ )  ≠  |ψ⟩ ⊗ |ψ⟩      for a general, unknown |ψ⟩
```

It's a precise, provable statement, not an engineering limitation waiting
on better hardware — quantum mechanics itself forbids it.

**Why it has to be true (the one-line proof):** quantum evolution is
*linear*. Suppose some unitary `U` could clone two particular states
`|a⟩` and `|b⟩`, i.e. `U(|a⟩|0⟩) = |a⟩|a⟩` and `U(|b⟩|0⟩) = |b⟩|b⟩`. Now
feed it their superposition `|ψ⟩ = (|a⟩ + |b⟩)/√2`. Linearity forces:

```
U(|ψ⟩|0⟩) = (|a⟩|a⟩ + |b⟩|b⟩) / √2
```

But a genuine clone of `|ψ⟩` would be:

```
|ψ⟩ ⊗ |ψ⟩ = (|a⟩|a⟩ + |a⟩|b⟩ + |b⟩|a⟩ + |b⟩|b⟩) / 2
```

These two are not the same state — the cross terms `|a⟩|b⟩` and `|b⟩|a⟩`
are missing. So the same `U` cannot clone both `|a⟩`, `|b⟩` *and* every
superposition of them. The only way out is for `|a⟩` and `|b⟩` to be
orthogonal and *fixed in advance* (a known basis) — which is exactly why a
classical bit can be copied (0 and 1 are fixed and orthogonal) but an
unknown qubit cannot.

This project doesn't just state that proof — it runs it.

## What the code actually shows

`src/no_cloning_demo.py` builds the most natural first guess for a cloning
circuit: a single **CNOT gate**, with the state to be cloned on the control
qubit and a blank `|0⟩` on the target. A CNOT is exactly the reversible
"copy" operation classical computing already relies on, so it's the
obvious candidate.

The script prepares `|ψ⟩ = cos(θ/2)|0⟩ + e^(iφ) sin(θ/2)|1⟩` for a range of
`θ`, runs the CNOT, and checks the target qubit against two independent
criteria for "did cloning actually happen":

1. **Fidelity** — how close is the target qubit's state to `|ψ⟩`?
2. **Entanglement** — is the target qubit still an independent, standalone
   state, or is it now entangled with the source?

```
State                                       Fidelity    Entangled?
---------------------------------------------------------------------------
|0>                                         1.000000         False
|1>                                         1.000000         False
|+> = (|0> + |1>)/sqrt(2)                   0.500000          True
|i> = (|0> + i|1>)/sqrt(2)                  0.500000          True
theta = pi/4 (generic superposition)        0.750000          True
theta = 2*pi/3 (generic superposition)      0.625000          True
```

Reading the table the way the theorem predicts: the two computational
basis states, `|0⟩` and `|1⟩`, come out perfectly (fidelity 1, no
entanglement) — CNOT really is a valid copier *for that fixed, known,
orthogonal pair*. Every genuine superposition comes out both imperfect
*and* entangled with the source qubit. That entanglement is the tell: the
circuit didn't produce a second, independent `|ψ⟩` sitting on its own
qubit — it produced one correlated two-qubit state. There's only ever one
copy of the information, shared between two qubits, never two.

The worst case, `|+⟩ = (|0⟩+|1⟩)/√2`, lands at exactly fidelity 0.5 — no
better than a random guess between `|0⟩` and `|1⟩`. `assets/generate_plot.py`
sweeps `θ` continuously to produce the plot above.

`src/teleportation_demo.py` then shows what quantum mechanics *does*
allow: moving `|ψ⟩` from Alice to Bob using a shared entangled pair, a
Bell-basis measurement, and two classical bits (the standard teleportation
protocol). Averaged over random states, Bob recovers `|ψ⟩` with fidelity
1.0 — but only after Alice's own qubit has been irreversibly measured and
destroyed in the process. At no instant do two copies of `|ψ⟩` exist
simultaneously, so teleportation transports quantum information without
ever violating no-cloning.

## Why this matters

- **Quantum key distribution (BB84 and friends):** an eavesdropper cannot
  copy the qubits in transit to inspect them without disturbing the
  original, which is what makes intercept-and-resend attacks detectable.
- **Quantum error correction:** you cannot fix noise by simply duplicating
  a qubit's state the way classical error correction duplicates bits;
  entire different strategies (encoding into entangled multi-qubit states)
  had to be invented instead.
- **Quantum networking:** teleportation and entanglement swapping — the
  building blocks of long-distance quantum links, e.g. city-scale fiber
  demonstrations like Bersin et al., *Phys. Rev. Applied* 21 (2024)
  (MIT → Lincoln Laboratory) and satellite-based approaches such as Li,
  Yang, et al. (2025) — exist precisely *because* cloning isn't an option;
  moving quantum information requires consuming entanglement and a
  classical channel instead of just copying it down the line.

## Repository structure

```
no-cloning-theorem/
├── src/
│   ├── no_cloning_demo.py      # the CNOT "cloner": fidelity + entanglement checks
│   └── teleportation_demo.py   # the lawful alternative: transport without copying
├── tests/
│   └── test_no_cloning.py      # pytest suite verifying every claim above
├── assets/
│   ├── generate_plot.py        # regenerates fidelity_vs_theta.png
│   └── fidelity_vs_theta.png
├── requirements.txt
├── LICENSE
└── README.md
```

## Getting started

```bash
git clone https://github.com/Tanisha105/no-cloning-theorem.git
cd no-cloning-theorem
pip install -r requirements.txt

python src/no_cloning_demo.py
python src/teleportation_demo.py

pytest -v
```

All 18 tests pass, checking: perfect cloning of basis states, failed
cloning (fidelity < 1, entanglement present) across several superposition
angles, agreement between the simulator and a closed-form analytic
fidelity formula, the exact worst-case fidelity of 0.5 at the equatorial
state, and perfect-fidelity teleportation of five random unknown states.

## References

- W. K. Wootters and W. H. Zurek, "A Single Quantum Cannot Be Cloned,"
  *Nature* 299, 802–803 (1982).
- D. Dieks, "Communication by EPR devices," *Physics Letters A* 92,
  271–272 (1982).
- C. H. Bennett, G. Brassard, C. Crépeau, R. Jozsa, A. Peres, and
  W. K. Wootters, "Teleporting an Unknown Quantum State via Dual
  Classical and Einstein-Podolsky-Rosen Channels," *Phys. Rev. Lett.* 70,
  1895 (1993).
- E. Bersin et al., *Phys. Rev. Applied* 21 (2024) — city-scale quantum
  networking over deployed fiber (MIT ↔ Lincoln Laboratory).
- Li, Yang, et al. (2025) — satellite-based quantum communication links.

## License

MIT — see [LICENSE](LICENSE).
