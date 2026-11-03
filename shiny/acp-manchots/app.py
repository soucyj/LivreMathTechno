"""
À la recherche du meilleur plan — l'ACP des manchots de l'archipel Palmer
MAT-2901, chapitre 5 (Analyse en composantes principales)

Lancer l'application :
    shiny run --reload app.py          (puis ouvrir l'adresse affichée)

Principe : le plan de projection est le plan de l'écran. Faire tourner le
nuage, c'est choisir un plan ; à droite, on voit l'ombre du nuage sur ce
plan, mise à plat, et la part de la variance qu'il conserve.

Python fait les calculs (réduction des variables, matrice de corrélation,
vecteurs propres, variance conservée) ; graphiques.js dessine avec Plotly
et lit le point de vue de la caméra.
"""

from pathlib import Path
import json

import numpy as np
import pandas as pd
from shiny import App, reactive, render, ui

ICI = Path(__file__).parent

# ─────────────────────────────────────────────────────────────────────
#  Données : les 342 manchots et leurs trois mesures, réduites (cotes z)
# ─────────────────────────────────────────────────────────────────────
VARIABLES = ["bill_length_mm", "bill_depth_mm", "flipper_length_mm"]
NOMS_VAR = ["longueur du bec", "hauteur du bec", "longueur de la nageoire"]
NOMS_COURTS = ["Long. du bec", "Haut. du bec", "Nageoire"]

ESPECES = ["Adelie", "Chinstrap", "Gentoo"]
NOMS_ESP = ["Adélie", "à jugulaire", "papou"]

manchots = pd.read_csv(ICI / "manchots.csv").dropna(subset=VARIABLES)
manchots = manchots.reset_index(drop=True)
X = manchots[VARIABLES].to_numpy(dtype=float)
n = len(X)

# Réduire : chaque mesure devient une cote z (moyenne 0, écart type 1).
Z = (X - X.mean(axis=0)) / X.std(axis=0, ddof=1)

# La matrice de covariance des variables réduites = matrice de corrélation R.
R = (Z.T @ Z) / (n - 1)

# Valeurs propres et vecteurs propres de R, de la plus grande à la plus
# petite. Le signe d'un vecteur propre est arbitraire : on choisit celui
# du livre (troisième composante positive).
lam, V = np.linalg.eigh(R)
ordre = np.argsort(lam)[::-1]
lam, V = lam[ordre], V[:, ordre]
V = V * np.where(V[2, :] < 0, -1, 1)
VP = [V[:, k] for k in range(3)]

# Meilleur et pire plan (pour la jauge).
PART_MAX = 100 * (lam[0] + lam[1]) / 3
PART_MIN = 100 * (lam[1] + lam[2]) / 3

# Point de vue de départ (le même que dans graphiques.js).
OEIL_DEPART = np.array([1.55, -1.45, 0.85])
HAUT_DEPART = np.array([0.0, 0.0, 1.0])

# Ce qui est envoyé une seule fois au navigateur.
code_esp = manchots["species"].map({e: k for k, e in enumerate(ESPECES)})
infos = [
    f"<b>Manchot {i + 1}</b> ({NOMS_ESP[c]})<br>"
    f"bec : {x[0]:.1f} mm × {x[1]:.1f} mm<br>nageoire : {x[2]:.0f} mm".replace(".", ",")
    for i, (c, x) in enumerate(zip(code_esp, X))
]
DONNEES_JS = {
    "z": np.round(Z, 3).tolist(),
    "espece": code_esp.tolist(),
    "info": infos,
    "nomsEspeces": NOMS_ESP,
    "nomsAxes": [f"{v} (cote z)" for v in NOMS_COURTS],
    "vp": [v.tolist() for v in VP],
}


