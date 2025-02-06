echo Setting up the environment...
@echo off

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
    PAUSE
)

:: deactivate the virtual environment
deactivate

endlocal

echo "Environment setup complete."
