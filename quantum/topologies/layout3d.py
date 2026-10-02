"""3D layouts for the topology viewer. Pure functions, networkx + numpy only.

Each topology gets an (N, 3) coordinate list:
  - star / T-shape: hand-placed on the z=0 plane.
  - heavy-hex patches: real honeycomb coordinates ('pos' from
    networkx.hexagonal_lattice_graph); subdivision (edge) qubits sit at the
    midpoint of their two corner qubits. Centred and scaled, z=0.
  - Eagle-127: deterministic Kamada-Kawai 2D layout, z=0.
  - hyperbolic {7,3}: Kamada-Kawai 2D centred on the most central node,
    lifted onto the hyperboloid model. With r = k*|p| and angle theta:
        x = sinh(r)*cos(theta), y = sinh(r)*sin(theta), z = -(cosh(r)-1)
    k is chosen so the outermost node lands at u ~ 2.1. Points satisfy
    x^2 + y^2 - (z-1)^2 = -1 (hyperboloid shifted so its tip is at origin).

All layouts are deterministic (fixed seeds) and rounded to 3 decimals.
"""

import math

import networkx as nx
import numpy as np

_SEED = 42
_U_MAX = 2.1  # hyperboloid parameter of the outermost node


def _finish(pos2d, z=0.0):
    """Centre, scale to unit max radius, add z, round."""
    pts = np.array([pos2d[i] for i in range(len(pos2d))], dtype=float)
    pts -= pts.mean(axis=0)
    r = np.abs(pts).max()
    if r > 0:
        pts /= r
    out = [[round(float(x), 3), round(float(y), 3), round(z, 3)]
           for x, y in pts]
    return out


def _star_positions():
    # hub at origin, leaves along the axes
    return [[0, 0, 0], [1, 0, 0], [0, 1, 0], [-1, 0, 0], [0, -1, 0]]


def _tshape_positions():
    #   3
    #   |
    # 0-1-2   (4 hangs off 3)
    #   |
    #   4  -> laid flat: 1 at origin
    return [[-1, 0, 0], [0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 2, 0]]


def _heavy_hex_positions(topology):
    """Real honeycomb coordinates; edge qubits at midpoints."""
    rows, cols = topology._rows, topology._cols
    honey = nx.hexagonal_lattice_graph(rows, cols)
    index = {node: i for i, node in enumerate(honey.nodes())}
    pos = {}
    for node, i in index.items():
        px, py = honey.nodes[node]["pos"]
        pos[i] = (float(px), float(py))
    nxt = len(index)
    # Mirror _heavy_hex_edges exactly (same iteration order -> same ids).
    for u, v in honey.edges():
        w = nxt
        nxt += 1
        iu, iv = index[u], index[v]
        pos[w] = ((pos[iu][0] + pos[iv][0]) / 2,
                  (pos[iu][1] + pos[iv][1]) / 2)
    return _finish(pos)


def _kamada_2d(graph):
    # kamada_kawai_layout has no seed; start from the deterministic circular
    # layout so the result is reproducible.
    init = nx.circular_layout(graph)
    pos = nx.kamada_kawai_layout(graph, pos=init)
    return {int(n): (float(p[0]), float(p[1])) for n, p in pos.items()}


def _hyperbolic_positions(topology):
    g = topology.graph()
    pos = _kamada_2d(g)
    # most central node = min eccentricity
    ecc = nx.eccentricity(g)
    center = min(ecc, key=ecc.get)
    cx, cy = pos[center]
    pts = {}
    for n, (x, y) in pos.items():
        pts[n] = (x - cx, y - cy)
    rhos = {n: math.hypot(x, y) for n, (x, y) in pts.items()}
    max_rho = max(rhos.values())
    k = _U_MAX / max_rho if max_rho > 0 else 1.0
    out = []
    for n in range(len(pts)):
        x, y = pts[n]
        rho, theta = math.hypot(x, y), math.atan2(y, x)
        r = k * rho
        out.append([round(math.sinh(r) * math.cos(theta), 3),
                    round(math.sinh(r) * math.sin(theta), 3),
                    round(-(math.cosh(r) - 1), 3)])
    return out, {"type": "hyperboloid", "k": round(k, 6), "u_max": _U_MAX}


def layout_3d(topology) -> dict:
    """3D layout for a topology.

    Returns {"positions": [[x,y,z], ...], "surface": {...}, "family": ...}
    where surface is {"type": "plane", "z": 0} or
    {"type": "hyperboloid", "k": k, "u_max": 2.1},
    and family is "flat" | "hyperbolic".
    """
    from .heavy_hex import HeavyHexPatch, Eagle127Topology
    from .hyperbolic import HyperbolicTiling

    name = topology.name
    if name == "star":
        return {"positions": _star_positions(),
                "surface": {"type": "plane", "z": 0}, "family": "flat"}
    if name == "t-shape":
        return {"positions": _tshape_positions(),
                "surface": {"type": "plane", "z": 0}, "family": "flat"}
    if isinstance(topology, HyperbolicTiling):
        positions, surface = _hyperbolic_positions(topology)
        return {"positions": positions, "surface": surface,
                "family": "hyperbolic"}
    if isinstance(topology, HeavyHexPatch):
        return {"positions": _heavy_hex_positions(topology),
                "surface": {"type": "plane", "z": 0}, "family": "flat"}
    if isinstance(topology, Eagle127Topology):
        return {"positions": _finish(_kamada_2d(topology.graph())),
                "surface": {"type": "plane", "z": 0}, "family": "flat"}
    # fallback: deterministic Kamada-Kawai, flat
    return {"positions": _finish(_kamada_2d(topology.graph())),
            "surface": {"type": "plane", "z": 0}, "family": "flat"}
