#!/bin/sh
python3 -m venv env

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
echo "export PYTHONPATH=\"\$PYTHONPATH:$PROJECT_ROOT\"" >> env/bin/activate

. env/bin/activate

echo "Virtual environment created. To use it, run 'source env/bin/activate'."
