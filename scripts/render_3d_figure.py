"""Render static 3D PNGs of the chip topologies (matplotlib mplot3d).

Saves results/figures/topologies_3d.png: one 3D subplot per headline
topology with the worst-case Bell-pair route highlighted. Used for the
team's own deck-making (the repo ships no deck).
"""

import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services import topology_service

OUT = os.path.join("results", "figures", "topologies_3d.png")
HEADLINE = ["t-shape", "heavy-hex-21", "hyperbolic-20"]
TITLES = {
    "t-shape": "T-shape (flat, 5q)",
    "heavy-hex-21": "Heavy-hex 21q (flat)",
    "hyperbolic-20": "Hyperbolic {7,3} 20q (curved)",
}


def main():
    fig = plt.figure(figsize=(15, 5))
    for i, name in enumerate(HEADLINE):
        d = topology_service.topology_detail(name)
        pos = np.array(d["positions3d"])
        ax = fig.add_subplot(1, 3, i + 1, projection="3d")
        # couplers
        for a, b in d["edges"]:
            xs = [pos[a][0], pos[b][0]]
            ys = [pos[a][1], pos[b][1]]
            zs = [pos[a][2], pos[b][2]]
            ax.plot(xs, ys, zs, color="#9aa4b2", linewidth=0.6, alpha=0.7)
        # qubits
        ax.scatter(pos[:, 0], pos[:, 1], pos[:, 2], s=18, c="#1f6feb",
                   depthshade=True, zorder=3)
        # worst-case route
        route = d["route"]
        rp = pos[route]
        ax.plot(rp[:, 0], rp[:, 1], rp[:, 2], color="#f0b429", linewidth=3,
                zorder=4)
        ax.scatter(rp[[0, -1], 0], rp[[0, -1], 1], rp[[0, -1], 2],
                   s=80, c="#f0b429", edgecolors="black", zorder=5)
        for q in (route[0], route[-1]):
            ax.text(pos[q][0], pos[q][1], pos[q][2], f"q{q}", fontsize=9)
        ax.set_title(f"{TITLES[name]}\n{d['diameter']} hops, "
                     f"q{route[0]}→q{route[-1]}", fontsize=11)
        ax.set_box_aspect((1, 1, 0.7))
        ax.view_init(elev=22, azim=-60)
    fig.suptitle("T-shape reference, size-matched heavy-hex reference, and proposed {7,3} hyperbolic patch\n"
                 "same worst-case Bell pair (heavy-hex-21 is a supplementary visual reference, not the required 127-qubit row)",
                 fontsize=12, y=0.98)
    fig.tight_layout()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    fig.savefig(OUT, dpi=150)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
