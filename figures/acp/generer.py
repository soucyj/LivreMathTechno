# ═══════════════════════════════════════════════════════════════════════
#  Générateur des figures du chapitre 5 (analyse en composantes
#  principales).
#
#  Chaque figure fondée sur des données (nuages de points, éboulis) est
#  calculée ici et écrite sous forme d'un fichier
#  figures/tikz/fig-acp-*.tikz complet (pgfplots), que le pré-rendu
#  convertit en SVG pour le web et que le PDF insère tel quel.
#
#  Données :
#    manchots.csv  : manchots de l'archipel Palmer (Gorman et coll., 2014 ;
#                    paquet R palmerpenguins, licence CC0)
#    decathlon.csv : décathlon, Décastar et Jeux olympiques d'Athènes 2004
#                    (paquet R FactoMineR)
#
#  Utilisation :  python3 generer.py      (depuis n'importe quel dossier)
# ═══════════════════════════════════════════════════════════════════════
import csv
import math
import os

import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__))
TIKZ = os.path.join(ICI, "..", "tikz")


# ── Outils ───────────────────────────────────────────────────────────────
def fmt(x, chiffres=3):
    s = f"{x:.{chiffres}f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def coords(pts, chiffres=3):
    """Liste de points -> « (x,y) (x,y) ... » coupée en lignes."""
    morceaux = ["(" + ",".join(fmt(c, chiffres) for c in p) + ")" for p in pts]
    return "\n      ".join(" ".join(morceaux[i:i + 8]) for i in range(0, len(morceaux), 8))


def ecrire(nom, texte):
    with open(os.path.join(TIKZ, nom + ".tikz"), "w", encoding="utf-8") as f:
        f.write(texte.strip() + "\n")
    print("écrit", nom)


def acp(X, reduire=True):
    """Valeurs propres (décroissantes), vecteurs propres (colonnes) et
    coordonnées des individus, pour un tableau X (une ligne par individu)."""
    Z = X - X.mean(axis=0)
    if reduire:
        Z = Z / X.std(axis=0)
    C = Z.T @ Z / len(Z)
    valeurs, vecteurs = np.linalg.eigh(C)
    ordre = np.argsort(valeurs)[::-1]
    return valeurs[ordre], vecteurs[:, ordre], Z


# Styles des trois espèces : couleur ET forme (lisible en noir et blanc)
ESPECES = [("Adelie", "Adélie", "firebrick3", "*"),
           ("Chinstrap", "à jugulaire", "steelblue4", "triangle*"),
           ("Gentoo", "papou", "coveraccent", "square*")]

STYLE_AXES = r"""
    width=#L#, height=#H#, scale only axis,
    tick label style={font=\scriptsize}, label style={font=\scriptsize},
    title style={font=\small, sectioncolor},
    axis line style={gray!70}, tick style={gray!70},
    grid=major, grid style={gray!18, very thin},"""


def axes(largeur, hauteur):
    return STYLE_AXES.replace("#L#", largeur).replace("#H#", hauteur)


def nuage_especes(pts_par_espece, taille="1.1pt"):
    lignes = []
    for (cle, nom, couleur, marque), pts in zip(ESPECES, pts_par_espece):
        lignes.append(
            f"    \\addplot[only marks, mark={marque}, mark size={taille}, "
            f"color={couleur}, fill opacity=0.65, draw opacity=0.9]\n"
            f"      coordinates {{\n      {coords(pts, 2)}}};")
    return "\n".join(lignes)


LEGENDE_ESPECES = r"""
  \matrix[anchor=north, font=\scriptsize, column sep=3pt] at (#POS#) {
    \node[circle, fill=firebrick3, inner sep=1.4pt] {}; & \node{Adélie}; &
    \node[regular polygon, regular polygon sides=3, fill=steelblue4, inner sep=1.3pt] {}; & \node{à jugulaire}; &
    \node[rectangle, fill=coveraccent, inner sep=1.6pt] {}; & \node{papou};\\
  };"""


def legende(pos):
    return LEGENDE_ESPECES.replace("#POS#", pos)


# ── 1. Les notes de six élèves ───────────────────────────────────────────
NOMS = "ABCDEF"
MATH = np.array([60, 63, 67, 75, 76, 79], float)
SCI = np.array([72, 66, 67, 84, 82, 79], float)
GX, GY = MATH.mean(), SCI.mean()          # (70, 75)


