# Diaporama --- Chapitre 5 : L'analyse en composantes principales

Diaporama Beamer pour un exposé magistral (visé : ~4 heures) reprenant
le contenu du chapitre 5 des notes (`05-acp.qmd`).

Le préambule est celui du chapitre 4, complété par `pgfplots` (les
figures du chapitre sont celles du livre, lues directement dans
`../../figures/tikz/fig-acp-*.tikz` par la commande `\FigLivre`) et par
`qrcode`. Le portrait de Pearson vient de `../../figures/portraits/`.

## L'application interactive

La section 3 (les manchots) contient une diapositive « À vous de
chercher le meilleur plan » avec un bouton, un code QR et l'adresse de
l'application shinylive publiée avec le site du livre :

<https://soucyj.github.io/LivreMathTechno/applications/acp-manchots/>

L'adresse est définie une seule fois, par `\urlappli` dans
`preambule.tex`. La diapositive « Et maintenant » de la synthèse y
renvoie aussi.

## Compiler

```
cd chapitre5
lualatex main.tex        # deux passages, pour le sommaire
lualatex main.tex
```

## Structure

```
chapitre5/
├── main.tex
├── preambule.tex
└── sections/
    ├── 00-introduction.tex       Nuages de points, la théière, le chemin du chapitre
    ├── 01-statistique.tex        §5.1 Déf. 5.1-5.2, remarques 5.1-5.2, classe 5.1
    ├── 02-droite.tex             §5.2 Déf. 5.3, prop. 5.1, exemple 5.1, théorème 5.2,
    │                             fig. 5.2-5.5, classe 5.2, remarque 5.3
    ├── 03-espace.tex             §5.3 Manchots, tableau 5.2, fig. 5.6-5.8, réduction,
    │                             classe 5.3, application interactive, outil 5.1
    ├── 04-acp.tex                §5.4 Déf. 5.4-5.5, prop. 5.3, théorème 5.4,
    │                             algorithme 5.1, remarques 5.4-5.6, programme 5.1
    ├── 05-histoire.tex           §5.4.6 Note historique 5.1 (Pearson), Hotelling
    ├── 06-grande-dimension.tex   §5.5 Décathlon, programme 5.3, fig. 5.9-5.10,
    │                             tableaux 5.3-5.4, limites, classe 5.4
    └── 07-conclusion.tex
```

## Conventions typographiques

Comme pour les chapitres précédents : pas de gras ni d'italique dans le
texte des diapositives ; `siunitx` avec la virgule décimale (tous les
décimaux passent par `\num`) ; point-virgule entre les composantes
décimales d'un vecteur. Les termes définis (`\defi`) sont en couleur,
sans gras.

## Ce qui a été volontairement omis

- **Les démonstrations.** Chaque résultat qui, dans les notes, porte une
  démonstration est marqué d'un encadré rouge « DÉMONSTRATION AU
  TABLEAU » avec un rappel très court de l'idée.
- **Les exercices.** Le diaporama y renvoie : valeurs extrêmes
  (exercices 5.5 et 5.10) dans « Les limites de la méthode », liste
  complète en conclusion.

## Numérotation

Les numéros (définitions, théorèmes, figures, tableaux, programmes,
exercices) sont ceux du livre au moment de la création de ce diaporama
(novembre 2026), après l'ajout des exercices 5.5 et 5.10 et de la
question 5.3 e). Les propositions et les théorèmes partagent le même
compteur (proposition 5.1, théorème 5.2, proposition 5.3, théorème 5.4).
Il n'y a pas de synchronisation automatique.
