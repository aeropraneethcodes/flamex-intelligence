@echo off
setlocal
cd /d "%~dp0"
echo.
echo ============================================
echo  FlameX Intelligence - Team Dynamic Duo
echo ============================================
echo.
where py >nul 2>nul
if not errorlevel 1 (
  set PY=py
) else (
  where python >nul 2>nul
  if errorlevel 1 (
    echo Python not found. Install Python 3.10 or newer, then rerun this file.
    pause
    exit /b 1
  )
  set PY=python
)
if not exist .venv\Scripts\python.exe (
  echo Creating local Python environment...
  %PY% -m venv .venv
  if errorlevel 1 goto failed
)
echo Installing / verifying dependencies...
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto failed
echo Launching http://localhost:8501
.venv\Scripts\python.exe -m streamlit run app.py
if errorlevel 1 goto failed
exit /b 0
:failed
echo.
echo There was a setup or startup error. Check Python and your Internet connection.
pause
exit /b 1
