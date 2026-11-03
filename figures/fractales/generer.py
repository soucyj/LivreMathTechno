# ═══════════════════════════════════════════════════════════════════════
#  Générateur des figures TikZ du chapitre 3 (fractales et SIF).
#
#  Chaque figure « lourde » (itérées d'un SIF, nuages de points du jeu du
#  chaos, graphes très irréguliers) est calculée ici et écrite sous forme
#  de commandes TikZ brutes dans un fichier .tikz, que le chapitre insère
#  avec \input à l'intérieur d'un environnement tikzpicture. Les fichiers
#  ne contiennent que des chemins : l'échelle, les axes et les étiquettes
#  restent dans Livre.tex.
#
#  Styles attendus (définis dans le préambule de Livre.tex) :
#    fractale  : remplissage des pièces d'un ensemble
#    nuage     : remplissage des points du jeu du chaos
#    courbe    : tracé des courbes (von Koch, Weierstrass, Mandelbrot)
#
#  Utilisation :  python3 generer.py      (depuis ce dossier)
# ═══════════════════════════════════════════════════════════════════════
import math
import os
import random

import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__))


# ── Outils ───────────────────────────────────────────────────────────────
def affine(a, b, c, d, e, f):
    """Application affine (x,y) -> (ax+by+e, cx+dy+f), stockée (A, t)."""
    return (np.array([[a, b], [c, d]], dtype=float), np.array([e, f], dtype=float))


def homothetie(k, e=0.0, f=0.0):
    return affine(k, 0, 0, k, e, f)


def similitude(k, theta_deg, e=0.0, f=0.0):
    t = math.radians(theta_deg)
    return affine(k * math.cos(t), -k * math.sin(t), k * math.sin(t), k * math.cos(t), e, f)


def applique(w, pts):
    A, t = w
    return pts @ A.T + t


def iteree(sif, polygones, n):
    """W^n appliqué à une liste de polygones (tableaux m x 2)."""
    for _ in range(n):
        polygones = [applique(w, p) for w in sif for p in polygones]
    return polygones


def fmt(x, chiffres=4):
    s = f"{x:.{chiffres}f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def chemin_polygones(polygones, style="fractale", par_ligne=4, par_commande=400):
    lignes = []
    for i in range(0, len(polygones), par_commande):
        bloc = polygones[i:i + par_commande]
        morceaux = []
        for p in bloc:
            morceaux.append(" -- ".join(f"({fmt(x)},{fmt(y)})" for x, y in p) + " -- cycle")
        corps = "\n  ".join(" ".join(morceaux[j:j + par_ligne])
                            for j in range(0, len(morceaux), par_ligne))
        lignes.append(f"\\fill[{style}]\n  {corps};")
    return "\n".join(lignes) + "\n"


def chemin_polyligne(points, style="courbe", par_ligne=6):
    coords = [f"({fmt(x)},{fmt(y)})" for x, y in points]
    corps = "\n  ".join(" -- ".join(coords[j:j + par_ligne]) + (" --" if j + par_ligne < len(coords) else "")
                        for j in range(0, len(coords), par_ligne))
    return f"\\draw[{style}]\n  {corps};\n"


def chemin_points(points, cote, style="nuage", par_commande=1500):
    """Chaque point devient un petit carré de côté « cote » (en unités)."""
    lignes = []
    for i in range(0, len(points), par_commande):
        bloc = points[i:i + par_commande]
        morceaux = [f"({fmt(x - cote / 2, 3)},{fmt(y - cote / 2, 3)})rectangle++({fmt(cote)},{fmt(cote)})"
                    for x, y in bloc]
        corps = "\n  ".join(" ".join(morceaux[j:j + 5]) for j in range(0, len(morceaux), 5))
        lignes.append(f"\\fill[{style}]\n  {corps};")
    return "\n".join(lignes) + "\n"


def ecrit(nom, contenu, entete):
    with open(os.path.join(ICI, nom), "w", encoding="utf-8") as fichier:
        fichier.write(f"% {entete}\n% Fichier généré par generer.py : ne pas modifier à la main.\n")
        fichier.write(contenu)
    print(f"{nom:34s} {len(contenu) / 1024:7.1f} Ko")


