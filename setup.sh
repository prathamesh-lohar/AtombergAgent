#!/bin/bash

echo "========================================"
echo "Atomberg Agent - Installation Script"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed."
    echo "Please install Python 3.8+ first:"
    echo "  macOS: brew install python3"
    echo "  Ubuntu/Debian: sudo apt-get install python3 python3-pip python3-venv"
    echo "  Fedora: sudo dnf install python3 python3-pip"
    exit 1
fi

echo "Python version:"
python3 --version
echo ""

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv .venv

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo ""
echo "Installing required packages..."
pip install -r requirements.txt

echo ""
echo "========================================"
echo "Installation Complete!"
echo "========================================"
echo ""
echo "IMPORTANT: Before running the agent:"
echo "1. Create a .env file with your API key:"
echo "   api=YOUR_GOOGLE_API_KEY_HERE"
echo ""
echo "2. Make sure Google Chrome is installed:"
echo "   macOS: https://www.google.com/chrome/"
echo "   Linux: sudo apt-get install google-chrome-stable"
echo ""
echo "To run the agent:"
echo "   source .venv/bin/activate"
echo "   python agent.py"
echo ""