#!/bin/sh
set -eu
APP_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
printf '%s\n' 'Physical execution requires a successful preflight and recorded poses.'
if [ -x "$APP_DIR/RobotSorter/RobotSorter" ]; then
  "$APP_DIR/RobotSorter/RobotSorter" --execute
else
  "$APP_DIR/RobotSorter" --execute
fi
