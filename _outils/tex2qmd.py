#!/usr/bin/env python3
"""Conversion d'un chapitre de Livre.tex (classe livrejs) en fichier .qmd.

Outil de migration ponctuel : il produit une première version du chapitre,
à relire, qui devient ensuite la source principale. Il connaît les
conventions du livre (environnements de livrejs.cls, figures TikZ, notes
historiques avec portrait, exercices et solutions) et rien d'autre.

    python3 _outils/tex2qmd.py ../Livre.tex 3 03-fractales.qmd

Les figures TikZ sont extraites dans figures/tikz/<nom>.tikz : le livre
(PDF) les inclut telles quelles, la version web les reçoit en SVG.
"""
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
DOSSIER_TIKZ = RACINE / "figures" / "tikz"

# Environnements à titre : \begin{env}{Titre}\label{...}
ENV_TITRE = ["theorem", "proposition", "lemma", "corollary", "definition",
             "example", "remark", "historical", "secondaire", "outil",
             "algorithme"]
ENV_SIMPLES = ["solution", "proof", "extrait"]
ENV_MATH = ["align", "align*", "equation", "equation*", "gather", "gather*",
            "multline", "multline*"]

# Chemins des images dans le nouveau projet
CHEMINS_IMAGES = {"figures/py-": "figures/python/py-",
                  "figures/": "figures/portraits/"}

PH = "\u27e6{}{}\u27e7"  # ⟦M12⟧ : marqueurs temporaires


# ── Outils d'analyse ─────────────────────────────────────────────────────
def accolade(s, i):
    """s[i] == '{' : renvoie l'indice qui suit l'accolade fermante."""
    assert s[i] == "{", s[i:i + 30]
    prof = 0
    j = i
    while j < len(s):
        c = s[j]
        if c == "\\":
            j += 2
            continue
        if c == "{":
            prof += 1
        elif c == "}":
            prof -= 1
            if prof == 0:
                return j + 1
        j += 1
    raise ValueError("accolade non fermée : " + s[i:i + 60])


def crochet(s, i):
    """s[i] == '[' : renvoie l'indice qui suit le crochet fermant (niveau 0)."""
    prof = 0
    j = i
    while j < len(s):
        c = s[j]
        if c == "{":
            j = accolade(s, j)
            continue
        if c == "[":
            prof += 1
        elif c == "]":
            prof -= 1
            if prof == 0:
                return j + 1
        j += 1
    raise ValueError("crochet non fermé")


def fin_env(s, nom, debut):
    """Indice de début du \\end{nom} correspondant, en tenant compte de
    l'imbrication ; debut est juste après le \\begin{nom}."""
    b = "\\begin{" + nom + "}"
    e = "\\end{" + nom + "}"
    prof = 1
    j = debut
    while True:
        ib = s.find(b, j)
        ie = s.find(e, j)
        if ie < 0:
            raise ValueError("\\end{%s} manquant" % nom)
        if 0 <= ib < ie:
            prof += 1
            j = ib + len(b)
        else:
            prof -= 1
            if prof == 0:
                return ie
            j = ie + len(e)


def arg(s, i):
    """Lit un argument {..} à partir de i (espaces sautés)."""
    while i < len(s) and s[i] in " \t\n":
        i += 1
    f = accolade(s, i)
    return s[i + 1:f - 1], f


def opt(s, i):
    """Lit un argument optionnel [..] s'il est présent."""
    j = i
    while j < len(s) and s[j] in " \t":
        j += 1
    if j < len(s) and s[j] == "[":
        f = crochet(s, j)
        return s[j + 1:f - 1], f
    return None, i


def label_suivant(s, i):
    """Lit un \\label{..} qui suit immédiatement (espaces permis)."""
    m = re.match(r"\s*\\label\{([^}]*)\}", s[i:])
    if m:
        return m.group(1), i + m.end()
    return None, i