def points_eleves(decal=True):
    l = []
    for n, x, y in zip(NOMS, MATH, SCI):
        pos = {"B": "below right", "C": "below right", "E": "right",
               "F": "below right"}.get(n, "above left")
        l.append(f"    \\node[pt, label={{[etiq]{pos}:${n}$}}] at (axis cs:{fmt(x)},{fmt(y)}) {{}};")
    return "\n".join(l)


def fig_notes():
    ecrire("fig-acp-notes", rf"""
\begin{{tikzpicture}}
  \begin{{axis}}[{axes("5.6cm", "5.6cm")}
    xmin=55, xmax=85, ymin=60, ymax=90,
    xtick={{55,60,...,85}}, ytick={{60,65,...,90}},
    xlabel={{Note en mathématiques}}, ylabel={{Note en sciences}}]
{points_eleves()}
    \draw[gray!60, dashed] (axis cs:70,60) -- (axis cs:70,90);
    \draw[gray!60, dashed] (axis cs:55,75) -- (axis cs:85,75);
    \node[circle, draw=firebrick3, fill=white, thick, inner sep=1.6pt,
      label={{[etiq, firebrick3]below right:$G = (70,75)$}}] at (axis cs:70,75) {{}};
  \end{{axis}}
\end{{tikzpicture}}""")


def fig_residus():
    vert, perp = [], []
    for x, y in zip(MATH, SCI):
        yr = GY + 0.8 * (x - GX)
        vert.append(f"    \\draw[firebrick3, thick] (axis cs:{fmt(x)},{fmt(y)}) -- (axis cs:{fmt(x)},{fmt(yr)});")
        t = ((x - GX) + (y - GY)) / 2
        perp.append(f"    \\draw[firebrick3, thick] (axis cs:{fmt(x)},{fmt(y)}) -- (axis cs:{fmt(GX + t)},{fmt(GY + t)});")
    pts = "\n".join(f"    \\node[pt] at (axis cs:{fmt(x)},{fmt(y)}) {{}};" for x, y in zip(MATH, SCI))
    def panneau(titre, droite, segs, decal):
        return rf"""
  \begin{{axis}}[{axes("5.4cm", "5.4cm")}
    xshift={decal}, title={{{titre}}},
    xmin=55, xmax=85, ymin=60, ymax=90,
    xtick={{55,60,...,85}}, ytick={{60,65,...,90}},
    xlabel={{Mathématiques}}, ylabel={{Sciences}}]
    \addplot[steelblue4, very thick, domain=55:85, samples=2] {{{droite}}};
{chr(10).join(segs)}
{pts}
  \end{{axis}}"""
    ecrire("fig-acp-residus", r"\begin{tikzpicture}" +
           panneau("Écarts verticaux", "75 + 0.8*(x - 70)", vert, "0cm") +
           panneau("Écarts perpendiculaires", "x + 5", perp, "6.9cm") +
           "\n\\end{tikzpicture}")


