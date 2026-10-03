import React from "react";
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { CSS2DRenderer, CSS2DObject } from "three/addons/renderers/CSS2DRenderer.js";

/**
 * 3D cost surface: two translucent surfaces (geometry A vs B) showing
 * estimated cloud cost over fixed-overhead-per-shot (x) and shots (z,
 * log scale). Height is log10(cost). The surfaces visibly converge as
 * fixed overhead dominates — the model's honest punchline.
 *
 * Props: depthA, depthB (two-qubit depths), labelA, labelB, price ($/QPU-s),
 * tLayer (µs per two-qubit layer). Rebuilds when any prop changes.
 */
const SEG = 40;
const OVH_MAX = 2000; // µs
const LOG_SHOTS_MIN = 3;
const LOG_SHOTS_MAX = 7;

function fmtMoney(p) {
  if (p < 0) return `$10^${p}`;
  if (p < 3) return "$" + "1" + "0".repeat(p);
  const k = ["$1k", "$10k", "$100k", "$1M", "$10M", "$100M", "$1B"];
  return k[p - 3] || `$10^${p}`;
}

function costOf(shots, ovh, depth, tLayer, price) {
  return (shots * (depth * tLayer + ovh) * price) / 1e6;
}

export default function CostSurface3D({ depthA, depthB, labelA, labelB, price, tLayer }) {
  const mountRef = React.useRef(null);

  React.useEffect(() => {
    const mount = mountRef.current;
    if (!mount || depthA == null || depthB == null) return;
    const reducedMotion =
      window.matchMedia?.("(prefers-reduced-motion: reduce)").matches ?? false;

    const W = mount.clientWidth || 640;
    const H = mount.clientHeight || 420;
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(W, H);
    mount.appendChild(renderer.domElement);

    const labelRenderer = new CSS2DRenderer();
    labelRenderer.setSize(W, H);
    Object.assign(labelRenderer.domElement.style, {
      position: "absolute", top: "0", left: "0", pointerEvents: "none",
    });
    mount.appendChild(labelRenderer.domElement);

    const scene = new THREE.Scene();
    scene.background = new THREE.Color("#0d1117");
    const camera = new THREE.PerspectiveCamera(45, W / H, 0.1, 500);
    camera.position.set(11, 8.5, 13);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.target.set(0, 2, 0);
    controls.autoRotate = !reducedMotion;
    controls.autoRotateSpeed = 0.9;
    let userGrabbed = false;
    controls.addEventListener("start", () => { userGrabbed = true; });

    scene.add(new THREE.AmbientLight(0xffffff, 0.75));
    const dir = new THREE.DirectionalLight(0xffffff, 1.1);
    dir.position.set(6, 12, 8);
    scene.add(dir);

    // Height normalization across both surfaces.
    let minL = Infinity, maxL = -Infinity;
    for (let i = 0; i <= SEG; i++) {
      const ovh = (i / SEG) * OVH_MAX;
      for (let j = 0; j <= SEG; j++) {
        const shots = 10 ** (LOG_SHOTS_MIN + (j / SEG) * (LOG_SHOTS_MAX - LOG_SHOTS_MIN));
        for (const d of [depthA, depthB]) {
          const c = costOf(shots, ovh, d, tLayer, price);
          if (c > 0) {
            const l = Math.log10(c);
            if (l < minL) minL = l;
            if (l > maxL) maxL = l;
          }
        }
      }
    }
    if (!isFinite(minL)) { minL = 0; maxL = 1; }
    if (maxL - minL < 0.5) maxL = minL + 0.5;

    const xOf = (ovh) => (ovh / OVH_MAX) * 10 - 5;
    const zOf = (logShots) => ((logShots - LOG_SHOTS_MIN) / (LOG_SHOTS_MAX - LOG_SHOTS_MIN)) * 10 - 5;
    const yOf = (logCost) => ((logCost - minL) / (maxL - minL)) * 5;

    const disposables = [];
    function buildSurface(depth, color) {
      const geo = new THREE.PlaneGeometry(10, 10, SEG, SEG);
      geo.rotateX(-Math.PI / 2);
      const pos = geo.attributes.position;
      for (let k = 0; k < pos.count; k++) {
        const x = pos.getX(k); // -5..5 -> overhead
        const z = pos.getZ(k); // -5..5 -> log shots
        const ovh = ((x + 5) / 10) * OVH_MAX;
        const logShots = LOG_SHOTS_MIN + ((z + 5) / 10) * (LOG_SHOTS_MAX - LOG_SHOTS_MIN);
        const shots = 10 ** logShots;
        const c = costOf(shots, ovh, depth, tLayer, price);
        pos.setY(k, yOf(Math.log10(Math.max(c, 1e-9))));
      }
      geo.computeVertexNormals();
      const mat = new THREE.MeshStandardMaterial({
        color, transparent: true, opacity: 0.72,
        side: THREE.DoubleSide, roughness: 0.55, metalness: 0.1,
      });
      const mesh = new THREE.Mesh(geo, mat);
      disposables.push(geo, mat);
      return mesh;
    }
    scene.add(buildSurface(depthA, 0x0e7c8c));
    scene.add(buildSurface(depthB, 0xa85f1d));

    // Floor grid + axis frame.
    const grid = new THREE.GridHelper(10, 10, 0x232b36, 0x1a2230);
    grid.position.y = -0.01;
    scene.add(grid);
    disposables.push(grid.geometry, grid.material);

    function tag(text, x, y, z, big = false) {
      const el = document.createElement("div");
      el.textContent = text;
      Object.assign(el.style, {
        fontFamily: "ui-monospace, monospace",
        fontSize: big ? "15px" : "12px",
        fontWeight: big ? "700" : "400",
        color: "#e6edf3",
        background: "rgba(13,17,23,0.85)",
        padding: big ? "4px 10px" : "2px 7px",
        borderRadius: "4px",
        whiteSpace: "nowrap",
      });
      const o = new CSS2DObject(el);
      o.position.set(x, y, z);
      scene.add(o);
      return o;
    }
    const tags = [];
    // X ticks: fixed overhead µs
    for (const ovh of [0, 500, 1000, 1500, 2000]) {
      tags.push(tag(`${ovh}`, xOf(ovh), -0.35, 5.7));
    }
    tags.push(tag("fixed overhead per shot (µs)", 0, -0.35, 6.6, true));
    // Z ticks: shots (log)
    for (let p = LOG_SHOTS_MIN; p <= LOG_SHOTS_MAX; p++) {
      tags.push(tag(`10^${p}`, 5.7, -0.35, zOf(p)));
    }
    tags.push(tag("shots (log scale)", 6.9, -0.35, 0, true));
    // Y ticks: cost (log $)
    for (let p = Math.ceil(minL); p <= Math.floor(maxL); p++) {
      tags.push(tag(fmtMoney(p), -5.7, yOf(p), -5.4));
    }
    tags.push(tag("cost $ (log scale)", -6.6, 2.5, -5.4, true));

    // Resize.
    const ro = new ResizeObserver(() => {
      const w = mount.clientWidth || 640;
      const h = mount.clientHeight || 420;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
      labelRenderer.setSize(w, h);
    });
    ro.observe(mount);

    let raf = 0;
    const animate = () => {
      raf = requestAnimationFrame(animate);
      controls.autoRotate = !reducedMotion && !userGrabbed;
      controls.update();
      renderer.render(scene, camera);
      labelRenderer.render(scene, camera);
    };
    animate();

    return () => {
      cancelAnimationFrame(raf);
      ro.disconnect();
      controls.dispose();
      scene.traverse((o) => { if (o.isCSS2DObject) o.element.remove(); });
      disposables.forEach((d) => d.dispose?.());
      labelRenderer.domElement.remove();
      renderer.domElement.remove();
      renderer.dispose();
      mount.replaceChildren();
    };
  }, [depthA, depthB, labelA, labelB, price, tLayer]);

  return (
    <div style={{ position: "relative" }}>
      <div
        ref={mountRef}
        style={{ position: "relative", width: "100%", minHeight: 430, borderRadius: 8, overflow: "hidden" }}
        role="img"
        aria-label={`3D cost surfaces for ${labelA} versus ${labelB}`}
      />
      <div style={{ display: "flex", gap: 18, marginTop: 10, flexWrap: "wrap" }}>
        <span className="mono small">
          <span style={{ display: "inline-block", width: 14, height: 14, background: "#0e7c8c", marginRight: 8, verticalAlign: -2, borderRadius: 3 }} />
          {labelA} (depth {depthA})
        </span>
        <span className="mono small">
          <span style={{ display: "inline-block", width: 14, height: 14, background: "#a85f1d", marginRight: 8, verticalAlign: -2, borderRadius: 3 }} />
          {labelB} (depth {depthB})
        </span>
        <span className="muted small">drag to rotate · scroll to zoom</span>
      </div>
    </div>
  );
}
