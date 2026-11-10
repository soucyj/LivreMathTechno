# Diaporama --- Chapitre 4 : Les chaînes de Markov et l'algorithme PageRank

Diaporama Beamer pour un exposé magistral (visé : ~4 heures) reprenant
le contenu du chapitre 4 des notes (`04-markov.qmd`).

Le préambule est celui du chapitre 2, complété par les macros et les
styles TikZ des chapitres 3 et 4 du livre, et par `listings` pour les
programmes Python (programmes 4.1, 4.5, 4.7 et 4.9 des notes,
légèrement raccourcis pour tenir sur une diapositive). Les portraits
viennent de `../../figures/portraits/`.

## Compiler

```
cd chapitre4
lualatex main.tex        # deux passages, pour le sommaire
lualatex main.tex
```

## Structure

```
chapitre4/
├── main.tex
├── preambule.tex
└── sections/
    ├── 00-introduction.tex     Internaute aléatoire, figure 4.1, note historique 4.1
    ├── 01-rappels-proba.tex    §4.1 Probabilités conditionnelles, espérance, classe 4.1
    ├── 02-meteo.tex            §4.2 Météo à deux états, équilibre, programme 4.1, outil 4.1
    ├── 03-chaines.tex          §4.3 Chaînes de Markov, migration, mémoire, note 4.2
    ├── 04-stochastiques.tex    §4.4 Matrices stochastiques, convergence, classe 4.3
    ├── 05-pagerank.tex         §4.5 PageRank, pages sans lien, téléportation, matrice Google
    ├── 06-puissances.tex       §4.6 Méthode des puissances, Banach, note 4.4
    └── 07-conclusion.tex
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