def fig_angle():
    dx, dy = MATH - GX, SCI - GY
    # à gauche : le nuage centré et ses projections sur deux directions
    proj = []
    for (ang, coul) in [(45, "steelblue4"), (135, "coveraccent")]:
        u = np.array([math.cos(math.radians(ang)), math.sin(math.radians(ang))])
        for a, b in zip(dx, dy):
            t = a * u[0] + b * u[1]
            proj.append(f"    \\draw[{coul}!70, thin, densely dotted] (axis cs:{fmt(a)},{fmt(b)}) -- "
                        f"(axis cs:{fmt(t*u[0])},{fmt(t*u[1])});")
            proj.append(f"    \\node[circle, fill={coul}, inner sep=1pt] at (axis cs:{fmt(t*u[0])},{fmt(t*u[1])}) {{}};")
    pts = "\n".join(f"    \\node[pt] at (axis cs:{fmt(a)},{fmt(b)}) {{}};" for a, b in zip(dx, dy))
    ecrire("fig-acp-angle", rf"""
\begin{{tikzpicture}}
  \begin{{axis}}[{axes("5.2cm", "5.2cm")}
    xmin=-14, xmax=14, ymin=-14, ymax=14,
    xtick={{-10,0,10}}, ytick={{-10,0,10}},
    xlabel={{$x$ (centré)}}, ylabel={{$y$ (centré)}}]
    \addplot[steelblue4, thick, domain=-14:14, samples=2] {{x}};
    \addplot[coveraccent, thick, domain=-14:14, samples=2] {{-x}};
{chr(10).join(proj)}
{pts}
    \node[etiq, steelblue4, anchor=south east] at (axis cs:13,9.5) {{$\theta = 45^\circ$}};
    \node[etiq, coveraccent!85!black, anchor=south west] at (axis cs:-13,9.5) {{$\theta = 135^\circ$}};
  \end{{axis}}
  \begin{{axis}}[{axes("5.6cm", "5.2cm")}
    xshift=6.6cm,
    xmin=0, xmax=180, ymin=0, ymax=100,
    xtick={{0,45,90,135,180}}, ytick={{0,10,50,90}},
    xticklabel={{$\pgfmathprintnumber{{\tick}}^\circ$}},
    xlabel={{angle $\theta$ de la direction}},
    ylabel={{variance des projections $f(\theta)$}}]
    \addplot[sectioncolor, very thick, domain=0:180, samples=91] {{50 + 40*sin(2*x)}};
    \draw[gray!60, dashed] (axis cs:0,50) -- (axis cs:180,50);
    \node[circle, fill=steelblue4, inner sep=1.6pt,
      label={{[etiq]above:$f(45^\circ) = 90$}}] at (axis cs:45,90) {{}};
    \node[circle, fill=coveraccent, inner sep=1.6pt,
      label={{[etiq]below:$f(135^\circ) = 10$}}] at (axis cs:135,10) {{}};
    \node[circle, fill=sectioncolor, inner sep=1.6pt,
      label={{[etiq]right:$f(0^\circ) = 50$}}] at (axis cs:0,50) {{}};
  \end{{axis}}
\end{{tikzpicture}}""")


def fig_axes_principaux():
    pts = "\n".join(f"    \\node[pt] at (axis cs:{fmt(x)},{fmt(y)}) {{}};" for x, y in zip(MATH, SCI))
    r1, r2 = 2 * math.sqrt(90), 2 * math.sqrt(10)
    ecrire("fig-acp-axes-principaux", rf"""
\begin{{tikzpicture}}
  \begin{{axis}}[{axes("5.4cm", "5.4cm")}
    title={{Ellipse et vecteurs propres}},
    xmin=55, xmax=85, ymin=60, ymax=90,
    xtick={{55,60,...,85}}, ytick={{60,65,...,90}},
    xlabel={{Mathématiques}}, ylabel={{Sciences}}]
    \draw[figaux, fill opacity=0.35, rotate around={{45:(axis cs:70,75)}}]
      (axis cs:70,75) ellipse [x radius={fmt(r1)}, y radius={fmt(r2)}];
{pts}
    \draw[fleche, firebrick3] (axis cs:70,75) -- (axis cs:{fmt(70 + math.sqrt(45))},{fmt(75 + math.sqrt(45))})
      node[etiq, pos=0.45, above left] {{$\sqrt{{90}}\,\vec{{v}}_1$}};
    \draw[fleche, firebrick3] (axis cs:70,75) -- (axis cs:{fmt(70 + math.sqrt(5))},{fmt(75 - math.sqrt(5))})
      node[etiq, pos=0.6, below left] {{$\sqrt{{10}}\,\vec{{v}}_2$}};
  \end{{axis}}
  \begin{{axis}}[{axes("5.4cm", "5.4cm")}
    xshift=6.9cm, title={{Trois droites}},
    xmin=55, xmax=85, ymin=60, ymax=90,
    xtick={{55,60,...,85}}, ytick={{60,65,...,90}},
    xlabel={{Mathématiques}}, ylabel={{Sciences}},
    legend pos=south east, legend cell align=left,
    legend style={{font=\scriptsize, draw=gray!40, fill=white}}]
    \addplot[steelblue4, very thick, domain=55:85, samples=2] {{x + 5}};
    \addlegendentry{{axe principal}}
    \addplot[firebrick3, thick, dashed, domain=55:85, samples=2] {{0.8*x + 19}};
    \addlegendentry{{$y$ selon $x$}}
    \addplot[coveraccent, thick, densely dashdotted, domain=58:81.6, samples=2] {{1.25*x - 12.5}};
    \addlegendentry{{$x$ selon $y$}}
{pts}
  \end{{axis}}
\end{{tikzpicture}}""")


