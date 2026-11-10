# Diaporama --- Chapitre 2 : Espaces métriques

Diaporama Beamer pour un exposé magistral (visé : ~4 heures, avec
démonstrations au tableau) reprenant le contenu du chapitre 2 des notes
de cours (`02-metriques.qmd`) : définitions, propositions/théorèmes/lemmes
(énoncés seulement), exemples, figures, tableaux, encadrés « Outil » et
« Pour la classe », notes historiques.

Ce dossier est **autonome**, comme celui du chapitre 1 : toutes les
couleurs, tous les raccourcis mathématiques (`\dE`, `\dT`, `\dHam`,
`\dH`, `\boule`, `\Vois`, `\Comp`, etc.) et tous les styles TikZ des
figures sont redéfinis dans `preambule.tex`, à l'identique de ceux du
livre (`latex/macros-livre.tex`, `latex/commandesJS.sty`). Les figures
TikZ de `figures/tikz/` sont recopiées en ligne dans les diapositives.
Seules les images bitmap sont réutilisées depuis `../../figures/`
(`python/py-sierpinski.png`, `portraits/felix-hausdorff.jpg`,
`portraits/stefan-banach.jpg`).

## Compiler

```
cd chapitre2
lualatex main.tex        # deux passages, pour le sommaire (\tableofcontents)
lualatex main.tex
```

`lualatex` est requis : la classe utilise `fontspec`/`unicode-math`.
Aucune bibliographie, aucune étape `biber` n'est nécessaire.

## Structure

```
chapitre2/
├── main.tex              fichier principal : préambule + page titre + \input des sections
├── preambule.tex         celui du chapitre 1, + macros du chapitre 2, siunitx, boîte « Outil »
├── sections/
│   ├── 00-pourquoi.tex          Introduction, figure 2.1 (Sierpiński), plan du chapitre
│   ├── 01-distance.tex          §2.1 Déf. 2.1, distances euclidienne et taxi
│   ├── 02-sphere-hamming.tex    §2.1.2-2.1.3 Distance sphérique, Hamming, note historique 2.1
│   ├── 03-ouverts-fermes.tex    §2.2 Boules, ouverts, fermés, compacts (Heine-Borel)
│   ├── 04-hausdorff.tex         §2.3 Minkowski, ε-voisinage, d_H, notes historiques 2.2
│   ├── 05-completude.tex        §2.4 Suites convergentes, de Cauchy, complétude
│   ├── 06-point-fixe.tex        §2.5 Points fixes, Brouwer
│   ├── 07-contractions.tex      §2.6 Contractions
│   ├── 08-banach.tex            §2.7 Théorème de Banach et ses lemmes
│   ├── 09-newton.tex            §2.7.1 Newton-Raphson, notes historiques 2.3-2.4
│   └── 10-conclusion.tex        Synthèse, suites (exercices, chapitre 3)
└── README.md             ce fichier
```

## Ce qui a été volontairement omis

- **Les démonstrations.** Chaque résultat qui, dans les notes, porte une
  démonstration est marqué d'un encadré rouge **« DÉMONSTRATION AU
  TABLEAU »** avec un rappel très court de l'idée --- à l'intention de
  la personne qui présente. Le détail complet reste dans les notes.
- **Les exercices.** Ils ne sont pas repris ; le diaporama y renvoie en
  conclusion (« Et maintenant »).

## Numérotation

Les numéros (Définition 2.9, Théorème 2.3, Figure 2.15, etc.) sont ceux
du chapitre 2 du livre compilé (`Mathématiques-et-technologie.aux`) au
moment de la création de ce diaporama. Il n'y a pas de mécanisme
automatique de synchronisation : une révision du chapitre peut les
désynchroniser.
