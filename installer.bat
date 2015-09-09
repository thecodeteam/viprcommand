@echo off
echo Installing...
set path=%path%;%cd%
cd ViPRCommand/bin
SETX PATH "%cd;%" 
echo.
echo done...
pause