@echo off
echo Physical execution requires a successful preflight and recorded poses.
"%~dp0RobotSorter.exe" --execute
pause
