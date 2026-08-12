# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path
import sys

project_root = Path(SPECPATH).parents[1]
ml_dir = project_root / "robotics" / "ml"

datas = [
    (str(ml_dir / "teachable_machine_demo.html"), "robotics/ml"),
    (str(ml_dir / "teachable_machine_actions.json"), "robotics/ml"),
    (str(ml_dir / "default_config.json"), "robotics/ml"),
    (str(ml_dir / "default_actions.json"), "robotics/ml"),
    (str(ml_dir / "assets"), "robotics/ml/assets"),
]

a = Analysis(
    [str(ml_dir / "teachable_machine_bridge.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=["serial.tools.list_ports", "dynamixel_sdk"],
    hookspath=[],
    runtime_hooks=[],
    excludes=["cv2", "pandas", "pygame", "mujoco"],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [] if sys.platform == "darwin" else a.binaries,
    [] if sys.platform == "darwin" else a.datas,
    [],
    name="RobotSorter",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    exclude_binaries=sys.platform == "darwin",
)

if sys.platform == "darwin":
    collected = COLLECT(
        exe,
        a.binaries,
        a.datas,
        strip=False,
        upx=False,
        name="RobotSorter",
    )
    app = BUNDLE(
        collected,
        name="RobotSorter.app",
        icon=None,
        bundle_identifier="edu.ttic.robot-sorter",
    )

recorder_analysis = Analysis(
    [str(ml_dir / "record_sorting_poses.py")],
    pathex=[str(project_root), str(ml_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=["serial.tools.list_ports", "dynamixel_sdk"],
    hookspath=[],
    runtime_hooks=[],
    excludes=["cv2", "pandas", "pygame", "mujoco"],
    noarchive=False,
)
recorder_pyz = PYZ(recorder_analysis.pure)
recorder = EXE(
    recorder_pyz,
    recorder_analysis.scripts,
    recorder_analysis.binaries,
    recorder_analysis.datas,
    [],
    name="RobotPoseRecorder",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
)
