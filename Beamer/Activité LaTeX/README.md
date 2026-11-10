# Laboratoire informatique — Écrire des mathématiques avec LaTeX

Diaporama Beamer pour un laboratoire sur Overleaf, destiné à de futurs
enseignants de mathématiques, au secondaire ou au collégial (les
exemples portent sur le secondaire ; les prompts types prévoient les
deux ordres d'enseignement).
Objectif : comprendre la structure d'un document LaTeX (classe,
préambule, corps), compiler et corriger les erreurs, écrire des
mathématiques, travailler avec l'IA de façon critique, et produire
deux livrables : la présentation d'une activité (2 à 3 pages) et un
examen avec la classe `exam`.

## Contenu

```
Activité LaTeX/
├── main.tex, preambule.tex   le diaporama (même style que les chapitres)
├── sections/                 00-pourquoi … 09-conclusion
└── exemples/                 fichiers à distribuer aux étudiants
    ├── 01-minimal.tex        premier document commenté
    ├── 02-activite.tex       fiche d'activité (Pythagore et téléviseurs)
    ├── 03-examen.tex         examen avec la classe exam, en français
    └── *.pdf                 leurs rendus (03-examen-corrige.pdf :
                              le même fichier avec \printanswers)
```

## Compiler

- Le diaporama : `lualatex main.tex` (deux passages). Il inclut les PDF
  de `exemples/` : les recompiler d'abord s'ils sont modifiés.
- Les exemples : `pdflatex` (le compilateur par défaut d'Overleaf).

## Environnements définis dans preambule.tex

- `CodeTeX` : du code LaTeX seul (`[title={...}]` facultatif).
- `CodeRendu` : le code à gauche, son rendu réel à droite.
- `Prompt{titre}` : un prompt type pour l'IA ; `\champ{...}` marque une
  partie à personnaliser.
- `Exercice{titre}` : une tâche à faire en laboratoire.
- `AuTableau[Piège fréquent]`, `Rem{...}`, `Classe{...}` : repris des
  diaporamas des chapitres.

Ces environnements contenant du code exigent `\begin{frame}[fragile]`.

## Conventions

Pas de gras ni d'italique décoratifs ; virgule décimale avec `siunitx`
(`\num`, `\qty`) ; point-virgule entre composantes décimales d'un
vecteur. Les exemples respectent les mêmes règles. Exception : dans le
corrigé de l'examen, la classe `exam` met la bonne réponse d'un choix
multiple en gras (réglage par défaut).