# ── 2. Les manchots de Palmer ────────────────────────────────────────────
def manchots():
    with open(os.path.join(ICI, "manchots.csv"), encoding="utf-8") as f:
        lignes = [r for r in csv.DictReader(f) if r["bill_length_mm"] != "NA"]
    X = np.array([[float(r[k]) for k in ("bill_length_mm", "bill_depth_mm",
                                         "flipper_length_mm", "body_mass_g")]
                  for r in lignes])
    esp = np.array([r["species"] for r in lignes])
    return X, esp


def par_espece(P, esp):
    return [P[esp == cle] for cle, *_ in ESPECES]


def fig_manchots_3d(X, esp):
    lignes = []
    for (cle, nom, couleur, marque), pts in zip(ESPECES, par_espece(X[:, :3], esp)):
        lignes.append(
            f"    \\addplot3[only marks, mark={marque}, mark size=0.9pt, color={couleur}, "
            f"fill opacity=0.65, draw opacity=0.9]\n      coordinates {{\n      {coords(pts, 1)}}};")
    ecrire("fig-acp-manchots-3d", rf"""
\begin{{tikzpicture}}
  \begin{{axis}}[
    width=8cm, height=7cm, view={{125}}{{22}},
    tick label style={{font=\scriptsize}}, label style={{font=\scriptsize, sloped}},
    grid=major, grid style={{gray!18, very thin}},
    axis line style={{gray!70}},
    xmin=30, xmax=60, ymin=13, ymax=22, zmin=170, zmax=235,
    xlabel={{longueur du bec (mm)}}, ylabel={{hauteur du bec (mm)}},
    zlabel={{nageoire (mm)}}]
{chr(10).join(lignes)}
  \end{{axis}}
{legende("3.4cm,-1.1cm")}
\end{{tikzpicture}}""")


def fig_manchots_plans(X, esp):
    noms = ["longueur du bec (mm)", "hauteur du bec (mm)", "nageoire (mm)"]
    lim = [(30, 60), (13, 22), (170, 235)]
    paires = [(0, 1), (0, 2), (1, 2)]
    panneaux = []
    for k, (i, j) in enumerate(paires):
        panneaux.append(rf"""
  \begin{{axis}}[{axes("3.6cm", "3.6cm")}
    xshift={k * 4.75}cm,
    xmin={lim[i][0]}, xmax={lim[i][1]}, ymin={lim[j][0]}, ymax={lim[j][1]},
    xlabel={{{noms[i]}}}, ylabel={{{noms[j]}}}]
{nuage_especes(par_espece(X[:, [i, j]], esp), "0.8pt")}
  \end{{axis}}""")
    ecrire("fig-acp-manchots-plans", r"\begin{tikzpicture}" + "".join(panneaux) +
           legende("6.55cm,-1.0cm") + "\n\\end{tikzpicture}")


def fig_manchots_acp(X, esp):
    valeurs, V, Z = acp(X[:, :3])
    # signes choisis pour la lecture : papous à droite, bec haut vers le haut
    if V[2, 0] < 0:
        V[:, 0] *= -1
    if V[1, 1] < 0:
        V[:, 1] *= -1
    if V[2, 2] < 0:
        V[:, 2] *= -1
    Y = Z @ V
    print("manchots 3D :", valeurs, valeurs / valeurs.sum())
    print(V)
    pc = rf"""
  \begin{{axis}}[{axes("5.4cm", "4.2cm")}
    title={{Plan des axes $\vec{{v}}_1$ et $\vec{{v}}_2$ (\num{{92.3}}\,\%)}},
    xmin=-3.5, xmax=3.5, ymin=-2.5, ymax=3,
    xlabel={{première composante $y_1$}}, ylabel={{deuxième composante $y_2$}}]
{nuage_especes(par_espece(Y[:, [0, 1]], esp), "0.8pt")}
  \end{{axis}}"""
    mauvais = rf"""
  \begin{{axis}}[{axes("5.4cm", "4.2cm")}
    xshift=6.9cm,
    title={{Plan des axes $\vec{{v}}_2$ et $\vec{{v}}_3$ (\num{{33.2}}\,\%)}},
    xmin=-3.5, xmax=3.5, ymin=-2.5, ymax=3,
    xlabel={{deuxième composante $y_2$}}, ylabel={{troisième composante $y_3$}}]
{nuage_especes(par_espece(Y[:, [1, 2]], esp), "0.8pt")}
  \end{{axis}}"""
    ecrire("fig-acp-manchots-acp", r"\begin{tikzpicture}" + pc + mauvais +
           legende("6.15cm,-1.0cm") + "\n\\end{tikzpicture}")


