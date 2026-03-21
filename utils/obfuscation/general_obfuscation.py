import ctypes
import os
from pathlib import Path

def hide_file(path: str):
    FILE_ATTRIBUTE_HIDDEN = 0x2
    FILE_ATTRIBUTE_SYSTEM  = 0x4
    ctypes.windll.kernel32.SetFileAttributesW(
        str(Path(path).resolve()),
        FILE_ATTRIBUTE_HIDDEN | FILE_ATTRIBUTE_SYSTEM
    )

def hide_files(dir=None):
    temp_base = dir or os.path.dirname(__file__)
    for item in Path(temp_base).rglob("*"):
        if item.is_file():
            hide_file(str(item))