def jeu_du_chaos(sif, probas, n, graine, depart=(0.0, 0.0), rejet=20, avec_indice=False):
    rng = random.Random(graine)
    p = np.array(depart, dtype=float)
    pts = []
    for i in range(n + rejet):
        j = rng.choices(range(len(sif)), weights=probas)[0]
        p = applique(sif[j], p)
        if i >= rejet:
            pts.append((tuple(p), j) if avec_indice else tuple(p))
    return pts


CARRE = np.array([[0, 0], [1, 0], [1, 1], [0, 1]], dtype=float)
R3 = math.sqrt(3) / 2
TRIANGLE = np.array([[0, 0], [1, 0], [0.5, R3]], dtype=float)
SOMMETS = [(0.0, 0.0), (1.0, 0.0), (0.5, R3)]
MOTIF_F = np.array([(0, 0), (0.3, 0), (0.3, 0.55), (0.6, 0.55), (0.6, 0.75), (0.3, 0.75),
                    (0.3, 0.85), (0.75, 0.85), (0.75, 1), (0, 1)], dtype=float)

# ── Les SIF du chapitre ──────────────────────────────────────────────────
SIERPINSKI = [homothetie(0.5, 0.5 * x, 0.5 * y) for x, y in SOMMETS]   # w_i(P) = (P + S_i)/2
KOCH = [homothetie(1 / 3),
        similitude(1 / 3, 60, 1 / 3, 0),
        similitude(1 / 3, -60, 0.5, math.sqrt(3) / 6),
        homothetie(1 / 3, 2 / 3, 0)]
TAPIS = [homothetie(1 / 3, i / 3, j / 3) for i in range(3) for j in range(3) if (i, j) != (1, 1)]
VICSEK = [homothetie(1 / 3, i / 3, j / 3) for i, j in [(0, 0), (2, 0), (1, 1), (0, 2), (2, 2)]]
FOUGERE = [affine(0, 0, 0, 0.16, 0, 0),
           affine(0.85, 0.04, -0.04, 0.85, 0, 1.6),
           affine(0.2, -0.26, 0.23, 0.22, 0, 1.6),
           affine(-0.15, 0.28, 0.26, 0.24, 0, 0.44)]
FOUGERE_P = [0.01, 0.85, 0.07, 0.07]


def koch_polyligne(n):
    pts = np.array([[0, 0], [1, 0]], dtype=float)
    for _ in range(n):
        morceaux = [applique(w, pts) for w in KOCH]
        pts = np.vstack([morceaux[0]] + [m[1:] for m in morceaux[1:]])
    return pts


def sur_segment(pts, P, Q):
    P, Q = np.array(P, dtype=float), np.array(Q, dtype=float)
    u = Q - P
    v = np.array([-u[1], u[0]])
    return P + np.outer(pts[:, 0], u) + np.outer(pts[:, 1], v)


def flocon_koch(n):
    # Parcours horaire : les « bosses », à gauche du sens de parcours,
    # pointent alors vers l'extérieur du triangle.
    A, B, C = (0, 0), (0.5, R3), (1, 0)
    k = koch_polyligne(n)
    cotes = [sur_segment(k, A, B), sur_segment(k, B, C), sur_segment(k, C, A)]
    return np.vstack([cotes[0]] + [c[1:] for c in cotes[1:]])


