"""
Generates assets/fidelity_vs_theta.png for the README: cloning fidelity
(and entanglement) as a function of the input state's Bloch angle theta,
for the naive CNOT "cloner" defined in src/no_cloning_demo.py.

Run from the repo root:
    python assets/generate_plot.py
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from no_cloning_demo import cloning_fidelity  # noqa: E402

thetas = np.linspace(0, 2 * np.pi, 400)
fidelities = [cloning_fidelity(t) for t in thetas]

fig, ax = plt.subplots(figsize=(7, 4.5))
ax.plot(thetas, fidelities, color="#5B4FE9", linewidth=2.5)
ax.axhline(1.0, color="#999999", linestyle="--", linewidth=1, label="perfect clone (F = 1)")
ax.axvline(0, color="#cccccc", linewidth=1)
ax.axvline(np.pi, color="#cccccc", linewidth=1)
ax.annotate(
    "|0>, |1>\n(basis states: F = 1)",
    xy=(np.pi, 1.0),
    xytext=(np.pi + 0.35, 0.85),
    fontsize=9,
    ha="left",
)
ax.annotate(
    "|+> (equatorial superposition)\nworst case: F = 0.5",
    xy=(np.pi / 2, 0.5),
    xytext=(0.25, 0.62),
    fontsize=9,
    ha="left",
    arrowprops=dict(arrowstyle="->", color="#555555", lw=1),
)

ax.set_xlabel(r"$\theta$  (Bloch angle of input state $|\psi\rangle$)")
ax.set_ylabel("Cloning fidelity F")
ax.set_title("Naive CNOT \"cloner\": fidelity vs. input state")
ax.set_xticks([0, np.pi / 2, np.pi, 3 * np.pi / 2, 2 * np.pi])
ax.set_xticklabels(["0", "π/2", "π", "3π/2", "2π"])
ax.set_ylim(0.4, 1.05)
ax.legend(loc="lower center", frameon=False)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
fig.tight_layout()

out_path = Path(__file__).resolve().parent / "fidelity_vs_theta.png"
fig.savefig(out_path, dpi=160)
print(f"Saved {out_path}")
