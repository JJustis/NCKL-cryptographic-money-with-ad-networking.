@echo off
setlocal
title Nickles Setup
cd /d "%~dp0"

rem ---- 1. Python -------------------------------------------------------------
set "PY="
where py >nul 2>&1 && set "PY=py -3"
if not defined PY where python >nul 2>&1 && set "PY=python"
if not defined PY goto nopython
%PY% -c "import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)" >nul 2>&1
if errorlevel 1 goto nopython
goto havepython

:nopython
echo Python 3.9 or newer was not found on this PC.
where winget >nul 2>&1
if errorlevel 1 (
    echo Please install Python from https://www.python.org/downloads/ ^(tick "Add python.exe to PATH"^) and run setup.bat again.
    pause
    exit /b 1
)
choice /c YN /m "Install Python 3.12 now with Windows' winget"
if errorlevel 2 (
    echo Setup cannot continue without Python.
    pause
    exit /b 1
)
winget install --id Python.Python.3.12 -e --silent --accept-package-agreements --accept-source-agreements
echo.
echo Python is installed. Please close this window and run setup.bat again so Windows finds it.
pause
exit /b 0

:havepython
rem ---- 2. packages ------------------------------------------------------------
echo Installing the Python packages the wallet needs...
%PY% -m pip install -q -r requirements.txt
if errorlevel 1 (
    echo.
    echo [ERROR] The Python packages could not be installed. Check your internet connection and try again.
    pause
    exit /b 1
)

rem ---- 3. the wizard ------------------------------------------------------------
%PY% setup_wizard.py %*
if errorlevel 1 (
    echo.
    echo The wizard stopped. See the message above.
    pause
    exit /b 1
)
endlocal
