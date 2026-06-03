@echo off
title FINDexplorER — Compilation Python 3.12
color 0A
cd /d "%~dp0"
if exist build_log.txt del build_log.txt

echo. >> build_log.txt
echo === FINDexplorER build.bat === >> build_log.txt
echo. >> build_log.txt

echo.
echo  FINDexplorER - Compilation Python 3.12
echo.

:: ── Trouver Python 3.12 ─────────────────────────────────────────────────────
echo [1/4] Recherche de Python 3.12... >> build_log.txt
echo [1/4] Recherche de Python 3.12...

set PY312=

py -3.12 --version >> build_log.txt 2>&1
if not errorlevel 1 ( set "PY312=py -3.12" & goto found )

for %%P in (
  "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
  "%LOCALAPPDATA%\Programs\Python\Python312-64\python.exe"
  "%USERPROFILE%\AppData\Local\Programs\Python\Python312\python.exe"
  "C:\Python312\python.exe"
  "C:\Program Files\Python312\python.exe"
) do ( if exist %%~P if not defined PY312 set "PY312=%%~P" )
if defined PY312 goto found

for /f "usebackq tokens=2*" %%A in (`reg query "HKCU\Software\Python\PythonCore\3.12\InstallPath" /ve 2^>nul`) do set "PY312=%%B\python.exe"
if defined PY312 if exist "%PY312%" goto found

for /f "usebackq tokens=2*" %%A in (`reg query "HKLM\SOFTWARE\Python\PythonCore\3.12\InstallPath" /ve 2^>nul`) do set "PY312=%%B\python.exe"
if defined PY312 if exist "%PY312%" goto found

for /f "usebackq tokens=2*" %%A in (`reg query "HKLM\SOFTWARE\WOW6432Node\Python\PythonCore\3.12\InstallPath" /ve 2^>nul`) do set "PY312=%%B\python.exe"
if defined PY312 if exist "%PY312%" goto found

for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python312*") do (
  if exist "%%D\python.exe" set "PY312=%%D\python.exe"
)
if defined PY312 goto found

echo Python 3.12 INTROUVABLE >> build_log.txt
echo.
echo  ERREUR : Python 3.12 introuvable.
echo  Verifiez l'installation puis relancez.
echo  Detail dans build_log.txt
echo.
pause
exit /b 1

:found
echo   Trouve : %PY312% >> build_log.txt
echo   Trouve : %PY312%
%PY312% --version >> build_log.txt 2>&1
echo.

:: ── Dependances ─────────────────────────────────────────────────────────────
echo [2/4] Installation des dependances... >> build_log.txt
echo [2/4] Installation des dependances...

%PY312% -m pip install --upgrade pip >> build_log.txt 2>&1
%PY312% -m pip install pyinstaller pystray pillow customtkinter >> build_log.txt 2>&1
set PIPERR=%errorlevel%
echo pip errorlevel=%PIPERR% >> build_log.txt

if not "%PIPERR%"=="0" (
  echo ERREUR pip - voir build_log.txt >> build_log.txt
  echo.
  echo  ERREUR pip. Contenu de build_log.txt :
  echo.
  type build_log.txt
  echo.
  pause
  exit /b 1
)
echo   OK. >> build_log.txt
echo   OK.
echo.

:: ── Compilation ─────────────────────────────────────────────────────────────
echo [3/4] Compilation... >> build_log.txt
echo [3/4] Compilation en cours (1-2 minutes)...
echo.

%PY312% -m PyInstaller --onefile --noconsole --name "FINDexplorER" --icon "FindExplorer.ico" --add-data "FindExplorer.ico;." --hidden-import "pystray" --hidden-import "pystray._win32" --collect-all "pystray" --hidden-import "PIL" --hidden-import "PIL.Image" --hidden-import "PIL.ImageDraw" --collect-all "PIL" --hidden-import "customtkinter" --collect-all "customtkinter" --hidden-import "fe_ui" --hidden-import "fe_backend" --hidden-import "fe_quickaccess" main.py >> build_log.txt 2>&1
set BUILDERR=%errorlevel%
echo PyInstaller errorlevel=%BUILDERR% >> build_log.txt

if not "%BUILDERR%"=="0" (
  echo.
  echo  ERREUR compilation. Dernieres lignes du log :
  echo.
  type build_log.txt
  echo.
  pause
  exit /b 1
)

:: ── Resultat ─────────────────────────────────────────────────────────────────
echo [4/4] Finalisation... >> build_log.txt
echo [4/4] Finalisation...

if not exist "dist\FINDexplorER.exe" (
  echo dist\FINDexplorER.exe introuvable >> build_log.txt
  echo.
  echo  ERREUR : exe introuvable. Voir build_log.txt
  echo.
  type build_log.txt
  pause
  exit /b 1
)

copy "dist\FINDexplorER.exe" "FINDexplorER.exe" >nul
echo   Copie OK. >> build_log.txt

echo.
echo  ==============================================
echo   FINDexplorER.exe cree avec succes !
echo   Ctrl+Espace pour ouvrir depuis partout
echo  ==============================================
echo.

:: ── Lancement optionnel ───────────────────────────────────────────────────────
:: Note : --onefile extrait ses fichiers dans %%TEMP%% au premier lancement,
:: ce qui prend quelques secondes. On utilise "choice" plutot que "set /p"
:: pour eviter les problemes de lecture de variable en fin de script.
echo  Lancer FINDexplorER maintenant ?
choice /c ON /n /m "  [O] Oui   [N] Non  : "
if errorlevel 2 goto fin
if errorlevel 1 (
  echo.
  echo  Lancement en cours (premiere extraction ~5s)...
  start "" "%~dp0FINDexplorER.exe"
)

:fin
echo.
echo  Log complet dans build_log.txt
pause
