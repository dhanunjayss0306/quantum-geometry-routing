"""Hyperbolic topology -- a genuine finite patch of the {7,3} tessellation.

Construction (Poincare disk, reflection group): place a regular heptagon with
interior angle 2*pi/3 in the Poincare disk (circumradius found by bisection),
then grow the patch by reflecting heptagons across their edges -- reflections
in circles orthogonal to the unit disk. Vertices computed via different
reflection paths coincide (up to floating-point error) and are identified by
rounding; the tiling's own symmetry guarantees this is exact.

In the {7,3} tiling, heptagons meet three-to-a-vertex. Invariants, checked by
tests/test_topologies.py:
  * every face is a 7-cycle,
  * every vertex has degree <= 3 (degree 3 = interior),
  * every edge belongs to <= 2 faces, every vertex to <= 3 faces,
  * the patch is connected.

Why hyperbolic: volume grows exponentially with radius, so a {7,3} patch
packs many qubits at a small graph diameter -- short trips need few SWAPs.
Nobody has built this in hardware; that is why we simulate it.
"""

import cmath
import math
from collections import deque

from .topology_base import TopologyBase

_ROUND = 9  # decimals for vertex identification


def _reflect_factory(a: complex, b: complex):
    """Return z -> reflection of z across the geodesic through a and b.

    The geodesic is a circle orthogonal to the unit circle: |c|^2 = 1 + rho^2
    with |a-c| = |b-c| = rho. Reflection = inversion in that circle.
    """
    ar, ai = a.real, a.imag
    br, bi = b.real, b.imag
    rhs1 = (ar * ar + ai * ai + 1) / 2
    rhs2 = (br * br + bi * bi + 1) / 2
    det = ar * bi - ai * br
    if abs(det) < 1e-14:
        # a, b, origin collinear: geodesic is a diameter; reflect across the
        # line through the origin in direction (a+b).
        ang = cmath.phase(a + b)
        rot = cmath.exp(-1j * ang)
        return lambda z: cmath.exp(1j * ang) * (rot * z).conjugate()
    x = (rhs1 * bi - ai * rhs2) / det
    y = (ar * rhs2 - rhs1 * br) / det
    c = complex(x, y)
    rho2 = x * x + y * y - 1.0

    def reflect(z: complex) -> complex:
        w = z - c
        return c + rho2 / w.conjugate()

    return reflect


def _interior_angle(r: float) -> float:
    """Interior angle of a regular heptagon of circumradius r in the disk.

    The model is conformal, so the hyperbolic angle equals the Euclidean
    angle between the circle tangents at the vertex.
    """
    v0 = complex(r, 0.0)
    d = (r * r + 1) / (2 * r * math.cos(math.pi / 7))  # |circle center|
    out = []
    for sgn in (1, -1):
        c = d * cmath.exp(sgn * 1j * math.pi / 7)
        t = 1j * (v0 - c)  # tangent to the circle at v0
        if (t.real * (-v0.real) + t.imag * (-v0.imag)) < 0:
            t = -t  # point into the heptagon (toward the origin)
        out.append(t / abs(t))
    dot = max(-1.0, min(1.0, (out[0].real * out[1].real
                              + out[0].imag * out[1].imag)))
    return math.acos(dot)


def _heptagon_radius() -> float:
    """Circumradius giving interior angle exactly 2*pi/3 (bisection)."""
    target = 2 * math.pi / 3
    lo, hi = 1e-9, 1.0 - 1e-12
    # angle decreases monotonically from 5*pi/7 (r->0) to 0 (r->1)
    for _ in range(200):
        mid = (lo + hi) / 2
        if _interior_angle(mid) > target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def _grow_73(target_qubits: int):
    """Grow a {7,3} patch by edge reflections. Returns (n, edges, faces)."""
    r = _heptagon_radius()
    start = [r * cmath.exp(2j * math.pi * k / 7) for k in range(7)]

    def vkey(z: complex):
        return (round(z.real, _ROUND), round(z.imag, _ROUND))

    vert_id = {}
    heptagons = []      # 7-tuples of vertex indices (for faces/tests)
    seen = set()        # frozensets of indices

    def add_heptagon(vlist) -> bool:
        idx = []
        for z in vlist:
            k = vkey(z)
            if k not in vert_id:
                vert_id[k] = len(vert_id)
            idx.append(vert_id[k])
        fs = frozenset(idx)
        if fs in seen or len(set(idx)) != 7:
            return False
        seen.add(fs)
        heptagons.append(tuple(idx))
        return True

    add_heptagon(start)
    queue = deque([start])
    done = len(vert_id) >= target_qubits
    while queue and not done:
        h = queue.popleft()
        for k in range(7):
            a, b = h[k], h[(k + 1) % 7]
            refl = _reflect_factory(a, b)
            h2 = tuple(refl(z) for z in h)
            if add_heptagon(h2):
                queue.append(h2)
                if len(vert_id) >= target_qubits:
                    done = True
                    break

    n = len(vert_id)
    edges = set()
    for f in heptagons:
        for a, b in zip(f, f[1:] + f[:1]):
            edges.add(tuple(sorted((a, b))))
    return n, [tuple(e) for e in edges], heptagons


class HyperbolicTiling(TopologyBase):
    """Finite {7,3} patch with ~target_qubits qubits. Name carries the count."""

    def __init__(self, target_qubits: int = 22):
        n, edges, faces = _grow_73(target_qubits)
        self._num_qubits = n
        self._edges = edges
        self._faces = faces

    @property
    def name(self) -> str:
        return f"hyperbolic-{self._num_qubits}"

    @property
    def description(self) -> str:
        return (f"{self._num_qubits}-qubit finite patch of the hyperbolic "
                f"{{7,3}} tessellation (heptagons, 3 per vertex).")

    def num_qubits(self) -> int:
        return self._num_qubits

    def edges(self) -> list:
        return self._edges

    def faces(self) -> list:
        """The heptagonal faces as 7-tuples (for tests)."""
        return self._faces


# Backwards-compatible alias.
HyperbolicTopology = HyperbolicTiling
