import React from "react";
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { CSS2DRenderer, CSS2DObject } from "three/addons/renderers/CSS2DRenderer.js";

/**
 * 3D coupling-graph viewer. Props:
 *   topology  - full TopologyInfo from /api/topologies (positions3d, route, ...)
 *   normalize - scale every chip to the same bounding size (Compare mode)
 *   autoRotate - slow turntable until the user grabs the scene
 *
 * Ref exposes exportPNG(filename).
 */
const Topology3D = React.forwardRef(function Topology3D(
  { topology, normalize = false, autoRotate = true },
  ref
) {
  const mountRef = React.useRef(null);
  const apiRef = React.useRef({});
  const autoRotateRef = React.useRef(autoRotate);
  autoRotateRef.current = autoRotate;

  React.useEffect(() => {
    const mount = mountRef.current;
    if (!mount || !topology) return;
    const reducedMotion =
      window.matchMedia?.("(prefers-reduced-motion: reduce)").matches ?? false;

    const css = getComputedStyle(document.documentElement);
    const cssVar = (name, fallback) =>
      css.getPropertyValue(name).trim() || fallback;
    const C = {
      bg: cssVar("--canvas-bg", "#0d1117"),
      qubit: new THREE.Color(cssVar("--qubit", "#1f6feb")),
      qubitHi: new THREE.Color(cssVar("--accent", "#f0b429")),
      edge: new THREE.Color(cssVar("--edge", "#3a4552")),
      route: new THREE.Color(cssVar("--accent", "#f0b429")),
      pulse: new THREE.Color(cssVar("--pulse", "#ffffff")),
      grid: new THREE.Color(cssVar("--grid", "#232b36")),
      surface: new THREE.Color(cssVar("--surface", "#1f6feb")),
      label: cssVar("--label-bg", "rgba(13,17,23,0.85)"),
      labelText: cssVar("--label-text", "#ffffff"),
    };

    // Our (x, y, z) -> three.js (x, z, y) so "height" is up.
    let pts = topology.positions3d.map(
      (p) => new THREE.Vector3(p[0], p[2], p[1])
    );
    let normFactor = 1;
    if (normalize) {
      const r = Math.max(...pts.map((p) => p.length()), 1e-9);
      normFactor = 1 / r;
      pts = pts.map((p) => p.clone().multiplyScalar(normFactor));
    }
    const posOf = (n) => pts[n];

    const W = mount.clientWidth || 600;
    const H = mount.clientHeight || 360;
    const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
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
    scene.background = new THREE.Color(C.bg);
    const camera = new THREE.PerspectiveCamera(45, W / H, 0.01, 1000);

    // Frame the chip.
    const sphere = new THREE.Sphere();
    pts.forEach((p) => sphere.expandByPoint(p));
    const fitDist = Math.max(sphere.radius, 0.5) / Math.sin(THREE.MathUtils.degToRad(22.5));
    const dir = new THREE.Vector3(0.9, 0.65, 1).normalize();
    camera.position.copy(sphere.center).addScaledVector(dir, fitDist * 1.25);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.08;
    controls.autoRotate = autoRotateRef.current && !reducedMotion;
    controls.autoRotateSpeed = 0.9;

    scene.add(new THREE.AmbientLight(0xffffff, 0.9));
    const key = new THREE.DirectionalLight(0xffffff, 1.4);
    key.position.set(3, 5, 2);
    scene.add(key);

    const disposables = [];
    const track = (o) => (disposables.push(o), o);

    // Qubits (instanced spheres).
    const N = topology.num_qubits;
    const routeSet = new Set(topology.route);
    const qGeo = track(new THREE.SphereGeometry(0.045, 18, 18));
    const qMat = track(new THREE.MeshStandardMaterial({ roughness: 0.35, metalness: 0.1 }));
    const qubits = track(new THREE.InstancedMesh(qGeo, qMat, N));
    const m4 = new THREE.Matrix4();
    pts.forEach((p, i) => {
      m4.makeTranslation(p.x, p.y, p.z);
      qubits.setMatrixAt(i, m4);
      qubits.setColorAt(i, routeSet.has(i) ? C.qubitHi : C.qubit);
    });
    qubits.instanceMatrix.needsUpdate = true;
    if (qubits.instanceColor) qubits.instanceColor.needsUpdate = true;
    scene.add(qubits);

    // Couplers.
    const edgePos = new Float32Array(topology.edges.length * 6);
    topology.edges.forEach(([a, b], i) => {
      const pa = posOf(a), pb = posOf(b);
      edgePos.set([pa.x, pa.y, pa.z, pb.x, pb.y, pb.z], i * 6);
    });
    const eGeo = track(new THREE.BufferGeometry());
    eGeo.setAttribute("position", new THREE.BufferAttribute(edgePos, 3));
    const edges = track(new THREE.LineSegments(
      eGeo, track(new THREE.LineBasicMaterial({ color: C.edge, transparent: true, opacity: 0.85 }))
    ));
    scene.add(edges);

    // Worst-case Bell-pair route as a thick tube.
    const routePts = topology.route.map(posOf);
    const curve = new THREE.CatmullRomCurve3(routePts);
    const tube = track(new THREE.Mesh(
      track(new THREE.TubeGeometry(curve, 64, 0.022, 10, false)),
      track(new THREE.MeshStandardMaterial({
        color: C.route, roughness: 0.3, emissive: C.route, emissiveIntensity: 0.35,
      }))
    ));
    scene.add(tube);

    // Bell-pair endpoints: bigger spheres + labels.
    const [qa, qb] = topology.bell_pair;
    const endGeo = track(new THREE.SphereGeometry(0.085, 20, 20));
    const endMat = track(new THREE.MeshStandardMaterial({
      color: C.route, roughness: 0.25, emissive: C.route, emissiveIntensity: 0.5,
    }));
    [qa, qb].forEach((q) => {
      const s = track(new THREE.Mesh(endGeo, endMat));
      s.position.copy(posOf(q));
      const div = document.createElement("div");
      div.className = "q3d-label";
      div.textContent = `q${q}`;
      div.style.background = C.label;
      div.style.color = C.labelText;
      const label = new CSS2DObject(div);
      label.position.set(0, 0.16, 0);
      s.add(label);
      scene.add(s);
    });

    // Travelling pulse: the Bell pair being routed.
    let pulse = null;
    if (!reducedMotion) {
      pulse = track(new THREE.Mesh(
        track(new THREE.SphereGeometry(0.05, 14, 14)),
        track(new THREE.MeshBasicMaterial({ color: C.pulse }))
      ));
      scene.add(pulse);
    }

    // Supporting surface.
    if (topology.surface.type === "hyperboloid") {
      const { k, u_max } = topology.surface;
      void k; // nodes already carry the lift; surface uses u directly
      const profile = [];
      const STEPS = 40;
      for (let i = 0; i <= STEPS; i++) {
        const u = (i / STEPS) * u_max;
        profile.push(new THREE.Vector2(Math.sinh(u), 1 - Math.cosh(u)));
      }
      // Match the normalized scale when comparing.
      const surfGeo = track(new THREE.LatheGeometry(profile, 48));
      surfGeo.scale(normFactor, normFactor, normFactor);
      const surf = track(new THREE.Mesh(
        surfGeo,
        track(new THREE.MeshBasicMaterial({
          color: C.surface, wireframe: true, transparent: true, opacity: 0.28,
        }))
      ));
      scene.add(surf);
    } else {
      const size = Math.max(sphere.radius * 2.4, 1);
      const grid = track(new THREE.GridHelper(size, 12, C.grid, C.grid));
      grid.material.transparent = true;
      grid.material.opacity = 0.5;
      grid.position.y = -0.002;
      scene.add(grid);
    }

    // Resize with the container.
    const ro = new ResizeObserver(() => {
      const w = mount.clientWidth || 600;
      const h = mount.clientHeight || 360;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
      labelRenderer.setSize(w, h);
    });
    ro.observe(mount);

    // Render loop.
    let raf = 0;
    const clock = new THREE.Clock();
    const animate = () => {
      raf = requestAnimationFrame(animate);
      controls.autoRotate = autoRotateRef.current && !reducedMotion && !userGrabbed;
      if (pulse) {
        const t = (clock.getElapsedTime() * 0.25) % 1;
        pulse.position.copy(curve.getPointAt(t));
      }
      controls.update();
      renderer.render(scene, camera);
      labelRenderer.render(scene, camera);
    };
    let userGrabbed = false;
    controls.addEventListener("start", () => { userGrabbed = true; });
    animate();

    apiRef.current.exportPNG = (filename = "topology-3d.png") => {
      renderer.render(scene, camera);
      const a = document.createElement("a");
      a.href = renderer.domElement.toDataURL("image/png");
      a.download = filename;
      a.click();
    };

    return () => {
      cancelAnimationFrame(raf);
      ro.disconnect();
      controls.dispose();
      scene.traverse((o) => {
        if (o.isCSS2DObject) o.element.remove();
      });
      disposables.forEach((d) => d.dispose?.());
      labelRenderer.domElement.remove();
      renderer.domElement.remove();
      renderer.dispose();
      mount.replaceChildren();
    };
  }, [topology, normalize]);

  React.useImperativeHandle(ref, () => ({
    exportPNG: (f) => apiRef.current.exportPNG?.(f),
  }));

  return (
    <div
      ref={mountRef}
      className="topo3d"
      style={{ position: "relative", width: "100%", minHeight: 340, borderRadius: 8, overflow: "hidden" }}
      role="img"
      aria-label={`3D view of the ${topology?.name} coupling graph`}
      tabIndex={0}
    />
  );
});

export default Topology3D;
