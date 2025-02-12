#!/bin/bash

set -o errexit

echo "Python version:"
python3.12 --version

# Ensure pip is installed and up-to-date
if ! command -v pip3.12 &> /dev/null; then
    echo "pip3.12 could not be found, installing pip..."
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python3.12 get-pip.py --user
    rm get-pip.py
fi

# Ensure pip is in PATH
export PATH="$HOME/.local/bin:$PATH"

# Install pipenv
python3.12 -m pip install --user pipenv

echo "Installing dependencies..."
python3.12 -m pip install --user -r requirements.txt
python3.12 -m pip install setuptools

echo "Applying migrations..."
python3.12 manage.py migrate --noinput

echo "Collecting static files..."
python3.12 manage.py collectstatic --noinput --clear
