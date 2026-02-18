#!/bin/bash

echo "Starting eConsolidated Mark Schedule System..."
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3.8+ and try again."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing/updating dependencies..."
pip install -r requirements.txt

# Run the application
echo
echo "==============================================="
echo "   eConsolidated Mark Schedule System"
echo "   Starting server at http://127.0.0.1:5000"
echo "   Default login: admin / admin123"
echo "==============================================="
echo
python app.py