#!/bin/zsh
# Exporte les applications Shiny en version shinylive (Python exécuté dans le
# navigateur, sans serveur) dans ../applications/, que Quarto copie ensuite
# dans _book/ (voir « resources » dans _quarto.yml).
#
# À relancer après chaque modification d'une application, puis : quarto render
#
#   ./exporter.sh                 → toutes les applications
#   ./exporter.sh acp-manchots    → une seule
#
# Il faut shinylive dans l'environnement de l'application :
#   acp-manchots/.venv/bin/python -m pip install shinylive
set -e
ICI=${0:A:h}
DEST=$ICI/../applications
SHINYLIVE=$ICI/acp-manchots/.venv/bin/shinylive

apps=("$@")
(( ${#apps} )) || apps=($(cd $ICI && ls -d */ | tr -d /))

for app in $apps; do
  echo "→ $app"
  $SHINYLIVE export $ICI/$app $DEST --subdir $app
done
echo "Terminé. Lancer « quarto render » (ou « quarto preview ») pour mettre le site à jour."
