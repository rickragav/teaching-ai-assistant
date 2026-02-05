#!/bin/bash

# Activate virtual environment and start the server
cd "$(dirname "$0")"

echo "🚀 Starting UdemyGPT Backend Server..."
echo ""

# Activate virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found at .venv"
    echo "Please create it with: python3 -m venv .venv"
    exit 1
fi

# Start the server
echo "🌐 Starting FastAPI server on http://localhost:8000"
echo ""
python -m src.api.main
