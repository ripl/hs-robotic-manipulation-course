#!/bin/sh
set -eu

PROJECT_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$PROJECT_ROOT"
python3 -m venv "$PROJECT_ROOT/.robot-sorter-build"
"$PROJECT_ROOT/.robot-sorter-build/bin/python" -m pip install --upgrade pip
"$PROJECT_ROOT/.robot-sorter-build/bin/python" -m pip install -r "$PROJECT_ROOT/robotics/ml/requirements-build.txt"
"$PROJECT_ROOT/.robot-sorter-build/bin/pyinstaller" --clean --noconfirm "$PROJECT_ROOT/robotics/ml/robot-sorter.spec"
