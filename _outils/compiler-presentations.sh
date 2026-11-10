#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════
#  compiler-presentations.sh — compile les diaporamas Beamer et les
#  fichiers du laboratoire LaTeX, puis les copie là où le site du livre
#  les publie (par défaut _book/presentations/).
#
#  Usage :   _outils/compiler-presentations.sh [dossier-de-destination]
#
#  À lancer APRÈS « quarto render », qui recrée _book/.
#  Le site du cours (dépôt MAT-2901) renvoie à ces fichiers :
#    presentations/chapitre1.pdf … chapitre4.pdf
#    presentations/laboratoire-latex.pdf
#    presentations/labo-latex/01-minimal.tex, 02-activite.tex, 03-examen.tex
# ═══════════════════════════════════════════════════════════════════════
set -euo pipefail

racine="$(cd "$(dirname "$0")/.." && pwd)"
dest="${1:-$racine/_book/presentations}"
mkdir -p "$dest/labo-latex"

# Deux passages : le sommaire (\tableofcontents) et le total des pages.
deux_passages() {   # $1 = compilateur, $2 = fichier .tex
  "$1" -interaction=nonstopmode -halt-on-error "$2" > /dev/null \
    || { echo "Échec de $1 sur $(pwd)/$2 :"; tail -n 30 "${2%.tex}.log"; exit 1; }
  "$1" -interaction=nonstopmode -halt-on-error "$2" > /dev/null
}

# ── Les diaporamas des chapitres (lualatex) ──────────────────────────────
for chapitre in "$racine"/Beamer/chapitre*/; do
  nom="$(basename "$chapitre")"
  echo "→ $nom"
  ( cd "$chapitre" && deux_passages lualatex main.tex )
  cp "$chapitre/main.pdf" "$dest/$nom.pdf"
done

# ── Le laboratoire LaTeX ──────────────────────────────────────────────────
labo="$racine/Beamer/Activité LaTeX"
echo "→ laboratoire LaTeX : exemples (pdflatex, comme sur Overleaf)"
(
  cd "$labo/exemples"
  for f in 01-minimal 02-activite 03-examen; do
    deux_passages pdflatex "$f.tex"
  done
  # Le corrigé : le même examen avec \printanswers activé.
  sed 's/^% \\printanswers/\\printanswers/' 03-examen.tex > 03-examen-corrige.tex
  deux_passages pdflatex 03-examen-corrige.tex
  rm -f 03-examen-corrige.tex
)
echo "→ laboratoire LaTeX : diaporama (lualatex)"
( cd "$labo" && deux_passages lualatex main.tex )
cp "$labo/main.pdf" "$dest/laboratoire-latex.pdf"
cp "$labo"/exemples/0*.tex "$dest/labo-latex/"

echo "Présentations copiées dans $dest"
