#!/bin/bash

# check if .venv folder exists
if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
    if [ $? -ne 0 ]; then
        echo "Failed to activate virtual environment."
        exit 1
    fi
else
    echo "No .venv folder found. Running install.sh to set up the environment..."
    # run the install.sh file to create the virtual environment
    bash install.sh

    # check again if the .venv folder was created
    if [ -d ".venv" ]; then
        echo ".venv folder created successfully. Activating virtual environment..."
        source .venv/bin/activate
        if [ $? -ne 0 ]; then
            echo "Failed to activate virtual environment after running install.sh."
            exit 1
        fi
    else
        echo ".venv folder was not created. Please check install.sh for errors."
        exit 1
    fi
fi

# run the application
python app.py
