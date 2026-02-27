# ============================================================
#  AUREXIS — Installateur automatique Windows
#  Usage : iwr -useb https://raw.githubusercontent.com/TON_USERNAME/aurexis/main/install_aurexis.ps1 | iex
# ============================================================

$ErrorActionPreference = "Stop"
$REPO = "https://github.com/darrylhdk/AUREXIS"
$INSTALL_DIR = "$env:USERPROFILE\AUREXIS"

function Write-Color($text, $color="Cyan") {
    Write-Host $text -ForegroundColor $color
}

function Write-Step($step, $text) {
    Write-Host ""
    Write-Host "[$step] " -ForegroundColor Yellow -NoNewline
    Write-Host $text -ForegroundColor White
}

Clear-Host
Write-Host ""
Write-Host " █████╗ ██╗   ██╗██████╗ ███████╗██╗  ██╗██╗███████╗" -ForegroundColor Cyan
Write-Host "██╔══██╗██║   ██║██╔══██╗██╔════╝╚██╗██╔╝██║██╔════╝" -ForegroundColor Cyan
Write-Host "███████║██║   ██║██████╔╝█████╗   ╚███╔╝ ██║███████╗" -ForegroundColor Cyan
Write-Host "██╔══██║██║   ██║██╔══██╗██╔══╝   ██╔██╗ ██║╚════██║" -ForegroundColor Cyan
Write-Host "██║  ██║╚██████╔╝██║  ██║███████╗██╔╝ ██╗██║███████║" -ForegroundColor Cyan
Write-Host "╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝╚══════╝" -ForegroundColor Cyan
Write-Host "         Universal AI Agent OS - Installation" -ForegroundColor DarkCyan
Write-Host ""

# ── Vérification Python ──────────────────────────────────────
Write-Step "1/5" "Vérification de Python..."
try {
    $pyVersion = python --version 2>&1
    Write-Color "  ✓ $pyVersion trouvé" "Green"
} catch {
    Write-Color "  ✗ Python non trouvé !" "Red"
    Write-Host ""
    Write-Host "  Installe Python depuis : https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "  IMPORTANT : Coche 'Add Python to PATH' pendant l'installation !" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Puis relance ce script." -ForegroundColor Yellow
    Read-Host "Appuie sur Entrée pour fermer"
    exit 1
}

# ── Vérification Git ─────────────────────────────────────────
Write-Step "2/5" "Vérification de Git..."
try {
    $gitVersion = git --version 2>&1
    Write-Color "  ✓ $gitVersion trouvé" "Green"
} catch {
    Write-Color "  ✗ Git non trouvé. Installation en cours..." "Yellow"
    Write-Host "  Télécharge Git depuis : https://git-scm.com/download/win" -ForegroundColor Yellow
    Start-Process "https://git-scm.com/download/win"
    Read-Host "  Installe Git puis appuie sur Entrée pour continuer"
}

# ── Clonage du projet ────────────────────────────────────────
Write-Step "3/5" "Téléchargement d'AUREXIS..."
if (Test-Path $INSTALL_DIR) {
    Write-Color "  → Dossier existant trouvé, mise à jour..." "Yellow"
    Set-Location $INSTALL_DIR
    git pull origin main
} else {
    Write-Color "  → Clonage dans $INSTALL_DIR" "Cyan"
    git clone $REPO $INSTALL_DIR
    Set-Location $INSTALL_DIR
}
Write-Color "  ✓ Projet téléchargé" "Green"

# ── Installation des dépendances ─────────────────────────────
Write-Step "4/5" "Installation des dépendances Python..."
Write-Color "  (Cela peut prendre 2-5 minutes...)" "DarkGray"
pip install -r requirements.txt --quiet
Write-Color "  ✓ Dépendances installées" "Green"

# ── Setup AUREXIS ────────────────────────────────────────────
Write-Step "5/5" "Configuration d'AUREXIS..."
$configExists = Test-Path "config\config.json"
if (-not $configExists) {
    Write-Host ""
    Write-Host "  Création de ton profil AUREXIS..." -ForegroundColor Cyan
    python install.py
} else {
    Write-Color "  ✓ Profil existant détecté, on passe l'installation." "Green"
}

# ── Création du raccourci bureau ──────────────────────────────
Write-Host ""
Write-Color "  Création d'un raccourci sur le bureau..." "Cyan"
$desktop = [System.Environment]::GetFolderPath("Desktop")
$shortcutPath = "$desktop\AUREXIS.lnk"
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = "powershell.exe"
$shortcut.Arguments = "-NoExit -Command `"cd '$INSTALL_DIR'; python main.py`""
$shortcut.WorkingDirectory = $INSTALL_DIR
$shortcut.IconLocation = "powershell.exe"
$shortcut.Description = "Lancer AUREXIS Agent OS"
$shortcut.Save()
Write-Color "  ✓ Raccourci créé sur le bureau !" "Green"

# ── Lancement ────────────────────────────────────────────────
Write-Host ""
Write-Host "╔══════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║          AUREXIS installé avec succès !          ║" -ForegroundColor Green
Write-Host "╠══════════════════════════════════════════════════╣" -ForegroundColor Green
Write-Host "║                                                  ║" -ForegroundColor Green
Write-Host "║  Interface web : http://localhost:8000           ║" -ForegroundColor Green
Write-Host "║                                                  ║" -ForegroundColor Green
Write-Host "║  Pour relancer plus tard :                       ║" -ForegroundColor Green
Write-Host "║  → Double-clique sur 'AUREXIS' sur le bureau     ║" -ForegroundColor Green
Write-Host "║  → ou : cd $INSTALL_DIR && python main.py       ║" -ForegroundColor Green
Write-Host "║                                                  ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

$launch = Read-Host "Lancer AUREXIS maintenant ? (O/n)"
if ($launch -ne "n" -and $launch -ne "N") {
    Write-Color "Lancement d'AUREXIS..." "Cyan"
    Start-Process powershell -ArgumentList "-NoExit -Command `"cd '$INSTALL_DIR'; python main.py`""
    Start-Sleep -Seconds 3
    Start-Process "http://localhost:8000"
}
