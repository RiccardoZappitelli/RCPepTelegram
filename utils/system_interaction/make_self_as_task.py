import os
import sys
import subprocess

def create_startup_task(task_name, isfrozen) -> bool:
    if isfrozen:
        exe_path = os.path.abspath(sys.executable)
        task_cmd = f'"{exe_path}"'
    else:
        script_path = os.path.abspath(__file__)
        python_path = os.path.abspath(sys.executable)
        task_cmd = f'"{python_path}" "{script_path}"'
    try:
        subprocess.run([
            "schtasks",
            "/Create",
            "/TN", task_name,
            "/TR", task_cmd,
            "/SC", "ONSTART",
            "/RU", "SYSTEM",
            "/RL", "HIGHEST",
            "/F"
        ], check=True)
        return True
    except Exception as e:
        print(e)
        return False