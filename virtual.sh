#!/bin/sh
python3 -m venv env

echo 'export PYTHONPATH="$PYTHONPATH:/home/ttic/Desktop/hs-robotic-manipulation-course"' >> env/bin/activate

. env/bin/activate

echo "Virtual environment created. To use it, run 'source env/bin/activate'."
