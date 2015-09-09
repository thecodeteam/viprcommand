@ECHO OFF
set PYFILE=%~f0
set PYFILE=%PYFILE:~0,-4%.py
"python.exe" "%PYFILE%" %*
