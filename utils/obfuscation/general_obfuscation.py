import sys
import os
import ctypes
import random

def hide_files(dir) -> None:
    for file in os.listdir(dir):
        try:
            print(f"Hiding: {file}")
            ctypes.windll.kernel32.SetFileAttributes(file, 0x02)
        except:
            print(f"Error hiding {file}")
            pass