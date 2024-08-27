@echo off
setlocal

:: get installed Python version
for /f "tokens=2 delims= " %%i in ('python --version') do set PYTHON_VERSION=%%i

:: check if the installed Python version is 3.12
echo %PYTHON_VERSION% | findstr /r /c:"^3\.12" >nul
if %ERRORLEVEL% NEQ 0 (
    echo Python 3.12 is required. Please install Python 3.12.
    exit /b 1
)

:: create and activate virtual environment
python -m venv .venv
call .venv\Scripts\activate

:: install dependencies
echo Installing requirements...
pip install -r requirements.txt --verbose
if %ERRORLEVEL% EQU 0 (
    echo Dependencies installed successfully.
) else (
    echo Failed to install dependencies.
    exit /b 1
)

:: deactivate the virtual environment
deactivate

endlocal
