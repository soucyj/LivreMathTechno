# Diaporama --- Chapitre 1 : Les transformations du plan

Diaporama Beamer pour un exposé magistral (visé : ~4-5 heures, avec
démonstrations au tableau) reprenant le contenu du chapitre 1 des notes
de cours (*Livre.tex*) : définitions, propositions/théorèmes (énoncés
seulement), exemples, figures et tableaux.

Ce dossier est **autonome** : aucun fichier n'est partagé avec le reste
du projet (`Livre.tex`, `livrejs.cls`, `commandesJS.sty`). Toutes les
couleurs, tous les raccourcis mathématiques (`\mat`, `\col`, `\Aire`,
`\dete`, `\Transf`, `\Aff`, etc.) et tous les styles TikZ des figures
sont redéfinis dans `preambule.tex`, à l'identique de ceux du livre.
Seules les images bitmap (`felix-klein.jpg`) sont réutilisées depuis
`../figures/`.

## Compiler

```
cd chapitre1
lualatex main.tex        # deux passages, pour le sommaire (\tableofcontents)
lualatex main.tex
```

`lualatex` est requis (comme pour `Livre.tex`) : la classe utilise
`fontspec`/`unicode-math`. Aucune bibliographie, aucune étape `biber`
n'est nécessaire.

## Structure

```
chapitre1/
├── main.tex              fichier principal : préambule + page titre + \input des sections
├── preambule.tex         couleurs, thème beamer, raccourcis maths, styles TikZ, boîtes d'énoncés
├── sections/
│   ├── 00-pourquoi.tex               §1.1 Motivation, note historique (Erlangen)
│   ├── 01-definition-transfo.tex     §1.2 Définition, exemples/contre-exemples
│   ├── 02-composition-groupe.tex     §1.3 Composition, (T,∘), hiérarchie de Klein
│   ├── 03-affines.tex                §1.4-1.5 Applications affines, propriétés, carré unité
│   ├── 04-catalogue.tex              §1.6 Translations…décomposition
│   ├── 05-homogenes.tex              §1.7 Coordonnées homogènes
│   ├── 06-similitudes-isometries.tex §1.8 Similitudes, classification, réflexions
│   ├── 07-bulldozer.tex              §1.9 Déterminer une transformation à partir de points
│   ├── 08-secondaire.tex             §1.10 Transformations et enseignement secondaire
│   └── 09-conclusion.tex             Synthèse, suites (exercices, annexe Python)
└── README.md             ce fichier
```

## Ce qui a été volontairement omis

- **Les démonstrations.** Chaque résultat qui, dans les notes, porte une
  démonstration est marqué d'un encadré rouge **« DÉMONSTRATION AU
  TABLEAU »** avec un rappel très court (1 à 3 lignes) de l'idée ou de
  la technique employée --- à l'intention de la personne qui présente,
  qui fera la démonstration à la craie. Le détail complet reste dans
  les notes de cours.
- **Les exercices.** Ils ne sont pas repris ici ; le diaporama y renvoie
  en conclusion (« Et maintenant »).
- **L'annexe Python** et le chapitre des solutions : hors du chapitre 1
  proprement dit.

## Numérotation

Les numéros (Définition 1.3, Proposition 1.10, Figure 1.6, etc.) sont
ceux du chapitre 1 de *Livre.pdf* au moment de la création de ce
diaporama. Si le chapitre est révisé par la suite (résultat ajouté,
retiré ou renuméroté), ces numéros peuvent se désynchroniser : il n'y a
pas de mécanisme automatique de synchronisation entre les deux
documents.
