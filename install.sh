#!/bin/bash

echo "Setting up the environment..."

# create and activate the virtual environment
python3 -m venv .venv
if [ $? -ne 0 ]; then
    echo "Failed to create virtual environment."
    exit 1
fi

source .venv/bin/activate

# install dependencies
echo "Installing requirements..."
pip install -r requirements.txt --verbose
if [ $? -eq 0 ]; then
    echo "Dependencies installed successfully."
else
    echo "Failed to install dependencies."
    deactivate
    exit 1
fi

# deactivate the virtual environment
deactivate

echo "Environment setup complete."
