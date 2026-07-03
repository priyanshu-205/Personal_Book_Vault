#!/bin/sh
set -e

echo "Applying database migrations..."
flask db upgrade

echo "Starting application..."
exec python run.py