def sans_commentaires(s):
    lignes = []
    for l in s.split("\n"):
        if l.lstrip().startswith("%"):
            continue
        l = re.sub(r"(?<!\\)%.*$", "", l)
        lignes.append(l)
    return "\n".join(lignes)


def attr(v):
    return '"' + v.replace('"', '\\"') + '"'


# ── Convertisseur ────────────────────────────────────────────────────────
class Convertisseur:
    def __init__(self):
        self.reserve = {}       # marqueur -> texte final (blocs protégés)
        self.math = {}          # marqueur -> math
        self.n = 0
        self.tikz = {}          # nom de fichier -> code
        self.contexte = []      # pile des étiquettes d'environnements
        self.niveau_liste = 0

    def marque(self, prefixe, contenu, table):
        self.n += 1
        m = PH.format(prefixe, self.n)
        table[m] = contenu
        return m

    # -- figures TikZ --------------------------------------------------------
    def fichier_tikz(self, base, code):
        nom = base
        k = 2
        while nom in self.tikz:
            nom = "%s-%d" % (base, k)
            k += 1
        self.tikz[nom] = code.strip("\n") + "\n"
        return "figures/tikz/%s.tikz" % nom

    def nom_contexte(self):
        for lab in reversed(self.contexte):
            if lab:
                pre, _, reste = lab.partition(":")
                return "%s-%s" % (pre, reste)
        return "figure"

    def extraire_figures(self, s):
        # \begin{figure}...\end{figure}
        out = []
        i = 0
        while True:
            k = s.find("\\begin{figure}", i)
            if k < 0:
                out.append(s[i:])
                break
            out.append(s[i:k])
            d = k + len("\\begin{figure}")
            _, d = opt(s, d)
            f = fin_env(s, "figure", d)
            corps = s[d:f]
            i = f + len("\\end{figure}")
            out.append(self.figure(corps))
        return "".join(out)

    def figure(self, corps):
        lab = None
        m = re.search(r"\\label\{([^}]*)\}", corps)
        if m:
            lab = m.group(1)
            corps = corps[:m.start()] + corps[m.end():]
        leg = ""
        k = corps.find("\\caption")
        if k >= 0:
            leg, f = arg(corps, k + len("\\caption"))
            corps = corps[:k] + corps[f:]
        corps = corps.replace("\\centering", "")
        corps = corps.strip("\n")
        corps = "\n".join(l[2:] if l.startswith("  ") else l
                          for l in corps.split("\n"))
        mi = re.search(r"\\includegraphics(\[[^\]]*\])?\{([^}]*)\}", corps)
        if mi and "tikzpicture" not in corps:
            src = self.chemin_image(mi.group(2))
            larg = self.largeur(mi.group(1))
        else:
            base = lab.replace(":", "-") if lab else self.nom_contexte()
            src = self.fichier_tikz(base, sans_commentaires_tikz(corps))
            larg = ""
        texte_leg = self.texte(sans_commentaires(leg))
        texte_leg = " ".join(l.strip() for l in texte_leg.split("\n"))
        bloc = "::: {#%s}\n![](%s)%s\n\n%s\n:::" % (lab or "", src, larg,
                                                   texte_leg)
        return "\n\n" + self.marque("B", bloc, self.reserve) + "\n\n"

    def largeur(self, o):
        if not o:
            return ""
        m = re.search(r"width=([\d.]*)\\(text|line)width", o)
        if m:
            v = float(m.group(1) or 1)
            return "{width=%d%%}" % round(v * 100)
        return ""

    def chemin_image(self, p):
        if not re.search(r"\.\w+$", p):
            p += ".png"
        for a, b in CHEMINS_IMAGES.items():
            if p.startswith(a) and p.count("/") == 1:
                return b + p[len(a):]
        return p

    # -- code ------------------------------------------------------------------
    def listings(self, s):
        motif = re.compile(r"\\begin\{lstlisting\}(\[)?")
        out = []
        i = 0
        while True:
            m = motif.search(s, i)
            if not m:
                out.append(s[i:])
                break
            out.append(s[i:m.start()])
            d = m.end()
            options = ""
            if m.group(1):
                f = crochet(s, m.start(1))
                options = s[m.start(1) + 1:f - 1]
                d = f
            f = s.index("\\end{lstlisting}", d)
            code = s[d:f].strip("\n")
            i = f + len("\\end{lstlisting}")
            langue = "python" if "stylePy" in options else (
                "r" if "styleR" in options else "")
            cap = ""
            k = options.find("caption=")
            if k >= 0:
                c, _ = arg(options, k + len("caption="))
                cap = " ".join(self.texte(c).split())
            att = "." + langue if langue else ""
            ml = re.search(r"label=\{?([^,}\]]*)\}?", options)
            if ml:
                att += " #" + ml.group(1).strip()
            if cap:
                att += " caption=" + attr(cap)
            bloc = "```{%s}\n%s\n```" % (att.strip(), code)
            out.append("\n\n" + self.marque("B", bloc, self.reserve) + "\n\n")
        return "".join(out)

    # -- mathématiques -----------------------------------------------------------
    def proteger_math(self, s):
        # environnements mathématiques hors mode math : gardés tels quels
        for nom in ENV_MATH:
            b = "\\begin{%s}" % nom
            while b in s:
                k = s.index(b)
                f = fin_env(s, nom, k + len(b)) + len("\\end{%s}" % nom)
                s = s[:k] + self.marque("M", s[k:f], self.math) + s[f:]
        # \[ ... \]
        def bloc(m):
            l = [x.strip() for x in m.group(1).strip().split("\n")]
            return self.marque("M", "$$\n" + "\n".join("  " + x for x in l)
                               + "\n$$", self.math)
        s = re.sub(r"(?<!\\)\\\[(.*?)\\\]", bloc, s, flags=re.S)
        # $...$
        s = re.sub(r"(?<!\\)\$(.+?)(?<!\\)\$",
                   lambda m: self.marque("M", "$" + re.sub(
                       r"\n\s*", "\n", m.group(1)) + "$", self.math),
                   s, flags=re.S)
        return s

    # -- texte courant -----------------------------------------------------------
    def commande(self, s, nom, rempl, opt_permis=False):
        """Remplace \\nom{x} par rempl(x) (avec imbrication)."""
        motif = "\\" + nom
        out = []
        i = 0
        while True:
            k = s.find(motif + "{", i)
            if k < 0:
                k2 = s.find(motif + "[", i) if opt_permis else -1
                if k2 < 0:
                    out.append(s[i:])
                    break
                k = k2
            out.append(s[i:k])
            j = k + len(motif)
            o = None
            if s[j] == "[":
                f = crochet(s, j)
                o = s[j + 1:f - 1]
                j = f
            f = accolade(s, j)
            contenu = s[j + 1:f - 1]
            out.append(rempl(contenu, o) if opt_permis else rempl(contenu))
            i = f
        return "".join(out)

    def texte(self, s):
        """Conversion des commandes de texte en Markdown."""
        s = re.sub(r"\\texorpdfstring\{([^{}]*)\}\{[^{}]*\}", r"\1", s)
        s = self.commande(s, "emph", lambda x: "*" + self.texte(x) + "*")
        s = self.commande(s, "textit", lambda x: "*" + self.texte(x) + "*")
        s = self.commande(s, "textbf", lambda x: "**" + self.texte(x) + "**")
        s = self.commande(s, "defi", lambda x: "[" + self.texte(x) + "]{.defi}")
        s = self.commande(s, "texttt", lambda x: "`" + desechapper_tt(x) + "`")
        s = self.commande(s, "footnote", lambda x: "^[" + " ".join(
            self.texte(x).split()) + "]")
        s = self.commande(s, "hyperref",
                          lambda x, o: "[%s](#%s)" % (self.texte(x), o),
                          opt_permis=True)
        s = self.commande(s, "url", lambda x: "<" + x + ">")
        s = self.commande(s, "href", lambda x: x)  # rare ; à relire
        # citations : ~\cite{a,b} -> [@a; @b]
        s = re.sub(r"~?\\cite\{([^}]*)\}",
                   lambda m: " [" + "; ".join(
                       "@" + c.strip() for c in m.group(1).split(",")) + "]",
                   s)
        # renvois : l'espace insécable est rétabli par le filtre
        s = re.sub(r"~(\\(?:eq)?ref\{)", r" \1", s)
        s = s.replace("\\ldots", "…").replace("\\dots", "…")
        s = s.replace("\\%", "%").replace("\\&", "&")
        s = s.replace("~", "\u00a0")
        s = s.replace("\\enspace", " ")
        return s

    # -- environnements ----------------------------------------------------------
    def blocs(self, s, prof=0):
        """Convertit une suite de blocs (texte + environnements)."""
        out = []
        i = 0
        motif = re.compile(r"\\begin\{([a-zA-Z*]+)\}")
        while True:
            m = motif.search(s, i)
            if not m:
                out.append(self.paragraphes(s[i:]))
                break
            avant = s[i:m.start()]
            nom = m.group(1)
            d = m.end()
            f = fin_env(s, nom, d)
            corps = s[d:f]
            i = f + len("\\end{%s}" % nom)
            needspace = None
            mn = re.search(r"\\Needspace\{(\d+)\\baselineskip\}\s*$", avant)
            if mn and nom in ENV_TITRE:
                needspace = mn.group(1)
                avant = avant[:mn.start()]
            out.append(self.paragraphes(avant))
            # ligne vide entre un texte et une liste : nouveau paragraphe
            # explicite (sinon le filtre colle la liste au texte, en PDF)
            if nom in ("itemize", "enumerate", "sousquestions") and \
                    avant.strip() and re.search(r"\n[ \t]*\n\s*$", avant):
                out.append("\n\n\\par\n\n")
            out.append("\n\n" + self.environnement(nom, corps, needspace, prof)
                       + "\n\n")
            # liste suivie d'une ligne vide puis de texte : nouveau paragraphe
            # explicite (sinon le filtre colle le texte à la liste, en PDF)
            if nom in ("itemize", "enumerate", "sousquestions") and re.match(
                    r"[ \t]*\n[ \t]*\n\s*[^\s\\]", s[i:]):
                out.append("\n\n\\par\n\n")
        return "".join(out)

    def environnement(self, nom, corps, needspace, prof):
        if nom in ENV_TITRE:
            titre, j = arg(corps, 0)
            lab, j = label_suivant(corps, j)
            self.contexte.append(lab)
            contenu = self.blocs(corps[j:], prof + 1)
            self.contexte.pop()
            att = "." + nom
            if lab:
                att += " #" + lab
            att += " title=" + attr(" ".join(self.texte(titre).split()))
            if needspace:
                att += ' needspace="%s"' % needspace
            return self.div(att, contenu)
        if nom == "exercice":
            o, j = opt(corps, 0)
            lab, j = label_suivant(corps, j)
            self.contexte.append(lab)
            contenu = self.blocs(corps[j:], prof + 1)
            self.contexte.pop()
            att = ".exercice" + (" ." + o if o else "")
            if lab:
                att += " #" + lab
            return self.div(att, contenu)
        if nom in ENV_SIMPLES:
            lab, j = label_suivant(corps, 0)
            if nom == "solution" and self.contexte and self.contexte[-1]:
                self.contexte.append("sol:" + self.contexte[-1].split(":", 1)[1])
            else:
                self.contexte.append(lab)
            contenu = self.blocs(corps[j:], prof + 1)
            self.contexte.pop()
            return self.div("." + nom + (" #" + lab if lab else ""), contenu)
        if nom in ("itemize", "enumerate", "sousquestions"):
            return self.liste(nom, corps, prof)
        if nom == "center":
            if "\\begin{tikzpicture}" in corps:
                src = self.fichier_tikz(self.nom_contexte(), corps.strip("\n"))
                return "![](%s)" % src
            if "\\begin{tabular}" in corps:
                return self.tableau(corps)
            return self.div(".center", self.blocs(corps, prof + 1))
        if nom == "tabular" and "\\includegraphics" in corps:
            return self.portrait(corps)
        if nom == "tabular":
            return self.tableau("\\begin{tabular}" + corps + "\\end{tabular}")
        if nom == "table":
            _, j = opt(corps, 0)
            return self.table(corps[j:])
        print("  ! environnement non converti (gardé en LaTeX) :", nom,
              file=sys.stderr)
        brut = "\\begin{%s}%s\\end{%s}" % (nom, corps, nom)
        return "```{=latex}\n" + self.restaurer_math(brut) + "\n```"

    def div(self, att, contenu):
        contenu = contenu.strip("\n")
        prof = max([len(x) for x in re.findall(r"^(:{3,})", contenu, re.M)]
                   or [2])
        fence = ":" * (prof + 1)
        return "%s {%s}\n%s\n%s" % (fence, att, contenu, fence)

    def liste(self, nom, corps, prof):
        # coupe aux \item de premier niveau
        items = []
        i = 0
        niveau = 0
        courant = None
        jeton = re.compile(r"\\begin\{(itemize|enumerate|sousquestions)\}|"
                           r"\\end\{(itemize|enumerate|sousquestions)\}|"
                           r"\\item(\[[^\]]*\])?")
        for m in jeton.finditer(corps):
            if m.group(1):
                niveau += 1
            elif m.group(2):
                niveau -= 1
            elif niveau == 0:
                if courant is not None:
                    courant[1] = corps[courant[2]:m.start()]
                    items.append(courant)
                courant = [m.group(3)[1:-1] if m.group(3) else None, "",
                           m.end()]
        if courant is not None:
            courant[1] = corps[courant[2]:]
            items.append(courant)
        lignes = []
        for k, (etiq, contenu, _) in enumerate(items):
            if nom == "itemize":
                puce = "-"
            elif nom == "sousquestions":
                puce = "%s)" % "abcdefghijklmnop"[k]
            elif etiq:
                puce = etiq
            elif self.niveau_liste >= 1:
                puce = "(%s)" % "abcdefghijklmnop"[k]
            else:
                puce = "%d." % (k + 1)
            self.niveau_liste += 1
            texte = self.restaurer(self.blocs(contenu, prof + 1)).strip("\n")
            self.niveau_liste -= 1
            texte = re.sub(r"\n{3,}", "\n\n", texte)
            texte = re.sub(r"\n\n(?=(- |\d+\. |\(?[a-z]{1,4}\) ))", "\n",
                           texte)
            retrait = " " * (len(puce) + 1)
            t = texte.split("\n")
            corps_item = t[0] + "".join(
                "\n" + (retrait + l if l.strip() else "") for l in t[1:])
            lignes.append(puce + " " + corps_item)
        sep = "\n" if all("\n\n" not in x for x in lignes) else "\n\n"
        return sep.join(lignes)

    def tableau(self, corps, legende=None, lab=None):
        """tabular -> tableau Markdown (pipe table). Les réglages que le
        Markdown ne sait pas dire (colonnes p{..}, filets verticaux,
        espacement des rangées) passent dans les attributs d'un div ;
        une table numérotée (\\caption, \\label{tab:..}) devient
        ::: {#tab:..} avec sa légende au-dessus du tableau."""
        k = corps.index("\\begin{tabular}") + len("\\begin{tabular}")
        spec, f = arg(corps, k)
        lignes = corps[f:corps.index("\\end{tabular}")]
        spec_nette = re.sub(r"@\{[^}]*\}", "", spec)
        cols = []
        j = 0
        while j < len(spec_nette):
            c = spec_nette[j]
            if c in "lcr":
                cols.append(c)
                j += 1
            elif c == "p":
                _, j = arg(spec_nette, j + 1)
                cols.append("l")
            else:
                j += 1
        speciale = "p" in spec_nette or "|" in spec_nette
        for c in ("\\toprule", "\\bottomrule", "\\small", "\\addlinespace",
                  "\\centering"):
            lignes = lignes.replace(c, "")
        tete, _, corps_t = lignes.partition("\\midrule")
        espaces = re.findall(r"\\\\\[([^\]]*)\]", corps_t)
        def cellule(c):
            c = self.restaurer_math(self.texte(c.strip()))
            # une barre verticale couperait la cellule d'un tableau Markdown
            c = re.sub(r"\$[^$]*\$", lambda m: m.group(0).replace(
                "|", "\\vert{}"), c)
            return c
        def rangees(t):
            r = []
            for x in re.split(r"\\\\(?:\[[^\]]*\])?", t):
                x = " ".join(x.split())
                if x:
                    r.append([cellule(c) for c in x.split("&")])
            return r
        h = rangees(tete)[0]
        b = rangees(corps_t)
        al = {"l": ":--", "c": ":-:", "r": "--:"}
        out = ["| " + " | ".join(h) + " |",
               "|" + "|".join(al[c] for c in cols) + "|"]
        for r in b:
            out.append("| " + " | ".join(r) + " |")
        md = "\n".join(out)
        att = []
        if lab:
            att.append("#" + lab)
        if speciale:
            att.append("colonnes=" + attr(spec))
        if espaces:
            att.append("espacement=" + attr(espaces[0]))
        if legende is not None or att:
            if not lab:
                att.insert(0, ".tableau")
            contenu = md
            if legende is not None:
                contenu = " ".join(legende.split()) + "\n\n" + md
            md = self.div(" ".join(att), contenu)
        return self.marque("B", md, self.reserve)

    def table(self, corps):
        lab = None
        m = re.search(r"\\label\{([^}]*)\}", corps)
        if m:
            lab = m.group(1)
        leg = None
        k = corps.find("\\caption")
        if k >= 0:
            leg, _ = arg(corps, k + len("\\caption"))
            leg = self.restaurer_math(self.texte(sans_commentaires(leg)))
        return self.tableau(corps, leg, lab)

    def portrait(self, corps):
        # p{..}{..} & texte : portrait à gauche, texte à droite
        corps = re.sub(r"^\{[^}]*\}", "", corps.lstrip())  # spécification
        gauche, _, droite = corps.partition("&")
        mi = re.search(r"\\includegraphics(\[[^\]]*\])?\{([^}]*)\}", gauche)
        src = self.chemin_image(mi.group(2))
        ml = re.search(r"\{\\scriptsize\s*(.*?)\\par\}", gauche, re.S)
        leg = ml.group(1) if ml else ""
        leg, _, credit = leg.partition("\\\\")
        leg = " ".join(self.texte(leg).split())
        credit = " ".join(self.texte(credit).split())
        droite = droite.replace("\\vspace{0pt}", "")
        contenu = self.blocs(droite).strip("\n")
        return self.div('.portrait src="%s" legende=%s credit=%s'
                        % (src, attr(self.restaurer_math(leg)),
                           attr(self.restaurer_math(credit))), contenu)

    def paragraphes(self, s):
        """Texte sans environnement : titres, paragraphes, commandes."""
        s = self.texte(s)
        # titres
        def titre(niv):
            def f(m):
                return "\n\n%s %s{LAB}\n\n" % ("#" * niv, m.group(2))
            return f
        for niv, cmd in [(1, "chapter"), (2, "section"), (3, "subsection"),
                         (4, "subsubsection"), (5, "paragraph")]:
            s = re.sub(r"\\%s(\*?)\{((?:[^{}]|\{[^{}]*\})*)\}" % cmd,
                       lambda m, n=niv: "\n\n%s %s%s{LAB}\n\n" % (
                           "#" * n, m.group(2),
                           " {.unnumbered}" if m.group(1) else ""), s)
        s = re.sub(r"\{LAB\}\s*\\label\{([^}]*)\}",
                   lambda m: " {#%s}" % m.group(1), s)
        s = s.replace(" {.unnumbered} {#", " {.unnumbered #")
        s = re.sub(r"\{\.unnumbered\} \{#([^}]*)\}", r"{#\1 .unnumbered}", s)
        s = s.replace("{LAB}", "")
        s = s.replace("\\sectionExercices",
                      "\n\n## Exercices {.unnumbered .exercices}\n\n")
        s = s.replace("\\finExercices", "")
        s = s.replace("\\noindent", "")
        s = re.sub(r"\\(medskip|bigskip|smallskip)\b", r"\n\n\\\1\n\n", s)
        # nettoyage des lignes
        lignes = [l.strip() for l in s.split("\n")]
        s = "\n".join(lignes)
        s = re.sub(r"\n{3,}", "\n\n", s)
        # un « a) » ou « (a) » en tête de paragraphe serait lu comme une liste
        s = s.strip("\n")
        lignes = s.split("\n")
        for k, l in enumerate(lignes):
            if k == 0 or not lignes[k - 1].strip():
                lignes[k] = re.sub(r"^(\(?[a-zA-Z0-9]{1,3})\)( )", r"\1\\)\2", l)
        s = "\n" + "\n".join(lignes) + "\n"
        return s

    # -- assemblage ----------------------------------------------------------------
    def restaurer_math(self, s):
        for _ in range(3):
            for k, v in self.math.items():
                s = s.replace(k, v)
        return s

    def restaurer(self, s):
        for _ in range(4):
            for k, v in self.reserve.items():
                s = s.replace(k, v)
        return self.restaurer_math(s)

    def convertir(self, tex):
        tex = self.listings(tex)
        tex = sans_commentaires_hors_tikz(tex)
        tex = self.extraire_figures(tex)
        tex = self.proteger_math(tex)
        qmd = self.blocs(tex)
        qmd = self.restaurer(qmd)
        qmd = re.sub(r"\n{3,}", "\n\n", qmd).strip() + "\n"
        # math en bloc : $$ sur leurs propres lignes, dans le paragraphe
        return qmd


