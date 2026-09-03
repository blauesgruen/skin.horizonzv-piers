@echo off
REM Wrapper to run SetKodiWindow.ps1 with a visible console for debugging
REM Usage: RunSetKodiWindow_visible.bat 1680 720 50 50
set WIDTH=%1
set HEIGHT=%2
set X=%3
set Y=%4
if "%WIDTH%"=="" set WIDTH=1280
if "%HEIGHT%"=="" set HEIGHT=720
if "%X%"=="" set X=100
if "%Y%"=="" set Y=100
n
powershell.exe -ExecutionPolicy Bypass -NoExit -File "%~dp0SetKodiWindow.ps1" -Width %WIDTH% -Height %HEIGHT% -X %X% -Y %Y%
pause
