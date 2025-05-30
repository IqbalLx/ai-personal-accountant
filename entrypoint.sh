#!/bin/sh
set -e # Exit immediately if a command exits with a non-zero status.

echo "Running database migrations..."
python /app/agents/personal_accountant/tools/database.py

echo "Starting application..."
exec adk web --port=8000 --host=0.0.0.0 /app/agents