# ── 3. Le décathlon ──────────────────────────────────────────────────────
EPREUVES = ["100 m", "longueur", "poids", "hauteur", "400 m", "110 m haies",
            "disque", "perche", "javelot", "1500 m"]


def decathlon():
    with open(os.path.join(ICI, "decathlon.csv"), encoding="utf-8") as f:
        lignes = list(csv.DictReader(f))
    cles = list(lignes[0].keys())[1:11]
    X = np.array([[float(r[k]) for k in cles] for r in lignes])
    noms = [r["athlete"] for r in lignes]
    points = np.array([float(r["Points"]) for r in lignes])
    return X, noms, points


def fig_eboulis(X):
    valeurs, V, Z = acp(X)
    print("décathlon :", valeurs, np.cumsum(valeurs) / valeurs.sum())
    barres = " ".join(f"({k + 1},{fmt(l)})" for k, l in enumerate(valeurs))
    etiq = "\n".join(
        f"    \\node[etiq, above, text=black!70] at (axis cs:{k + 1},{fmt(l)}) {{\\num{{{100 * l / valeurs.sum():.1f}}}\\,\\%}};"
        for k, l in enumerate(valeurs[:5]))
    ecrire("fig-acp-eboulis", rf"""
\begin{{tikzpicture}}
  \begin{{axis}}[{axes("9cm", "4.2cm")}
    ybar, bar width=0.55cm, ymajorgrids, xmajorgrids=false, xtick pos=bottom,
    xmin=0.4, xmax=10.6, ymin=0, ymax=3.7,
    xtick={{1,...,10}}, ytick={{0,1,2,3}},
    xlabel={{numéro $k$ de la composante}}, ylabel={{valeur propre $\lambda_k$}}]
    \addplot[fill=steelblue4!55, draw=steelblue4] coordinates {{{barres}}};
    \draw[firebrick3, thick, dashed] (axis cs:0.4,1) -- (axis cs:10.6,1)
      node[etiq, above left, text=firebrick3] {{$\lambda = 1$}};
{etiq}
  \end{{axis}}
\end{{tikzpicture}}""")


def fig_decathlon(X, noms, points):
    valeurs, V, Z = acp(X)
    if V[1, 0] < 0:            # la longueur du côté positif du premier axe
        V[:, 0] *= -1
    if V[6, 1] < 0:            # le disque du côté positif du second axe
        V[:, 1] *= -1
    Y = Z @ V
    print("corrélation y1 / points :", np.corrcoef(Y[:, 0], points)[0, 1])
    print(np.round(V[:, :3], 3))
    pts = coords(Y[:, :2], 2)
    nommer = {"Karpov": "below", "Sebrle": "above", "Clay": "left",
              "Casarsa": "right", "BOURGUIGNON": "below right", "Drews": "right",
              "Macey": "above", "Warners": "below"}
    noeuds = "\n".join(
        f"    \\node[etiq, {pos}, text=black!75] at (axis cs:{fmt(Y[i, 0], 2)},{fmt(Y[i, 1], 2)}) {{{noms[i].capitalize()}}};"
        for i, n in enumerate(noms) for nom, pos in nommer.items() if n == nom)
    ecrire("fig-acp-decathlon", rf"""
\begin{{tikzpicture}}
  \begin{{axis}}[{axes("11.8cm", "6.8cm")}
    xmin=-4.6, xmax=5.4, ymin=-3.6, ymax=4.4,
    xlabel={{première composante $y_1$}}, ylabel={{deuxième composante $y_2$}}]
    \addplot[only marks, mark=*, mark size=1.2pt, color=sectioncolor, fill opacity=0.7]
      coordinates {{
      {pts}}};
{noeuds}
  \end{{axis}}
\end{{tikzpicture}}""")


if __name__ == "__main__":
    fig_notes()
    fig_residus()
    fig_angle()
    fig_axes_principaux()
    X, esp = manchots()
    fig_manchots_3d(X, esp)
    fig_manchots_plans(X, esp)
    fig_manchots_acp(X, esp)
    D, noms, points = decathlon()
    fig_eboulis(D)
    fig_decathlon(D, noms, points)
