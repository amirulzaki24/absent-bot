#!/bin/bash

# Check if Python is installed
if ! command -v python3 &>/dev/null; then
    echo "Python not installed, please install Python before retrying."
    echo "Please refer to./Python-setup.md to install Python."
    exit 1
else
    echo "Python is already installed, version: $(python3 --version)"
fi

# Check if pip is installed
if ! command -v pip3 &>/dev/null; then
    echo "pip not installed, starting pip installation..."
    python3 -m ensurepip --upgrade
    if ! command -v pip3 &>/dev/null; then
        echo "pip installation failed, please check the issue."
        exit 1
    fi
else
    echo "pip is already installed, version: $(pip3 --version)"
fi

# Install project dependencies
if [ -f "requirements.txt" ]; then
    echo "Installing project dependencies..."
    pip3 install -r requirements.txt
else
    echo "No requirements.txt file found, skipping dependency installation."
fi

# Start the project
echo "Starting the project..."
python3 main.py

