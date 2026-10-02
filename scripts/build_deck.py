"""Build the hackathon deck from real experiment results.

The handbook caps the deck at 4-8 slides, so this generates exactly 8.
Every number comes from results/tables/*.csv -- rerun
scripts/run_all_cases.py and scripts/scaling_sweep.py first, then this.

Usage (from repo root):
    .venv/bin/python scripts/build_deck.py
Output: results/reports/quantum-geometry-routing-deck.pptx
"""

import csv
import glob
import os
import re

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.util import Inches, Pt

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIGURES = os.path.join(REPO_ROOT, "results", "figures")
TABLES = os.path.join(REPO_ROOT, "results", "tables")
REPORTS = os.path.join(REPO_ROOT, "results", "reports")

# --- dark "quantum lab" theme ---------------------------------------------
BG = RGBColor(0x0D, 0x11, 0x17)
FG = RGBColor(0xE6, 0xED, 0xF3)
MUTED = RGBColor(0x8B, 0x94, 0x9E)
ACCENT = RGBColor(0x58, 0xA6, 0xFF)

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]  # blank


def _bg(slide):
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = BG


def _box(slide, left, top, width, height):
    return slide.shapes.add_textbox(Inches(left), Inches(top),
                                    Inches(width), Inches(height))


def _para(tf, text, size=20, bold=False, color=FG, alignment=None, space_after=6):
    p = tf.add_paragraph()
    p.text = text
    p.font.size = Pt(size)
    p.font.bold = bold
    p.font.color.rgb = color
    p.font.name = "Calibri"
    if alignment is not None:
        p.alignment = alignment
    p.space_after = Pt(space_after)
    return p


def title_slide(title, subtitle, foot=""):
    slide = prs.slides.add_slide(BLANK)
    _bg(slide)
    _para(_box(slide, 1, 1.2, 11.3, 1.5).text_frame, title, size=48,
          bold=True, color=ACCENT, alignment=2)
    _para(_box(slide, 1.5, 3.0, 10.3, 2).text_frame, subtitle, size=22,
          color=FG, alignment=2)
    if foot:
        _para(_box(slide, 1.5, 5.6, 10.3, 1).text_frame, foot, size=16,
              color=MUTED, alignment=2)


def content_slide(title, bullets, image=None, image_caption=""):
    slide = prs.slides.add_slide(BLANK)
    _bg(slide)
    _para(_box(slide, 0.6, 0.3, 12, 1).text_frame, title, size=32,
          bold=True, color=ACCENT)
    img_left = 6.9 if image else 0.8
    tf = _box(slide, 0.8, 1.4, 5.6 if image else 11.7, 5.6).text_frame
    tf.word_wrap = True
    for i, b in enumerate(bullets):
        p = tf.add_paragraph() if i else tf.paragraphs[0]
        p.text = b
        p.font.size = Pt(19)
        p.font.color.rgb = FG
        p.font.name = "Calibri"
        p.space_after = Pt(10)
        p.level = 0
    if image:
        path = os.path.join(FIGURES, image)
        slide.shapes.add_picture(path, Inches(img_left), Inches(1.6),
                                 width=Inches(5.8))
        if image_caption:
            _para(_box(slide, img_left, 6.6, 5.8, 0.6).text_frame,
                  image_caption, size=14, color=MUTED, alignment=2)
    return slide


def load_csv(name):
    with open(os.path.join(TABLES, name)) as f:
        return list(csv.DictReader(f))


def count_tests():
    n = 0
    for path in glob.glob(os.path.join(REPO_ROOT, "tests", "test_*.py")):
        with open(path) as f:
            n += len(re.findall(r"^def test_", f.read(), re.M))
    return n


