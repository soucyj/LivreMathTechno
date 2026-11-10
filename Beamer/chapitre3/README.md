# Diaporama --- Chapitre 3 : Fractales et systèmes itératifs de fonctions

Diaporama Beamer pour un exposé magistral (visé : ~5 heures) reprenant
le contenu du chapitre 3 des notes (`03-fractales.qmd`).

Le préambule est celui du chapitre 2, complété par les macros et les
styles TikZ des chapitres 3 et 4 du livre. Les figures TikZ sont
recopiées en ligne ; elles chargent toutefois leurs nuages de points et
leurs courbes depuis `../../figures/fractales/` (fichiers générés par
`figures/fractales/generer.py`), grâce à `\input@path` défini dans
`preambule.tex`. Les portraits viennent de `../../figures/portraits/`.

## Compiler

```
cd chapitre3
lualatex main.tex        # deux passages, pour le sommaire
lualatex main.tex
```

La compilation prend plus d'une minute : certaines figures (fougère,
jeu du chaos) contiennent des dizaines de milliers de points.

## Structure

```
chapitre3/
├── main.tex
├── preambule.tex
└── sections/
    ├── 00-introduction.tex        Introduction, figure 3.1 (flocon)
    ├── 01-koch.tex                §3.1.1 Courbe de von Koch, note historique 3.1
    ├── 02-sierpinski.tex          §3.1.2 Triangle et tapis, Cantor, note 3.2, classe 3.1, outil 3.1
    ├── 03-autosimilarite.tex      §3.2 Définition 3.1, exemples 3.1 à 3.4
    ├── 04-dimension.tex           §3.3 Dimension de similitude, Hausdorff, classe 3.3
    ├── 05-sif.tex                 §3.4 SIF, Hutchinson (théorèmes 3.1 à 3.3)
    ├── 06-collage.tex             §3.4.3 Collage, arbre, fougère, compression
    ├── 07-dim-generalisee.tex     §3.5 Moran, condition de l'ouvert
    ├── 08-algorithmes.tex         §3.6 Algorithme déterministe, jeu du chaos
    ├── 09-monstres-modeles.tex    §3.7 Weierstrass, Mandelbrot, finance
    └── 10-conclusion.tex
```

## Conventions typographiques

Comme pour le chapitre 2 : pas de gras ni d'italique dans le texte des
diapositives ; `siunitx` avec la virgule décimale (tous les décimaux
passent par `\num`) ; point-virgule entre les composantes décimales
d'un vecteur. Les termes définis (`\defi`) sont en couleur, sans gras,
et seulement dans les boîtes de définition.

## Ce qui a été volontairement omis

- **Les démonstrations.** Chaque résultat qui, dans les notes, porte une
  démonstration est marqué d'un encadré rouge « DÉMONSTRATION AU
  TABLEAU » avec un rappel très court de l'idée. Le détail complet reste
  dans les notes.
- **Les exercices.** Le diaporama y renvoie en conclusion.

## Numérotation

Les numéros (définitions, théorèmes, figures, tableaux, programmes) sont
ceux du livre compilé (`Mathématiques-et-technologie.aux`) au moment de
la création de ce diaporama. Il n'y a pas de synchronisation
automatique.
