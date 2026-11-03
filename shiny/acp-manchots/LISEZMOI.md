# À la recherche du meilleur plan — ACP des manchots (Shiny pour Python)

Application interactive pour la section « Les manchots de l'archipel Palmer »
du chapitre 5 (`05-acp.qmd`).

- À gauche : le nuage des 342 manchots (cotes z) en 3D, que l'on fait tourner
  à la souris. Le plan de projection est le plan de l'écran : tourner le
  nuage, c'est choisir un plan. On peut aussi figer le plan pour le voir
  dans le nuage, et afficher les vecteurs propres v₁, v₂, v₃.
- À droite : la projection (l'« ombre ») du nuage sur ce plan, mise à plat,
  qui suit la rotation en direct.
- En haut, une barre affiche la part de la variance conservée par le plan
  (92,3 % au mieux, pour v₁ et v₂ ; 33,2 % au pire, pour v₂ et v₃).
- Raccourcis : les trois plans de vecteurs propres et les trois plans de
  coordonnées ; la caméra pivote pour se placer face au plan choisi.

## Lancer

```bash
pip install -r requirements.txt
shiny run --reload app.py      # puis ouvrir http://127.0.0.1:8000
```

Plotly et MathJax sont chargés depuis un CDN : une connexion Internet est nécessaire.

## Fichiers

| Fichier | Rôle |
|---|---|
| `app.py` | données, calculs (réduction, matrice R, vecteurs propres, variance conservée), interface, textes |
| `graphiques.js` | dessin des deux graphiques (Plotly), lecture de la caméra (plan de l'écran), animation |
| `style.css` | mise en page, couleurs du livre |
| `manchots.csv` | copie de `figures/acp/manchots.csv` |

## Version intégrée au livre (shinylive)

Dans le site web, l'application tourne entièrement dans le navigateur (Python
compilé en WebAssembly) : aucun serveur n'est nécessaire. Elle est insérée dans
`05-acp.qmd`, après l'interprétation des axes principaux des manchots.

Après toute modification de l'application :

```bash
cd Quarto/shiny
./exporter.sh          # écrit Quarto/applications/ (environ 42 Mo)
cd .. && quarto render # copie applications/ dans _book/
```

Le site doit être servi par un serveur web (`quarto preview`, GitHub Pages,
etc.) : l'application ne fonctionne pas en ouvrant le fichier HTML directement
depuis le disque.
