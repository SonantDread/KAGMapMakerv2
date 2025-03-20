@echo off

@REM check if .venv folder exists
if exist .venv (
    echo Activating virtual environment...
    @REM activate the virtual environment
    call .venv\Scripts\activate
    if errorlevel 1 (
        echo Failed to activate virtual environment.
        PAUSE
        exit /b 1
    )
) else (
    echo No .venv folder found. Running install.bat to set up the environment...
    REM run the install.bat file to create the virtual environment
    call install.bat

    REM check again if the .venv folder was created
    if exist .venv (
        echo .venv folder created successfully. Activating virtual environment...
        call .venv\Scripts\activate
        if errorlevel 1 (
            echo Failed to activate virtual environment after running install.bat.
            PAUSE
            exit /b 1
        )
    ) else (
        echo .venv folder was not created. Please check install.bat for errors.
        PAUSE
        exit /b 1
    )
)

REM run the application
python app.py

PAUSE
