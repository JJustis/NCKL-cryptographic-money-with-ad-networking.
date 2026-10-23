@echo off
setlocal
title Nickles Ad Network
cd /d "%~dp0"

rem XAMPP root = three levels up (xampp\htdocs\livepy\pythoncoin); fall back to C:\xampp
set "XAMPP=%~dp0..\..\.."
if not exist "%XAMPP%\mysql\bin\mysqld.exe" set "XAMPP=C:\xampp"
if not exist "%XAMPP%\mysql\bin\mysqld.exe" (
    echo [ERROR] XAMPP not found. Edit the XAMPP line in run.bat.
    pause & exit /b 1
)

rem Python: prefer the py launcher, else python on PATH
set "PY=python"
where py >nul 2>&1 && set "PY=py -3"

echo [1/4] Installing Python packages...
%PY% -m pip install -q -r requirements.txt
if errorlevel 1 (
    echo [ERROR] pip install failed.
    pause & exit /b 1
)

echo [2/4] MySQL...
netstat -ano | findstr /r /c:":3306 .*LISTENING" >nul
if errorlevel 1 (
    start "MySQL" /min "%XAMPP%\mysql\bin\mysqld.exe" --defaults-file="%XAMPP%\mysql\bin\my.ini" --standalone
    timeout /t 5 /nobreak >nul
) else (
    echo      already running
)

echo [3/4] Apache (dashboard / api.php)...
netstat -ano | findstr /r /c:":80 .*LISTENING" >nul
if errorlevel 1 (
    start "Apache" /min "%XAMPP%\apache\bin\httpd.exe"
    timeout /t 2 /nobreak >nul
) else (
    echo      already running
)

echo [4/4] Starting Nickles wallet...
echo      Dashboard: http://localhost/livepy/pythoncoin/dashboard8.php
%PY% pyqt.py
echo.
echo Nickles exited with code %errorlevel%.
pause