def desechapper_tt(x):
    x = x.replace("\\textbackslash ", "\\").replace("\\textbackslash{}", "\\")
    x = x.replace("\\^{}", "^").replace("\\_", "_").replace("\\{", "{")
    return x.replace("\\}", "}").replace("\\%", "%").replace("\\&", "&")


def sans_commentaires_tikz(code):
    # dans les figures, on garde les commentaires (utiles à l'auteur)
    return code


def sans_commentaires_hors_tikz(s):
    """Retire les commentaires, sauf dans les tikzpicture."""
    out = []
    i = 0
    while True:
        k = s.find("\\begin{tikzpicture}", i)
        if k < 0:
            out.append(sans_commentaires(s[i:]))
            break
        out.append(sans_commentaires(s[i:k]))
        f = fin_env(s, "tikzpicture", k + 19) + len("\\end{tikzpicture}")
        out.append(s[k:f])
        i = f
    return "".join(out)


def extraire_chapitre(livre, numero):
    s = Path(livre).read_text(encoding="utf-8")
    debuts = [m.start() for m in re.finditer(r"^\\chapter\*?\{", s, re.M)]
    a = debuts[numero - 1]
    b = debuts[numero] if numero < len(debuts) else s.index("\\end{document}")
    return s[a:b]


def main():
    livre, numero, sortie = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    tex = extraire_chapitre(livre, numero)
    c = Convertisseur()
    qmd = c.convertir(tex)
    Path(sortie).write_text(qmd, encoding="utf-8")
    DOSSIER_TIKZ.mkdir(parents=True, exist_ok=True)
    for nom, code in c.tikz.items():
        (DOSSIER_TIKZ / (nom + ".tikz")).write_text(c.restaurer_math(code),
                                                    encoding="utf-8")
    print("%s : %d lignes, %d figures TikZ" % (sortie, qmd.count("\n"),
                                               len(c.tikz)))


if __name__ == "__main__":
    main()
