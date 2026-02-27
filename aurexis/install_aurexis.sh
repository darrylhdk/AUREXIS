#!/bin/bash
# AUREXIS — Installateur Mac/Linux
set -e

REPO="https://github.com/darrylhdk/AUREXIS.git"
INSTALL_DIR="$HOME/AUREXIS"

echo ""
echo " █████╗ ██╗   ██╗██████╗ ███████╗██╗  ██╗██╗███████╗"
echo "██╔══██╗██║   ██║██╔══██╗██╔════╝╚██╗██╔╝██║██╔════╝"
echo "███████║██║   ██║██████╔╝█████╗   ╚███╔╝ ██║███████╗"
echo "██╔══██║██║   ██║██╔══██╗██╔══╝   ██╔██╗ ██║╚════██║"
echo "██║  ██║╚██████╔╝██║  ██║███████╗██╔╝ ██╗██║███████║"
echo ""
echo "Universal AI Agent OS — Installation"
echo "======================================"

# Python
echo "[1/4] Vérification Python..."
if ! command -v python3 &>/dev/null; then
    echo "Python3 non trouvé. Installe-le depuis python.org"
    exit 1
fi
echo "  ✓ $(python3 --version)"

# Git
echo "[2/4] Vérification Git..."
if ! command -v git &>/dev/null; then
    echo "Installation Git..."
    sudo apt-get install git -y 2>/dev/null || brew install git 2>/dev/null
fi
echo "  ✓ $(git --version)"

# Clone
echo "[3/4] Téléchargement AUREXIS..."
if [ -d "$INSTALL_DIR" ]; then
    cd "$INSTALL_DIR" && git pull origin main
else
    git clone "$REPO" "$INSTALL_DIR" && cd "$INSTALL_DIR"
fi
cd "$INSTALL_DIR"
echo "  ✓ Installé dans $INSTALL_DIR"

# Deps
echo "[4/4] Installation dépendances..."
pip3 install -r requirements.txt --quiet
echo "  ✓ Dépendances OK"

# Setup
if [ ! -f "config/config.json" ]; then
    python3 install.py
fi

echo ""
echo "╔══════════════════════════════════╗"
echo "║  AUREXIS installé !              ║"
echo "║  Lancement sur localhost:8000    ║"
echo "╚══════════════════════════════════╝"
echo ""
echo "Pour relancer : cd ~/AUREXIS && python3 main.py"
echo ""

read -p "Lancer maintenant ? (O/n) " LAUNCH
if [ "$LAUNCH" != "n" ] && [ "$LAUNCH" != "N" ]; then
    python3 main.py &
    sleep 2
    open "http://localhost:8000" 2>/dev/null || xdg-open "http://localhost:8000" 2>/dev/null || echo "Ouvre http://localhost:8000 dans ton navigateur"
fi