# ── Figures du texte ─────────────────────────────────────────────────────
def figures_texte():
    # Courbe de von Koch : étapes 0 à 5.
    for n in range(6):
        ecrit(f"koch-{n}.tikz", chemin_polyligne(koch_polyligne(n)), f"Courbe de von Koch, étape {n}")

    # Les quatre copies w_i(K) de la courbe de von Koch, en couleurs.
    k = koch_polyligne(4)
    ecrit("koch-pieces.tikz",
          "".join(chemin_polyligne(applique(w, k), style=f"trait{i + 1}") for i, w in enumerate(KOCH)),
          "Courbe de von Koch : les quatre copies w_i(K)")

    # Flocon de von Koch : étapes 0 à 4 (contour fermé, rempli).
    for n in range(5):
        pts = flocon_koch(n)[:-1]
        ecrit(f"flocon-koch-{n}.tikz", chemin_polygones([pts]), f"Flocon de von Koch, étape {n}")

    # Triangle de Sierpiński : étapes 0 à 6.
    for n in range(7):
        ecrit(f"sierpinski-{n}.tikz", chemin_polygones(iteree(SIERPINSKI, [TRIANGLE], n)),
              f"Triangle de Sierpiński, étape {n}")

    # Les trois copies w_i(S) du triangle de Sierpiński, en couleurs.
    tri = iteree(SIERPINSKI, [TRIANGLE], 5)
    ecrit("sierpinski-pieces.tikz",
          "".join(chemin_polygones([applique(w, p) for p in tri], style=f"piece{i + 1}")
                  for i, w in enumerate(SIERPINSKI)),
          "Triangle de Sierpiński : les trois copies w_i(S)")

    # Ensemble de Cantor : étapes 0 à 5, une rangée par étape.
    segments = [(0.0, 1.0)]
    rangees = []
    for n in range(6):
        rangees += [np.array([(a, -0.3 * n), (b, -0.3 * n), (b, -0.3 * n + 0.1), (a, -0.3 * n + 0.1)])
                    for a, b in segments]
        segments = [s for a, b in segments for s in ((a, a + (b - a) / 3), (b - (b - a) / 3, b))]
    ecrit("cantor.tikz", chemin_polygones(rangees), "Ensemble de Cantor, étapes 0 à 5")

    # Tapis de Sierpiński : étapes 0 à 4.
    for n in range(5):
        ecrit(f"tapis-{n}.tikz", chemin_polygones(iteree(TAPIS, [CARRE], n)),
              f"Tapis de Sierpiński, étape {n}")

    # Le SIF de Sierpiński appliqué à trois ensembles de départ différents.
    depart = {"carre": [CARRE], "motif": [MOTIF_F],
              "disque": [np.array([(0.5 + 0.45 * math.cos(2 * math.pi * i / 40),
                                    0.45 + 0.45 * math.sin(2 * math.pi * i / 40)) for i in range(40)])]}
    for nom, poly in depart.items():
        for n in (0, 1, 2, 3, 5):
            ecrit(f"hutchinson-{nom}-{n}.tikz", chemin_polygones(iteree(SIERPINSKI, poly, n)),
                  f"W^{n} appliqué au départ « {nom} »")

    # Jeu du chaos : les premiers coups, puis des nuages de tailles croissantes.
    # Suite de sommets fixée à la main (plutôt que tirée au hasard) pour
    # que les six premiers coups se lisent bien sur la figure.
    p = np.array([0.2, 0.75])
    trace = [tuple(p)]
    choix = [0, 1, 1, 2, 0, 2]
    for i in choix:
        p = (p + np.array(SOMMETS[i])) / 2
        trace.append(tuple(p))
    lignes = []
    for k in range(len(trace) - 1):
        (x0, y0), (x1, y1) = trace[k], trace[k + 1]
        sx, sy = SOMMETS[choix[k]]
        lignes.append(f"\\draw[chaosvers] ({fmt(x1)},{fmt(y1)}) -- ({fmt(sx)},{fmt(sy)});")
        lignes.append(f"\\draw[chaospas] ({fmt(x0)},{fmt(y0)}) -- ({fmt(x1)},{fmt(y1)});")
    positions = ["right", "left", "below", "right", "right", "below left", "above right"]
    for k, (x, y) in enumerate(trace):
        lignes.append(f"\\node[ptim, label={{[etiq]{positions[k]}:$P_{{{k}}}$}}] at ({fmt(x)},{fmt(y)}) {{}};")
    ecrit("chaos-premiers-coups.tikz", "\n".join(lignes) + "\n", "Jeu du chaos : six premiers coups")

    for n in (200, 2000, 15000):
        pts = jeu_du_chaos(SIERPINSKI, [1, 1, 1], n, graine=2026, depart=(0.3, 0.2))
        ecrit(f"chaos-sierpinski-{n}.tikz", chemin_points(pts, 0.009 if n > 5000 else 0.014),
              f"Jeu du chaos, {n} points")

    # Fougère de Barnsley.
    pts = jeu_du_chaos(FOUGERE, FOUGERE_P, 20000, graine=1988)
    ecrit("fougere.tikz", chemin_points(pts, 0.04), "Fougère de Barnsley, 20 000 points")

    # La fougère, chaque point coloré selon la dernière application utilisée.
    pieces = jeu_du_chaos(FOUGERE, FOUGERE_P, 20000, graine=1988, avec_indice=True)
    ecrit("fougere-pieces.tikz",
          "".join(chemin_points([p for p, i in pieces if i == j], 0.04, style=f"piece{j + 1}")
                  for j in range(4)),
          "Fougère : les quatre pièces w_i(A)")

    # Trois SIF de trois similitudes : chevauchements (propriété de l'ouvert).
    for nom, r in (("disjoint", 0.48), ("touche", 0.4)):
        if nom == "disjoint":
            sif = [homothetie(0.48), homothetie(0.48, 0.52, 0), homothetie(0.48, 0, 0.52)]
        else:
            sif = [homothetie(0.5), homothetie(r, 0.5, 0), homothetie(0.5, 0, 0.5)]
        probas = [A[0, 0] ** 2 for A, _ in sif]
        pts = jeu_du_chaos(sif, probas, 6000, graine=31)
        ecrit(f"chevauchement-{nom}.tikz", chemin_points(pts, 0.009), f"Chevauchement : {nom}")

    # Arbre fractal (théorème du collage) : un tronc et trois branches.
    arbre = [affine(0.03, 0, 0, 0.42, 0, 0),
             similitude(0.58, 38, 0, 0.42),
             similitude(0.58, -38, 0, 0.42),
             similitude(0.42, 0, 0, 0.6)]
    probas = [0.1, 0.33, 0.33, 0.24]
    pts = jeu_du_chaos(arbre, probas, 10000, graine=12)
    ecrit("arbre.tikz", chemin_points(pts, 0.008), "Arbre fractal")
    # Le même nuage, chaque point coloré selon la dernière application
    # utilisée : on voit les quatre pièces w_i(A) dont l'arbre est fait.
    pieces = jeu_du_chaos(arbre, probas, 10000, graine=12, avec_indice=True)
    ecrit("arbre-pieces.tikz",
          "".join(chemin_points([p for p, i in pieces if i == j], 0.008, style=f"piece{j + 1}")
                  for j in range(4)),
          "Arbre fractal : les quatre pièces w_i(A)")

    # Fonction de Weierstrass W(x) = somme (1/2)^n cos(3^n pi x).
    def weierstrass(x, termes=18):
        return sum(0.5 ** n * math.cos(3 ** n * math.pi * x) for n in range(termes))

    xs = np.linspace(-1, 1, 3001)
    ecrit("weierstrass.tikz", chemin_polyligne([(x, weierstrass(x)) for x in xs]),
          "Fonction de Weierstrass sur [-1,1]")
    xs = np.linspace(0.30, 0.40, 3001)
    ecrit("weierstrass-zoom.tikz", chemin_polyligne([((x - 0.30) * 20 - 1, weierstrass(x)) for x in xs]),
          "Fonction de Weierstrass sur [0,3 ; 0,4], abscisses dilatées d'un facteur 20")
    print("  W(0,30) =", round(weierstrass(0.30), 3), " W(0,40) =", round(weierstrass(0.40), 3),
          " min/max zoom :", round(min(weierstrass(x) for x in xs), 3), round(max(weierstrass(x) for x in xs), 3))

    # « Cartoon » brownien de Mandelbrot : générateur (0,0)-(4/9,2/3)-(5/9,1/3)-(1,1).
    cartoon = [affine(4 / 9, 0, 0, 2 / 3, 0, 0),
               affine(1 / 9, 0, 0, -1 / 3, 4 / 9, 2 / 3),
               affine(4 / 9, 0, 0, 2 / 3, 5 / 9, 1 / 3)]

    def cartoon_polyligne(n, melange=None):
        pts = np.array([[0, 0], [1, 1]], dtype=float)
        rng = random.Random(melange) if melange is not None else None
        for _ in range(n):
            nouveaux = [pts[0]]
            for a, b in zip(pts[:-1], pts[1:]):
                ordre = [0, 1, 2]
                if rng is not None:
                    rng.shuffle(ordre)
                # morceaux (dx, dy) du générateur, éventuellement permutés
                morceaux = [(4 / 9, 2 / 3), (1 / 9, -1 / 3), (4 / 9, 2 / 3)]
                p = a.copy()
                for j in ordre:
                    dx, dy = morceaux[j]
                    p = p + np.array([dx * (b[0] - a[0]), dy * (b[1] - a[1])])
                    nouveaux.append(p.copy())
            pts = np.array(nouveaux)
        return pts

    for n in (1, 2, 7):
        ecrit(f"cartoon-{n}.tikz", chemin_polyligne(cartoon_polyligne(n)), f"Cartoon de Mandelbrot, étape {n}")
    ecrit("cartoon-melange.tikz", chemin_polyligne(cartoon_polyligne(7, melange=5)),
          "Cartoon de Mandelbrot, étape 7, ordre des pièces tiré au hasard")
    # Vérification : la version déterministe est bien l'attracteur du SIF « cartoon ».
    arrondi = lambda tab: {(round(x, 9), round(y, 9)) for x, y in tab}
    images = np.vstack([applique(w, cartoon_polyligne(2)) for w in cartoon])
    assert arrondi(cartoon_polyligne(3)) == arrondi(images)


