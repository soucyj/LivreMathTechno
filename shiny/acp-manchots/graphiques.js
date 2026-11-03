// Dessin des deux graphiques avec Plotly.
//
// Le plan de projection est le plan de l'écran : on lit en continu la
// caméra du graphique 3D (direction du regard n, vecteur « haut »), on en
// déduit une base orthonormée (e1, e2) du plan, et l'on dessine à droite
// les coordonnées des ombres des points dans cette base. Le plan est aussi
// envoyé au serveur Shiny (input.plan), qui calcule la variance conservée.
(function () {
  const D = window.ACP_DONNEES;
  const COUL = ["#CD3333", "#36648B", "rgb(196,142,58)"];
  const GRIS = "#9aa3ad";
  const SYMB3D = ["circle", "diamond", "square"];
  const SYMB2D = ["circle", "triangle-up", "square"];
  const C_VP = "#2E8B57", C_PLAN = "rgb(28,63,110)";
  const L_VP = 2.6;     // longueur dessinée des vecteurs propres (unitaires)
  const BORNE = 3.6;    // étendue des axes, en cotes z
  const CAMERA_DEPART = {
    eye: { x: 1.55, y: -1.45, z: 0.85 }, up: { x: 0, y: 0, z: 1 },
    center: { x: 0, y: 0, z: 0 }, projection: { type: "orthographic" }
  };
  const CONFIG = { responsive: true, displaylogo: false,
                   modeBarButtonsToRemove: ["toImage", "resetCameraLastSave3d"] };

  const groupes = [0, 1, 2].map(s => D.espece.map((e, i) => (e === s ? i : -1)).filter(i => i >= 0));
  const fois = (w, t) => w.map(c => c * t);
  const plus = (u, w) => u.map((c, k) => c + w[k]);
  const dot = (u, w) => u[0] * w[0] + u[1] * w[1] + u[2] * w[2];
  const croix = (u, w) => [u[1] * w[2] - u[2] * w[1], u[2] * w[0] - u[0] * w[2], u[0] * w[1] - u[1] * w[0]];
  const norme = w => Math.hypot(...w);
  const unit = w => fois(w, 1 / norme(w));
  const vec = o => [o.x, o.y, o.z];

  let opts = { lie: true, vp: false, couleurs: true };
  let plan = null;           // {e1, e2, n}
  let dessine = false;

  // ── Plan de l'écran à partir de la caméra ───────────────────────
  function planDeCamera(cam) {
    const n = unit(plus(vec(cam.eye), fois(vec(cam.center || { x: 0, y: 0, z: 0 }), -1)));
    let h = vec(cam.up);
    let w = plus(h, fois(n, -dot(h, n)));
    if (norme(w) < 1e-6) w = croix(n, Math.abs(n[0]) < 0.9 ? [1, 0, 0] : [0, 1, 0]);
    const e2 = unit(w);
    const e1 = croix(e2, n);   // horizontale de l'écran
    return { e1, e2, n };
  }

  function cameraCourante() {
    const gd = document.getElementById("graphe3d");
    const sc = gd && gd._fullLayout && gd._fullLayout.scene;
    if (!sc) return null;
    // Pendant un glissement, seule la scène WebGL connaît la caméra à jour.
    if (sc._scene && sc._scene.getCamera) return sc._scene.getCamera();
    return sc.camera;
  }

  // ── Graphique 3D ────────────────────────────────────────────────
  function traces3D() {
    const t = [];
    groupes.forEach((idx, s) => t.push({
      type: "scatter3d", mode: "markers", name: D.nomsEspeces[s],
      x: idx.map(i => D.z[i][0]), y: idx.map(i => D.z[i][1]), z: idx.map(i => D.z[i][2]),
      text: idx.map(i => D.info[i]), hovertemplate: "%{text}<extra></extra>",
      marker: { size: 3.3, symbol: SYMB3D[s], color: opts.couleurs ? COUL[s] : GRIS,
                opacity: 0.9, line: { width: 0 } },
      showlegend: opts.couleurs
    }));
    // Le plan figé (seulement quand il ne suit pas le regard)
    const p = plan || planDeCamera(CAMERA_DEPART);
    const c = BORNE * 0.95;
    const coin = (s1, s2) => plus(fois(p.e1, s1 * c), fois(p.e2, s2 * c));
    const q = [[coin(-1, -1), coin(-1, 1)], [coin(1, -1), coin(1, 1)]];
    t.push({
      type: "surface", x: q.map(r => r.map(v => v[0])), y: q.map(r => r.map(v => v[1])),
      z: q.map(r => r.map(v => v[2])), surfacecolor: [[0, 0], [0, 0]],
      colorscale: [[0, C_PLAN], [1, C_PLAN]], showscale: false, opacity: 0.18,
      hoverinfo: "skip", visible: !opts.lie, name: "plan",
      lighting: { ambient: 1, diffuse: 0, specular: 0 }
    });
    // Les vecteurs propres
    D.vp.forEach((v, k) => {
      const bout = fois(v, L_VP * 0.9), etiq = fois(v, L_VP * 1.13);
      t.push({
        type: "scatter3d", mode: "lines+text", showlegend: false, hoverinfo: "skip",
        x: [0, bout[0], null, etiq[0]], y: [0, bout[1], null, etiq[1]], z: [0, bout[2], null, etiq[2]],
        line: { width: 6, color: C_VP }, text: ["", "", "", "<b>v" + (k + 1) + "</b>"],
        textfont: { size: 16, color: C_VP }, visible: opts.vp
      });
    });
    t.push({
      type: "cone", x: D.vp.map(v => v[0] * L_VP), y: D.vp.map(v => v[1] * L_VP),
      z: D.vp.map(v => v[2] * L_VP), u: D.vp.map(v => v[0]), v: D.vp.map(v => v[1]),
      w: D.vp.map(v => v[2]), anchor: "tip", sizemode: "absolute", sizeref: 0.4,
      colorscale: [[0, C_VP], [1, C_VP]], showscale: false, hoverinfo: "skip",
      visible: opts.vp
    });
    return t;
  }

  function axe3D(titre) {
    return { title: { text: titre, font: { size: 12 } }, range: [-BORNE, BORNE],
             zeroline: true, zerolinecolor: "#b8bec7", gridcolor: "#e6e9ee",
             backgroundcolor: "#fbfcfd", showbackground: true, tickfont: { size: 10 } };
  }

  function layout3D() {
    const cam = dessine ? cameraCourante() : null;
    const camera = cam ? JSON.parse(JSON.stringify(cam)) : JSON.parse(JSON.stringify(CAMERA_DEPART));
    camera.projection = { type: "orthographic" };
    return {
      margin: { l: 0, r: 0, t: 0, b: 0 }, uirevision: "fixe", paper_bgcolor: "white",
      legend: { x: 0.01, y: 0.99, bgcolor: "rgba(255,255,255,0.75)", font: { size: 12 } },
      scene: {
        uirevision: "fixe", aspectmode: "cube", dragmode: "orbit", camera: camera,
        xaxis: axe3D(D.nomsAxes[0]), yaxis: axe3D(D.nomsAxes[1]), zaxis: axe3D(D.nomsAxes[2])
      }
    };
  }

  function dessiner3D() {
    Plotly.react("graphe3d", traces3D(), layout3D(), CONFIG);
    dessine = true;
  }

  // ── Graphique 2D (l'ombre sur le plan) ──────────────────────────
  function dessiner2D() {
    const p = plan;
    const traces = groupes.map((idx, s) => ({
      type: "scattergl", mode: "markers", name: D.nomsEspeces[s],
      x: idx.map(i => dot(D.z[i], p.e1)), y: idx.map(i => dot(D.z[i], p.e2)),
      text: idx.map(i => D.info[i]), hovertemplate: "%{text}<extra></extra>",
      marker: { size: 7, symbol: SYMB2D[s], color: opts.couleurs ? COUL[s] : GRIS,
                opacity: 0.8, line: { width: 0.6, color: "white" } },
      showlegend: opts.couleurs
    }));
    const annotations = [];
    if (opts.vp) {
      D.vp.forEach((v, k) => {
        const x = L_VP * dot(v, p.e1), y = L_VP * dot(v, p.e2), r = Math.hypot(x, y);
        if (r > 0.12) annotations.push({
          x, y, ax: 0, ay: 0, xref: "x", yref: "y", axref: "x", ayref: "y", text: "",
          showarrow: true, arrowhead: 2, arrowsize: 1, arrowwidth: 2.5, arrowcolor: C_VP });
        const d = r > 0.12 ? 0.32 / r : 0;
        annotations.push({ x: x + d * x, y: y + d * y + (r > 0.12 ? 0 : 0.25), xref: "x", yref: "y",
          showarrow: false, text: "<b>v" + (k + 1) + "</b>", font: { size: 15, color: C_VP } });
      });
    }
    const axe = titre => ({ title: { text: titre, font: { size: 12 } },
                            range: [-BORNE - 0.6, BORNE + 0.6], zeroline: true,
                            zerolinecolor: "#b8bec7", gridcolor: "#eef0f3", tickfont: { size: 10 } });
    const layout = {
      margin: { l: 48, r: 10, t: 6, b: 44 }, uirevision: "fixe", paper_bgcolor: "white",
      plot_bgcolor: "#fbfcfd", hovermode: "closest",
      legend: { x: 0.01, y: 0.99, bgcolor: "rgba(255,255,255,0.75)", font: { size: 12 } },
      xaxis: axe("horizontale du plan"),
      yaxis: Object.assign(axe("verticale du plan"), { scaleanchor: "x", scaleratio: 1 }),
      annotations
    };
    Plotly.react("graphe2d", traces, layout, CONFIG);
  }

  // ── Envoi du plan au serveur (au plus toutes les 120 ms) ────────
  let dernierEnvoi = 0, envoiPrevu = null;
  function envoyerPlan() {
    const maintenant = performance.now();
    const go = () => {
      dernierEnvoi = performance.now(); envoiPrevu = null;
      Shiny.setInputValue("plan", { e1: plan.e1, e2: plan.e2, n: plan.n });
    };
    if (maintenant - dernierEnvoi > 120) go();
    else if (!envoiPrevu) envoiPrevu = setTimeout(go, 130);
  }

  function changerPlan(p) {
    plan = p;
    dessiner2D();
    envoyerPlan();
  }

  // ── Le plan suit le regard : on surveille la caméra ─────────────
  let derniereCle = "";
  const cleCamera = cam => [cam.eye.x, cam.eye.y, cam.eye.z, cam.up.x, cam.up.y, cam.up.z]
    .map(c => c.toFixed(4)).join();
  function surveiller() {
    if (dessine && opts.lie) {
      const cam = cameraCourante();
      if (cam) {
        const cle = cleCamera(cam);
        if (cle !== derniereCle) {
          derniereCle = cle;
          changerPlan(planDeCamera(cam));
        }
      }
    }
    requestAnimationFrame(surveiller);
  }

  // ── Animation douce de la caméra ────────────────────────────────
  let anim = null;
  function allerVers(cible, fin) {
    const gd = document.getElementById("graphe3d");
    const cam = cameraCourante();
    if (!cam) return;
    const e0 = vec(cam.eye), u0 = vec(cam.up), e1 = vec(cible.eye), u1 = vec(cible.up);
    const r0 = norme(e0), r1 = norme(e1), d0 = unit(e0), d1 = unit(e1);
    const sauter = dot(d0, d1) < -0.9;
    const debut = performance.now(), duree = 900;
    if (anim) cancelAnimationFrame(anim);
    function pas(maintenant) {
      const t = sauter ? 1 : Math.min(1, (maintenant - debut) / duree);
      const s = t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
      const e = fois(unit(plus(fois(d0, 1 - s), fois(d1, s))), r0 + (r1 - r0) * s);
      let u = plus(fois(u0, 1 - s), fois(u1, s));
      u = norme(u) < 1e-6 ? u1 : unit(u);
      Plotly.relayout(gd, { "scene.camera": {
        eye: { x: e[0], y: e[1], z: e[2] }, up: { x: u[0], y: u[1], z: u[2] },
        center: { x: 0, y: 0, z: 0 }, projection: { type: "orthographic" } } });
      if (t < 1) anim = requestAnimationFrame(pas);
      else if (fin) fin();
    }
    anim = requestAnimationFrame(pas);
  }

  // ── Messages du serveur ─────────────────────────────────────────
  Shiny.addCustomMessageHandler("acp_options", function (m) {
    const relie = m.lie && !opts.lie;
    opts = m;
    if (!plan) plan = planDeCamera(CAMERA_DEPART);
    if (relie) { const cam = cameraCourante(); if (cam) plan = planDeCamera(cam); derniereCle = ""; }
    dessiner3D();
    changerPlan(plan);
  });

  // Se placer face à un plan (raccourcis, « Se placer face au plan »)
  Shiny.addCustomMessageHandler("acp_aller", function (m) {
    const cible = { eye: { x: 2.1 * m.n[0], y: 2.1 * m.n[1], z: 2.1 * m.n[2] },
                    up: { x: m.e2[0], y: m.e2[1], z: m.e2[2] } };
    const exact = { e1: m.e1, e2: m.e2, n: m.n };
    if (!opts.lie) { changerPlan(exact); dessiner3D(); }
    // À l'arrivée, on fixe le plan exact (sans arrondi de la caméra).
    allerVers(cible, () => { if (opts.lie) { derniereCle = cleCamera(cameraCourante()); changerPlan(exact); } });
  });

  Shiny.addCustomMessageHandler("acp_depart", function (m) { allerVers(CAMERA_DEPART); });

  requestAnimationFrame(surveiller);
})();
