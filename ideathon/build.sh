#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Initialize database and run migrations
flask db upgrade

# Initialize admin user
python init_data.py