# ── Figures des exercices ────────────────────────────────────────────────
def figures_exercices():
    # Flocon de von Koch (exercice d'introduction) : étapes 0 à 3.
    # (réutilise flocon-koch-n.tikz)

    # Flocon « carré » (Vicsek) : étapes 0 à 3.
    for n in range(4):
        ecrit(f"vicsek-{n}.tikz", chemin_polygones(iteree(VICSEK, [CARRE], n)), f"Flocon carré, étape {n}")

    # Les six ensembles de l'exercice sur les SIF (attracteurs approchés).
    six = {
        "a": (VICSEK, 4),
        "b": ([homothetie(0.5), homothetie(0.5, 0.5, 0), similitude(0.5, 90, 0.5, 0.5)], 7),
        "c": ([homothetie(0.5), homothetie(0.5, 0.5, 0.5), homothetie(0.25, 0.75, 0),
               homothetie(0.25, 0, 0.75)], 5),
        "d": ([homothetie(0.25, x, y) for x in (0, 0.75) for y in (0, 0.75)], 3),
        "e": ([affine(1 / 3, 0, 0, 0.5, 0, 0), affine(1 / 3, 0, 0, 0.5, 2 / 3, 0),
               affine(1 / 3, 0, 0, 0.5, 1 / 3, 0.5)], 7),
        "f": ([homothetie(0.5), homothetie(1 / 3, 2 / 3, 0), homothetie(1 / 3, 0, 2 / 3),
               homothetie(1 / 3, 2 / 3, 2 / 3)], 5),
    }
    for nom, (sif, n) in six.items():
        ecrit(f"exo-sif-{nom}.tikz", chemin_polygones(iteree(sif, [CARRE], n)), f"Exercice SIF, ensemble ({nom})")

    # L'attracteur de {f1, f2, f3} (pièce tournée et étirée).
    f = [affine(0.5, 0, 0, 0.5, 0, 0), affine(0.5, 0, 0, 0.5, 8, 0), affine(0, -0.8, 5 / 16, 0, 16, 5)]
    rect = np.array([[0, 0], [16, 0], [16, 10], [0, 10]], dtype=float)
    ecrit("exo-f123.tikz", chemin_polygones(iteree(f, [rect], 7)), "Attracteur de {f1, f2, f3}")


if __name__ == "__main__":
    figures_texte()
    figures_exercices()