# ─────────────────────────────────────────────────────────────────────
#  Petits outils
# ─────────────────────────────────────────────────────────────────────
def fr(x, d=2):
    """Nombre à la française : virgule décimale, vrai signe moins."""
    s = f"{x:.{d}f}".replace(".", ",")
    if s.startswith("-"):
        s = "−" + s[1:]
    if s in ("−0", "−0,0", "−0,00", "−0,000"):
        s = s[1:]
    return s


def frm(x, d=2):
    """Nombre à la française dans une formule MathJax (virgule sans espace)."""
    return fr(x, d).replace(",", "{,}").replace("−", "-")


def fmt_vec(w, d=2):
    return "(" + " ; ".join(fr(c, d) for c in w) + ")"


def base_du_plan(oeil, haut):
    """Base orthonormée (e1, e2) du plan de l'écran et direction du regard n.

    n pointe vers l'observateur ; e2 est la verticale de l'écran (le vecteur
    « haut » de la caméra, rendu perpendiculaire à n) ; e1 = e2 × n est
    l'horizontale de l'écran.
    """
    nn = np.asarray(oeil, float)
    nn = nn / np.linalg.norm(nn)
    h = np.asarray(haut, float)
    w = h - (h @ nn) * nn
    if np.linalg.norm(w) < 1e-6:
        w = np.cross(nn, [1, 0, 0] if abs(nn[0]) < 0.9 else [0, 1, 0])
    e2 = w / np.linalg.norm(w)
    e1 = np.cross(e2, nn)
    return e1, e2, nn


# ─────────────────────────────────────────────────────────────────────
#  Interface
# ─────────────────────────────────────────────────────────────────────
def bouton(id_, texte, classe):
    return ui.input_action_button(id_, ui.HTML(texte), class_=f"btn-sm {classe}")


def remplir(html):
    """Insère les nombres calculés dans un texte HTML (sans toucher aux accolades LaTeX)."""
    for cle, val in {
        "§MAX§": frm(PART_MAX, 1), "§MIN§": frm(PART_MIN, 1),
        "§L1§": frm(lam[0], 3), "§L2§": frm(lam[1], 3), "§L3§": frm(lam[2], 3),
    }.items():
        html = html.replace(cle, val)
    return ui.HTML(html)


tableau_vp = ui.HTML(
    "<table class='table-vp'><thead><tr><th></th>"
    + "".join(f"<th>{v}</th>" for v in NOMS_COURTS)
    + "<th>valeur propre</th></tr></thead><tbody>"
    + "".join(
        f"<tr><td>\\(\\vec v_{k + 1}\\)</td>"
        + "".join(f"<td>{fr(c, 3)}</td>" for c in VP[k])
        + f"<td>\\(\\lambda_{k + 1} = {frm(lam[k], 3)}\\)</td></tr>"
        for k in range(3)
    )
    + "</tbody></table>"
)

entete = ui.div(
    {"class": "entete"},
    ui.div({"class": "surtitre"}, "MAT-2901 · Chapitre 5 · Analyse en composantes principales"),
    ui.h1("À la recherche du meilleur plan"),
    ui.p(
        {"class": "chapeau"},
        "Chaque manchot est un point de l'espace : ses trois coordonnées sont la longueur "
        "et la hauteur de son bec, et la longueur de sa nageoire (réduites en cotes z). "
        "Ce que vous voyez à l'écran est une projection du nuage sur le plan de l'écran : ",
        ui.strong("faire tourner le nuage, c'est choisir un plan de projection."),
    ),
    ui.div(
        {"class": "etapes"},
        ui.div(ui.span({"class": "num"}, "1"),
               ui.span("Faites tourner le nuage de gauche avec la souris (ou le doigt).")),
        ui.div(ui.span({"class": "num"}, "2"),
               ui.span("À droite, l'ombre du nuage sur le plan de l'écran, mise à plat. "
                       "Les trois espèces sont-elles bien séparées ?")),
        ui.div(ui.span({"class": "num"}, "3"),
               ui.span("Cherchez le meilleur point de vue, puis comparez avec les "
                       "vecteurs propres.")),
    ),
)

