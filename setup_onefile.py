"""
cx_Freeze setup script for Elden Ring Preset Manager
MINIMAL FILES VERSION (as close to single-file as cx_Freeze can get)

Build with:
    python setup_minimal.py build
"""

import sys
from cx_Freeze import setup, Executable

# Build options to minimize files
build_exe_options = {
    "packages": [
        "tkinter",
        "elden_ring_save_parser_lib",
        "character_presets",
    ],
    "includes": [
        "elden_ring_save_parser_lib.save",
        "elden_ring_save_parser_lib.user_data_10",
        "elden_ring_save_parser_lib.user_data_x",
        "elden_ring_save_parser_lib.character",
        "elden_ring_save_parser_lib.equipment",
        "elden_ring_save_parser_lib.world",
        "elden_ring_save_parser_lib.event_flags",
        "elden_ring_save_parser_lib.er_types",
    ],
    "excludes": [
        "matplotlib",
        "numpy",
        "scipy",
        "pandas",
        "PIL",
        "pytest",
        "unittest",
        "distutils",
        "email",
        "html",
        "http",
        "urllib",
        "xml",
        "pydoc",
        "test",
        "tkinter.test",
        "asyncio",
        "concurrent",
        "multiprocessing",
    ],
    "optimize": 2,
    "include_msvcr": False,
}

# Base for GUI (no console)
base = "gui" if sys.platform == "win32" else None

# Single executable
executables = [
    Executable(
        script="preset_gui.py",
        base=base,
        target_name="Elden Ring Preset Manager.exe",
        icon="icon.ico" if sys.platform == "win32" else None,
        copyright="Copyright (C) 2026 Hapfel",
    )
]

setup(
    name="Elden Ring Preset Manager",
    version="1.1.0",
    description="Elden Ring Character Preset Manager",
    options={"build_exe": build_exe_options},
    executables=executables,
)