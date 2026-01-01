@echo off
setlocal

cd /d "%~dp0"

REM 
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 tss_fireworks.py
  goto :done
)

REM 
where python >nul 2>nul
if %errorlevel%==0 (
  python tss_fireworks.py
  goto :done
)

echo.
echo Python is not installed or not on PATH.
echo Install it from https://www.python.org/downloads/windows/
echo (Make sure to tick "Add Python to PATH")
echo.
pause

:done
endlocal
