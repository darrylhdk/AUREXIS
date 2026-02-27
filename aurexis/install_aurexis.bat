@echo off
chcp 65001 >nul
title AUREXIS - Installation

echo.
echo  ██████╗ ██╗   ██╗██████╗ ███████╗██╗  ██╗██╗███████╗
echo  ██╔══██╗██║   ██║██╔══██╗██╔════╝╚██╗██╔╝██║██╔════╝
echo  ███████║██║   ██║██████╔╝█████╗   ╚███╔╝ ██║███████╗
echo  ██╔══██║██║   ██║██╔══██╗██╔══╝   ██╔██╗ ██║╚════██║
echo  ██║  ██║╚██████╔╝██║  ██║███████╗██╔╝ ██╗██║███████║
echo.
echo  Universal AI Agent OS - Installation Windows
echo  ================================================
echo.

:: ── Vérification Python ──────────────────────────────────────
echo [1/5] Verification de Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo  ERREUR : Python n'est pas installe !
    echo.
    echo  Telecharge Python sur : https://www.python.org/downloads/
    echo  IMPORTANT : Coche "Add Python to PATH" lors de l'installation !
    echo.
    start https://www.python.org/downloads/
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do echo   OK %%i

:: ── Vérification Git ─────────────────────────────────────────
echo.
echo [2/5] Verification de Git...
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo   Git non trouve. Ouverture de la page de telechargement...
    start https://git-scm.com/download/win
    echo   Installe Git puis relance ce fichier .bat
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('git --version') do echo   OK %%i

:: ── Clonage ──────────────────────────────────────────────────
echo.
echo [3/5] Telechargement d'AUREXIS depuis GitHub...
set INSTALL_DIR=%USERPROFILE%\AUREXIS
if exist "%INSTALL_DIR%" (
    echo   Dossier existant trouve, mise a jour...
    cd /d "%INSTALL_DIR%"
    git pull origin main
) else (
    git clone https://github.com/darrylhdk/AUREXIS.git "%INSTALL_DIR%"
    cd /d "%INSTALL_DIR%"
)
echo   OK Projet telecharge dans %INSTALL_DIR%

:: ── Dépendances ───────────────────────────────────────────────
echo.
echo [4/5] Installation des dependances (2-5 minutes)...
pip install -r requirements.txt --quiet
echo   OK Dependances installees

:: ── Setup ────────────────────────────────────────────────────
echo.
echo [5/5] Configuration d'AUREXIS...
if not exist "config\config.json" (
    echo   Creation du profil...
    python install.py
) else (
    echo   Profil existant detecte.
)

:: ── Raccourci bureau ─────────────────────────────────────────
echo.
echo Creation du raccourci bureau...
set SHORTCUT=%USERPROFILE%\Desktop\AUREXIS.bat
echo @echo off > "%SHORTCUT%"
echo cd /d "%INSTALL_DIR%" >> "%SHORTCUT%"
echo title AUREXIS Agent OS >> "%SHORTCUT%"
echo python main.py >> "%SHORTCUT%"
echo   OK Raccourci cree sur le bureau

:: ── Fin ──────────────────────────────────────────────────────
echo.
echo ====================================================
echo   AUREXIS installe avec succes !
echo ====================================================
echo.
echo   Pour lancer AUREXIS :
echo   - Double-clique sur AUREXIS sur ton bureau
echo   - OU tape : cd %INSTALL_DIR% puis python main.py
echo.
echo   Interface web : http://localhost:8000
echo.
set /p LAUNCH="Lancer AUREXIS maintenant ? (O/n) : "
if /i "%LAUNCH%" neq "n" (
    echo Lancement...
    start "" cmd /k "cd /d %INSTALL_DIR% && python main.py"
    timeout /t 3 >nul
    start http://localhost:8000
)
