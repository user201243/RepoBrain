@echo off
setlocal
title RepoBrain Report

cd /d "%~dp0"
set "PYTHONPATH=%CD%\src"

if exist "venv\Scripts\python.exe" (
  set "PYEXE=venv\Scripts\python.exe"
) else if exist ".venv\Scripts\python.exe" (
  set "PYEXE=.venv\Scripts\python.exe"
) else (
  set "PYEXE=python"
)

if not exist "repobrain.toml" (
  echo Initializing RepoBrain workspace...
  "%PYEXE%" -m repobrain.cli init --repo . --format text
  if errorlevel 1 goto error
)

if not exist ".repobrain\metadata.db" (
  echo Indexing repository for the first report...
  "%PYEXE%" -m repobrain.cli index --repo . --format text
  if errorlevel 1 goto error
)

"%PYEXE%" -m repobrain.cli report --repo . --format text
if errorlevel 1 goto error

if exist ".repobrain\report.html" (
  echo Opening .repobrain\report.html ...
  start "" ".repobrain\report.html"
)
goto end

:error
echo RepoBrain report could not open. Check that Python 3.12+ is installed, then see docs\install.md.

:end
pause
