#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Initialize database and run migrations
flask db upgrade

# Create admin user if it doesn't exist
python create_admin.py