carte_3d = ui.div(
    {"class": "carte"},
    ui.h3("Le nuage dans l'espace"),
    ui.p({"class": "aide"},
         "Glisser pour tourner, molette pour zoomer. ",
         ui.output_text("aide_3d", inline=True)),
    ui.div({"id": "graphe3d", "class": "graphe"}),
    ui.div(
        {"class": "options"},
        ui.input_switch("lie", "Le plan suit votre regard", True),
        ui.input_switch("montrer_vp", "Afficher les vecteurs propres", False),
        ui.input_switch("couleurs", "Colorer selon l'espèce", True),
    ),
    ui.div(
        {"class": "rangee-boutons"},
        bouton("face", "Se placer face au plan", "btn-outline-secondary"),
        bouton("vue_depart", "Vue de départ", "btn-outline-secondary"),
    ),
)

carte_2d = ui.div(
    {"class": "carte"},
    ui.h3("L'ombre du nuage sur le plan"),
    ui.p({"class": "aide"},
         "La projection orthogonale du nuage sur le plan choisi, vue de face. "
         "Survolez un point pour voir les mesures du manchot."),
    ui.div({"id": "graphe2d", "class": "graphe"}),
    ui.output_ui("info_regard"),
)

carte_raccourcis = ui.div(
    {"class": "carte"},
    ui.h3("Raccourcis"),
    ui.p({"class": "aide"},
         "Cherchez d'abord à la main ! Puis comparez avec les plans engendrés par deux des "
         "trois vecteurs propres de la matrice de covariance des données réduites "
         "(la matrice de corrélation ", ui.em("R"), "). La caméra pivote pour se placer "
         "face au plan choisi."),
    ui.div(
        {"class": "raccourcis"},
        ui.div(
            ui.div({"class": "etiquette"}, "Vecteurs propres"),
            ui.div(
                {"class": "rangee-boutons"},
                bouton("p12", "\\(\\vec v_1\\) et \\(\\vec v_2\\)", "btn-vp"),
                bouton("p13", "\\(\\vec v_1\\) et \\(\\vec v_3\\)", "btn-vp"),
                bouton("p23", "\\(\\vec v_2\\) et \\(\\vec v_3\\)", "btn-vp"),
            ),
        ),
        ui.div(
            ui.div({"class": "etiquette"}, "Plans de coordonnées (on « oublie » une mesure)"),
            ui.div(
                {"class": "rangee-boutons"},
                bouton("c12", "bec : longueur et hauteur", "btn-outline-secondary"),
                bouton("c13", "longueur du bec et nageoire", "btn-outline-secondary"),
                bouton("c23", "hauteur du bec et nageoire", "btn-outline-secondary"),
            ),
        ),
    ),
    ui.output_ui("tableau_vp_court"),
)

