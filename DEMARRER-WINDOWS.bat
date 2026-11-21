@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  py -m venv .venv
  if errorlevel 1 goto error
)
".venv\Scripts\python.exe" -m pip install -r requirements-dev.txt
if errorlevel 1 goto error
".venv\Scripts\python.exe" run.py
if errorlevel 1 goto error
exit /b 0
:error
echo.
echo Une erreur est survenue. Consultez les messages ci-dessus.
pause
exit /b 1
