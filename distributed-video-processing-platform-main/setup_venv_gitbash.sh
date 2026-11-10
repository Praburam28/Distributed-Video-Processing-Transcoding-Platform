#!/usr/bin/env bash
set -e
python -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
echo "Virtual environment created and activated for this Git Bash session."
echo "To activate later: source .venv/Scripts/activate"
