@echo off
REM RunSetKodiWindow_min.bat — minimal, non-intrusive wrapper to call the PowerShell script
REM Usage: RunSetKodiWindow_min.bat WIDTH HEIGHT X Y DURATION
set WIDTH=%1
set HEIGHT=%2
set X=%3
set Y=%4
set DURATION=%5
if "%WIDTH%"=="" set WIDTH=1680
if "%HEIGHT%"=="" set HEIGHT=720
if "%X%"=="" set X=50
if "%Y%"=="" set Y=50
if "%DURATION%"=="" set DURATION=5

start "SetKodiWindow" /min powershell.exe -ExecutionPolicy Bypass -File "%~dp0SetKodiWindow.ps1" -Width %WIDTH% -Height %HEIGHT% -X %X% -Y %Y% -DurationSeconds %DURATION%
exit /b 0
