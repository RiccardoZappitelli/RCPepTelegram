import os
import sys
import subprocess
import winreg as reg
import os
import sys
import getpass
from ..program_system.general import get_original_exe

def add_to_startup_registry(name: str = ""):
    """Add the current Python script to Windows startup (current user)"""
    if getattr(sys, 'frozen', False):
        script_path = get_original_exe()
    else:
        script_path = os.path.realpath(__file__)

    key = reg.HKEY_CURRENT_USER
    key_value = r"Software\Microsoft\Windows\CurrentVersion\Run"

    try:
        registry_key = reg.OpenKey(key, key_value, 0, reg.KEY_SET_VALUE)
        reg.SetValueEx(registry_key, name, 0, reg.REG_SZ, script_path)
        reg.CloseKey(registry_key)
        print(f"✅ Successfully added to startup: {name}")
        print(f"   Path: {script_path}")
    except Exception as e:
        print(f"❌ Failed to add to startup: {e}")

def create_startup_task(task_name, isfrozen) -> bool:
    if isfrozen:
        exe_path = get_original_exe() 
        task_cmd = f'"{exe_path}"'
        working_dir = os.path.dirname(exe_path)
    else:
        script_path = os.path.abspath(__file__)
        python_path = os.path.abspath(sys.executable)
        #task_cmd = f'"{python_path}" "{script_path}"'
        task_cmd = "cmd /k PAUSE"
        working_dir = os.path.dirname(script_path)

    username = getpass.getuser()

    try:
        subprocess.run([
            "schtasks",
            "/Create",
            "/TN", task_name,
            "/TR", task_cmd,
            "/SC", "ONLOGON",
            "/DELAY", "0000:20",
            "/RL", "HIGHEST",
            "/RU", username,
            "/F"
        ], check=True)

        return True

    except Exception as e:
        print(e)
        return False

    except Exception as e:
        print(e)
        return False