explications = ui.accordion(
    ui.accordion_panel(
        "Que mesure la jauge « variance conservée » ?",
        remplir(r"""
<p>Projeter, c'est perdre de l'information : deux manchots différents peuvent avoir la même
ombre. Pour mesurer ce qu'on garde, on regarde <strong>à quel point l'ombre est
étalée</strong>. Plus elle est étalée, moins les points ont été « écrasés » les uns sur
les autres.</p>
<p>L'étalement se mesure par la variance. Le nuage réduit a une variance totale égale à
\(3\) (une unité par variable). Si \((\vec e_1, \vec e_2)\) est une base orthonormée du plan,
la variance de l'ombre vaut</p>
\[\vec e_1^{\mathsf T} R\, \vec e_1 + \vec e_2^{\mathsf T} R\, \vec e_2 ,\]
<p>où \(R\) est la matrice de corrélation, c'est-à-dire la matrice de covariance des données
réduites. La jauge affiche cette variance divisée par \(3\), en pourcentage.</p>
<p>Ce que l'on perd, c'est l'étalement du nuage dans la direction du regard \(\vec n\),
perpendiculaire au plan : \(\vec n^{\mathsf T} R\, \vec n\). C'est aussi, par le théorème de
Pythagore, la moyenne des carrés des distances des points au plan.
<strong>Le meilleur plan est donc celui que l'on obtient en regardant le nuage dans la
direction où il est le plus mince.</strong></p>
"""),
    ),
    ui.accordion_panel(
        "Pourquoi les vecteurs propres ?",
        remplir(r"""
<p>La matrice \(R\) est symétrique : elle possède trois vecteurs propres unitaires et
orthogonaux. Chaque valeur propre mesure l'étalement du nuage dans la direction du vecteur
propre correspondant.</p>
"""),
        tableau_vp,
        remplir(r"""
<ul>
<li>Dans la direction de \(\vec v_1\), le nuage est <strong>le plus étalé possible</strong>
(\(\lambda_1 = §L1§\)) ; dans celle de \(\vec v_3\), <strong>le plus mince possible</strong>
(\(\lambda_3 = §L3§\)).</li>
<li>Pour perdre le moins possible, il faut donc regarder dans la direction de \(\vec v_3\).
Le plan de l'écran est alors engendré par \(\vec v_1\) et \(\vec v_2\), et il conserve
\(\frac{\lambda_1+\lambda_2}{3} \approx §MAX§\,\%\) de la variance : aucun autre plan ne
fait mieux.</li>
<li>Le pire point de vue est dans la direction de \(\vec v_1\) : le plan est engendré par
\(\vec v_2\) et \(\vec v_3\), et ne conserve que \(§MIN§\,\%\). Le nuage y est écrasé, et
les manchots Adélie et papous s'y confondent.</li>
</ul>
<p>Sous le graphique de droite, la ligne « direction du regard » affiche
\(\vec n^{\mathsf T} R\, \vec n\). Essayez : elle ne descend jamais sous
\(\lambda_3 = §L3§\) et ne dépasse jamais \(\lambda_1 = §L1§\).</p>
"""),
    ),
    ui.accordion_panel(
        "Une mise en garde : étalé ne veut pas toujours dire séparé",
        remplir(r"""
<p>L'ACP ne connaît pas les espèces : les couleurs ont été ajoutées après coup (désactivez-les
pour voir ce que « voit » la méthode). Elle cherche le plan sur lequel le nuage est le plus
étalé. Pour les manchots, ce plan sépare aussi très bien les trois espèces, parce que les
différences entre espèces sont la principale source de variation des mesures. Ce n'est pas
garanti en général.</p>
<p>Les trois plans de coordonnées l'illustrent bien : ils conservent tous exactement
\(\frac{2}{3} \approx 66{,}7\,\%\) de la variance (pourquoi ? regardez la diagonale de
\(R\)), mais ils ne racontent pas du tout la même histoire.</p>
"""),
    ),
    ui.accordion_panel(
        "Pistes pour la classe",
        remplir(r"""
<ol>
<li>Sans les couleurs, combien de « sortes » de manchots voyez-vous dans le plan de
\(\vec v_1\) et \(\vec v_2\) ? Et dans celui de \(\vec v_2\) et \(\vec v_3\) ?</li>
<li>Affichez les vecteurs propres, puis placez-vous dans le meilleur plan. Où pointe
\(\vec v_3\) ? Pourquoi le voit-on réduit à un point ?</li>
<li>Désactivez « Le plan suit votre regard », puis faites tourner le nuage : où se trouve le
meilleur plan par rapport au nuage ? Décrivez-le avec vos mots.</li>
<li>Pourquoi la jauge ne peut-elle jamais descendre sous
\(\frac{\lambda_2+\lambda_3}{3}\) ?</li>
<li>Le graphique de gauche est dessiné en projection orthogonale, sans effet de
perspective. Pourquoi regarder un objet de très loin revient-il (presque) à le projeter ?</li>
<li>Au secondaire : quelles situations (élèves, villes, sportifs…) se prêteraient à une
activité semblable, avec trois mesures et des « groupes » cachés ?</li>
</ol>
"""),
    ),
    id="explications",
    open=False,
)

