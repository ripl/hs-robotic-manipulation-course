$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$BuildEnv = Join-Path $ProjectRoot ".robot-sorter-build"
Set-Location $ProjectRoot

py -3.11 -m venv $BuildEnv
& (Join-Path $BuildEnv "Scripts/python.exe") -m pip install --upgrade pip
& (Join-Path $BuildEnv "Scripts/python.exe") -m pip install -r (Join-Path $ProjectRoot "robotics/ml/requirements-build.txt")
& (Join-Path $BuildEnv "Scripts/pyinstaller.exe") --clean --noconfirm (Join-Path $ProjectRoot "robotics/ml/robot-sorter.spec")