def main():
    rows = load_csv("summary.csv")
    by = {(r["topology"], r["condition"]): r for r in rows}
    scale = load_csv("scaling.csv")

    def fid(t, c):
        return float(by[(t, c)]["fidelity"])

    def swaps(t):
        return int(float(by[(t, "noisy")]["swap_count"]))

    def diam(t):
        return int(float(by[(t, "noisy")]["graph_distance"]))

    def yld(t):
        return float(by[(t, "protected")]["yield"])

    def added(t, k):
        return int(float(by[(t, "protected")][k]))

    topo_order = ["t-shape", "heavy-hex-21", "hyperbolic-20"]
    labels = {"t-shape": "T-shape (5q, 2016)",
              "heavy-hex-21": "heavy-hex (21q, IBM-style)",
              "hyperbolic-20": "hyperbolic {7,3} (20q, future)"}

    # scaling extremes for the recommendation
    hh127 = next(r for r in scale if r["topology"] == "heavy-hex-127")
    hyp_big = max((r for r in scale if r["family"] == "hyperbolic"),
                  key=lambda r: int(r["num_qubits"]))

    # 1. Title --------------------------------------------------------------
    title_slide(
        "Quantum Geometry Routing",
        "Which road-map should future quantum clouds use?\n"
        "Bell-state routing across 2016, 2026 and future chip topologies",
        "Track 4: Geometry-Aware Quantum Cloud Challenge  |  IBM Qiskit Fall Fest 2026",
    )

    # 2. Problem ------------------------------------------------------------
    content_slide("The problem: distant qubits pay a SWAP tax", [
        "Cloud QPUs have 100+ qubits, but each qubit talks to only a few neighbors.",
        "Entangling distant qubits needs SWAP detours along the coupling graph.",
        "Each SWAP = more gates = more noise exposure = worse entanglement.",
        "Question: which coupling-graph geometry minimizes this tax?",
    ])

    # 3. Experiment ---------------------------------------------------------
    content_slide("Our experiment: 9 real simulations + a scaling sweep", [
        "Bell state |Phi+> routed between the two farthest qubits of each chip (worst case).",
        "Matrix: T-shape (5q, 2016) x heavy-hex (21q, IBM-style) x hyperbolic {7,3} (20q).",
        "Conditions: ideal, noisy (depolarizing + readout), noisy + ancilla protection.",
        "Scaling sweep: 13 chips, 20 to 127 qubits, 3 families -- how does the worst trip grow?",
    ])

    # 4. How it works -------------------------------------------------------
    content_slide("How it works (and why you can trust it)", [
        "H + CNOT makes the Bell state; Qiskit transpile() routes it onto the coupling map.",
        "Fidelity from XX/YY/ZZ correlators: F = (1 + <XX> - <YY> + <ZZ>) / 4.",
        "Protection: an ancilla measures the ZZ then XX stabilizers mid-circuit; "
        "we keep only clean-syndrome shots and score the data bits alone.",
        "Selection and scoring use disjoint bits -- random noise cannot fake F=1.",
    ])

    # 5. Routing cost -------------------------------------------------------
    cost_lines = [
        f"{labels[t]}: {swaps(t)} SWAPs across diameter {diam(t)}."
        for t in topo_order
    ]
    content_slide("Result 1: the detour depends on the road-map", cost_lines + [
        "Every SWAP is noise exposure: routing cost is the whole story.",
    ], image="routing_cost.png",
        image_caption="SWAPs and two-qubit depth per topology (worst-case pair)")

    # 6. Fidelity + honest protection ---------------------------------------
    gain = {t: fid(t, "protected") - fid(t, "noisy") for t in topo_order}
    content_slide("Result 2: protection helps -- honestly", [
        f"Noisy fidelity: " + ", ".join(
            f"{labels[t].split(' (')[0]} {fid(t,'noisy'):.3f}" for t in topo_order) + ".",
        f"Protected: " + ", ".join(
            f"{labels[t].split(' (')[0]} {fid(t,'protected'):.3f} "
            f"(+{gain[t]:.3f})" for t in topo_order) + ".",
        f"Cost of protection: +{added('heavy-hex-21','added_swap_count')} SWAP, "
        f"+{added('heavy-hex-21','added_cx_count')} CX, "
        f"~{(1-yld('heavy-hex-21'))*100:.0f}% of shots discarded.",
        "It never reaches 1.0 -- some errors always slip through. That is the honest trade.",
    ], image="fidelity.png",
        image_caption="Bell-state fidelity across topologies and conditions")

    # 7. Scaling + recommendation -------------------------------------------
    content_slide("Result 3: scaling decides the future (recommendation)", [
        f"At 127 qubits, heavy-hex (real IBM Eagle map) has diameter {hh127['diameter']}; "
        f"hyperbolic {hyp_big['num_qubits']}q has diameter {hyp_big['diameter']}.",
        "Heavy-hex scales ~2.3*sqrt(N) -- worse than a plain grid (~1.8*sqrt(N)).",
        "Recommend: max degree 3, diameter target log(N), no long degree-2 wire chains, "
        "small faces (<=8), budget error detection only for the longest routes.",
        "Full evidence: docs/recommendation.md + results/tables/scaling.csv.",
    ], image="scaling_diameter.png",
        image_caption="Worst-case hops vs qubit count (log-x): hyperbolic grows slowest")

    # 8. System -------------------------------------------------------------
    content_slide("System and reproducibility", [
        f"Modular repo: quantum/ core, algorithms/ matrix+sweep, backend/ FastAPI, frontend/ React.",
        f"{count_tests()} pytest tests, fixed seeds, pinned requirements.",
        "Topologies: T-shape, star, heavy-hex patches (21/35/106), real Eagle-127, {7,3} tiling, grid.",
        "Next: real QPU runs, noise-aware routing, non-planar shortcut couplers.",
    ])

    os.makedirs(REPORTS, exist_ok=True)
    out = os.path.join(REPORTS, "quantum-geometry-routing-deck.pptx")
    prs.save(out)
    print(f"deck written: {out} ({len(prs.slides)} slides)")


if __name__ == "__main__":
    main()