app_ui = ui.page_fluid(
    ui.head_content(
        ui.tags.title("Meilleur plan — ACP des manchots"),
        ui.tags.meta(name="viewport", content="width=device-width, initial-scale=1"),
        ui.tags.script(src="https://cdn.jsdelivr.net/npm/plotly.js-dist-min@2.35.2/plotly.min.js"),
        ui.tags.script(
            "window.MathJax = {tex: {inlineMath: [['\\\\(', '\\\\)']]},"
            " svg: {fontCache: 'global'}};"
        ),
        ui.tags.script(src="https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-svg.js", async_=""),
        ui.tags.style((ICI / "style.css").read_text(encoding="utf-8")),
    ),
    entete,
    ui.output_ui("jauge"),
    ui.row(
        ui.column(6, carte_3d),
        ui.column(6, carte_2d),
    ),
    carte_raccourcis,
    ui.div({"class": "carte"}, ui.h3("Pour comprendre"), explications),
    ui.div({"class": "pied"},
           "Données : palmerpenguins (Gorman, Williams et Fraser, 2014), 342 manchots. "
           "Les trois mesures sont réduites (cotes z) avant le calcul."),
    ui.tags.script("window.ACP_DONNEES = " + json.dumps(DONNEES_JS, ensure_ascii=False) + ";"),
    ui.tags.script((ICI / "graphiques.js").read_text(encoding="utf-8")),
)


