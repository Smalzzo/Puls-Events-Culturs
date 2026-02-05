#!/usr/bin/env bash
# Bootstrap script for Linux/Mac
# Sets up Python virtual environment and installs dependencies

set -e

echo "=== Bootstrap Puls Events Culturs RAG ==="

# Check Python version
PYTHON_CMD=""
for cmd in python3.12 python3.11 python3 python; do
    if command -v "$cmd" &> /dev/null; then
        VERSION=$("$cmd" --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
        MAJOR=$(echo "$VERSION" | cut -d. -f1)
        MINOR=$(echo "$VERSION" | cut -d. -f2)
        if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 11 ]; then
            PYTHON_CMD="$cmd"
            echo "Found: $cmd (Python $VERSION)"
            break
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo "Error: Python 3.11+ not found in PATH"
    echo "Please install Python 3.11+ from https://www.python.org/"
    exit 1
fi

# Create virtual environment
echo ""
echo "Creating virtual environment in .venv..."
if [ -d ".venv" ]; then
    echo "Virtual environment already exists, skipping creation"
else
    "$PYTHON_CMD" -m venv .venv
    echo "Virtual environment created successfully"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
python -m pip install --upgrade pip setuptools wheel || echo "Warning: Failed to upgrade pip"

# Install project in editable mode with dev dependencies
echo ""
echo "Installing project dependencies..."
pip install -e ".[dev]"

# Copy .env.example to .env if not exists
echo ""
echo "Setting up environment file..."
if [ -f ".env" ]; then
    echo ".env already exists, skipping"
else
    cp .env.example .env
    echo ".env created from .env.example"
    echo "Please edit .env and add your API keys!"
fi

# Create logs directory
echo ""
echo "Creating logs directory..."
if [ ! -d "logs" ]; then
    mkdir -p logs
    echo "logs/ directory created"
fi

echo ""
echo "=== Bootstrap Complete ==="
echo ""
echo "Next steps:"
echo "  1. Edit .env and add your API keys (OPENAGENDA_API_KEY, MISTRAL_API_KEY)"
echo "  2. Activate the venv: source .venv/bin/activate"
echo "  3. Build the index: python scripts/build_index.py"
echo "  4. Run the API: uvicorn api.main:app --reload"
echo "  5. Or use VS Code tasks: Ctrl+Shift+P -> Tasks: Run Task"
echo ""
