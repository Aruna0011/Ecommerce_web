#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install Python 3.10 if not present
if ! command -v python3.10 &> /dev/null; then
    echo "Python 3.10 not found. Installing..."
    apt-get update && apt-get install -y python3.10 python3.10-venv
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3.10 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip and setuptools
python -m pip install --upgrade pip setuptools wheel

# Install Python dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput --clear

# Apply database migrations
python manage.py migrate --noinput
