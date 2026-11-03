# Mathématiques et technologie

*Des notions du secondaire aux applications modernes*

Jérôme Soucy — Université Laval, Département de mathématiques et de statistique

Ce livre montre comment des notions vues au secondaire (géométrie,
fonctions, vecteurs, probabilités, statistique) mènent à des technologies
d'aujourd'hui : images numériques, distances et fractales, moteurs de
recherche, analyse de données, cryptographie. Il a été écrit pour le cours
*MAT-2901 : Mathématiques et technologie*, destiné aux futurs enseignants de
mathématiques au secondaire.

| Chapitre | Sujet |
|---|---|
| 1 | Les transformations du plan |
| 2 | Espaces métriques |
| 3 | Fractales et systèmes itératifs de fonctions |
| 4 | Les chaînes de Markov et l'algorithme PageRank de Google |
| 5 | L'analyse en composantes principales (avec une application interactive) |
| à venir | Cryptographie |

## Construire le livre

Le livre est écrit en Markdown ([Quarto](https://quarto.org)) ; une seule
source produit le site web et le PDF.

```bash
quarto preview              # aperçu du site, mis à jour en direct
quarto render               # site web et PDF dans _book/
```

Il faut Quarto, une distribution TeX récente (LuaLaTeX, biber, pgfplots) et
Python 3 avec `numpy`. Les détails (conventions d'écriture, figures TikZ,
filtres) sont dans [LISEZMOI.md](LISEZMOI.md).

## Publier le site avec GitHub Pages

Le workflow GitHub Actions de `.github/workflows/publish.yml` exporte
l'application interactive, rend le site et le PDF, puis publie `_book/` sur
GitHub Pages à chaque poussée sur `main`. Après avoir créé le dépôt
[`soucyj/LivreMathTechno`](https://github.com/soucyj/LivreMathTechno) et
poussé les sources sur cette branche, choisir **Settings > Pages > Build and
deployment > Source > GitHub Actions**. Le site sera alors disponible à
<https://soucyj.github.io/LivreMathTechno/>.

L'application interactive du chapitre 5 (Shiny pour Python, exécutée dans le
navigateur grâce à shinylive) se trouve dans `shiny/acp-manchots/`. Pour
l'intégrer au site, il faut l'exporter avant le rendu :

```bash
cd shiny/acp-manchots
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt shinylive
cd .. && ./exporter.sh
```

## Licence

[![CC BY 4.0](https://licensebuttons.net/l/by/4.0/88x31.png)](https://creativecommons.org/licenses/by/4.0/deed.fr)

© 2026 Jérôme Soucy.

- **Texte et figures** : licence [Creative Commons Attribution 4.0
  International](https://creativecommons.org/licenses/by/4.0/deed.fr)
  (CC BY 4.0), voir [LICENSE](LICENSE). Vous pouvez copier, redistribuer,
  modifier et adapter ce livre, pour tout usage, à condition de citer
  l'auteur, d'indiquer les modifications apportées et de fournir un lien
  vers la licence.
- **Code** (programmes Python, filtres Lua, application Shiny) : licence
  MIT, voir [LICENSE-CODE](LICENSE-CODE).
- **Portraits et jeux de données** : ils conservent leur licence d'origine ;
  leur source est indiquée dans le livre (données des manchots : Horst,
  Hill et Gorman, *palmerpenguins*, CC0 ; données du décathlon : Husson, Lê et
  Pagès, paquet R *FactoMineR*).

Pour citer : Jérôme Soucy, *Mathématiques et technologie : des notions du
secondaire aux applications modernes*, 2026.
