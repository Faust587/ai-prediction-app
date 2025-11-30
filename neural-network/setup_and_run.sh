#!/bin/bash

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3.11 -m venv .venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv311/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Run the Python script
echo "Running the script..."
python3.11 index.py

# Deactivate virtual environment
deactivate 