# ─────────────────────────────────────────────────────────────────────
#  Serveur
# ─────────────────────────────────────────────────────────────────────
def server(input, output, session):
    vp_montres = reactive.value(False)

    # Le plan choisi, envoyé par graphiques.js : {e1, e2, n}.
    @reactive.calc
    def plan():
        p = input.plan() if "plan" in input else None
        if not p:
            return base_du_plan(OEIL_DEPART, HAUT_DEPART)
        return tuple(np.array(p[k], float) for k in ("e1", "e2", "n"))

    @reactive.calc
    def part():
        e1, e2, _ = plan()
        return 100 * (e1 @ R @ e1 + e2 @ R @ e2) / 3

    # Options d'affichage → navigateur
    @reactive.effect
    async def _():
        await session.send_custom_message("acp_options", {
            "lie": bool(input.lie()),
            "vp": bool(input.montrer_vp()),
            "couleurs": bool(input.couleurs()),
        })

    # Raccourcis : on envoie le plan visé ; la caméra pivote pour lui faire face.
    async def aller_au_plan(a, b):
        e1, e2 = np.asarray(a, float), np.asarray(b, float)
        await session.send_custom_message("acp_aller", {
            "e1": e1.tolist(), "e2": e2.tolist(), "n": np.cross(e1, e2).tolist()})

    @reactive.effect
    @reactive.event(input.p12)
    async def _():
        vp_montres.set(True)
        await aller_au_plan(VP[0], VP[1])

    @reactive.effect
    @reactive.event(input.p13)
    async def _():
        vp_montres.set(True)
        await aller_au_plan(VP[0], VP[2])

    @reactive.effect
    @reactive.event(input.p23)
    async def _():
        vp_montres.set(True)
        await aller_au_plan(VP[1], VP[2])

    for id_, (i, j) in {"c12": (0, 1), "c13": (0, 2), "c23": (1, 2)}.items():
        def faire(i=i, j=j, id_=id_):
            @reactive.effect
            @reactive.event(input[id_])
            async def _():
                await aller_au_plan(np.eye(3)[i], np.eye(3)[j])
        faire()

    @reactive.effect
    @reactive.event(input.face)
    async def _():
        e1, e2, _ = plan()
        await aller_au_plan(e1, e2)

    @reactive.effect
    @reactive.event(input.vue_depart)
    async def _():
        await session.send_custom_message("acp_depart", {})

    # Affichages
    @render.text
    def aide_3d():
        if input.lie():
            return "Le plan choisi est celui de l'écran."
        return ("Le plan est figé (en bleu translucide) : tournez autour pour le voir "
                "dans le nuage.")

    @render.ui
    def jauge():
        p = part()
        if p >= PART_MAX - 0.05:
            msg, cls = "C'est le meilleur plan possible : aucun plan ne conserve plus de variance.", "top"
        elif p >= PART_MAX - 3:
            msg, cls = "Excellent ! Vous êtes tout près du meilleur plan.", "bien"
        elif p >= 75:
            msg, cls = "Bon plan. Peut-on faire mieux ?", "moyen"
        elif p <= PART_MIN + 0.05:
            msg, cls = "C'est le pire plan possible : le nuage y est le plus écrasé.", "faible"
        else:
            msg, cls = ("Le nuage est assez écrasé sur ce plan. "
                        "Cherchez un point de vue où il est plus étalé."), "faible"
        return ui.div(
            {"class": f"jauge carte {cls}"},
            ui.div(
                {"class": "jauge-haut"},
                ui.span({"class": "jauge-titre"}, "Variance conservée par le plan"),
                ui.span({"class": "jauge-valeur"}, f"{fr(p, 1)} %"),
                ui.span({"class": "jauge-msg"}, msg),
            ),
            ui.div(
                {"class": "jauge-barre"},
                ui.div({"class": "jauge-rempli", "style": f"width:{p:.2f}%"}),
                ui.div({"class": "repere", "style": f"left:{PART_MIN:.2f}%"}),
                ui.div({"class": "repere", "style": f"left:{PART_MAX:.2f}%"}),
            ),
            ui.div(
                {"class": "jauge-legende"},
                ui.span({"style": f"left:{PART_MIN:.2f}%"}, f"pire plan : {fr(PART_MIN, 1)} %"),
                ui.span({"style": f"left:{PART_MAX:.2f}%"}, f"meilleur plan : {fr(PART_MAX, 1)} %"),
            ),
        )

    @render.ui
    def info_regard():
        _, _, nn = plan()
        return ui.div(
            {"class": "composantes"},
            ui.div("Direction du regard (perpendiculaire au plan) : ", ui.code(fmt_vec(nn))),
            ui.div({"class": "petit"},
                   "Étalement du nuage dans cette direction, perdu par la projection : ",
                   ui.strong(fr(nn @ R @ nn, 3)),
                   f" (toujours entre {fr(lam[2], 3)} et {fr(lam[0], 3)})"),
        )

    @render.ui
    def tableau_vp_court():
        if not (vp_montres.get() or input.montrer_vp()):
            return None
        return ui.div(
            {"class": "vp-rappel"},
            ui.HTML(
                "<table class='table-vp'><thead><tr><th></th>"
                + "".join(f"<th>{v}</th>" for v in NOMS_COURTS)
                + "<th>λ</th></tr></thead><tbody>"
                + "".join(
                    f"<tr><td><i>v</i><sub>{k + 1}</sub></td>"
                    + "".join(f"<td>{fr(c, 3)}</td>" for c in VP[k])
                    + f"<td>{fr(lam[k], 3)}</td></tr>"
                    for k in range(3)
                )
                + "</tbody></table>"
            ),
            ui.p({"class": "petit"},
                 f"Plan de v₁ et v₂ : {fr(PART_MAX, 1)} %  ·  "
                 f"v₁ et v₃ : {fr(100 * (lam[0] + lam[2]) / 3, 1)} %  ·  "
                 f"v₂ et v₃ : {fr(PART_MIN, 1)} %"),
        )


app = App(app_ui, server)
