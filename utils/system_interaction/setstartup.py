import os
import sys
import subprocess

def create_startup_task(task_name, isfrozen) -> bool:
    if isfrozen:
        exe_path = os.path.abspath(sys.executable)
        task_cmd = f'"{exe_path}"'
        working_dir = os.path.dirname(exe_path)
    else:
        script_path = os.path.abspath(__file__)
        python_path = os.path.abspath(sys.executable)
        task_cmd = f'"{python_path}" "{script_path}"'
        working_dir = os.path.dirname(script_path)

    try:
        subprocess.run([
            "schtasks",
            "/Create",
            "/TN", task_name,
            "/TR", task_cmd,
            "/SC", "ONLOGON",          # 👈 MUCH more stable for apps
            "/DELAY", "0000:20",       # 20s delay after login
            "/RL", "HIGHEST",
            "/F",
            "/V1"
        ], check=True)

        return True

    except Exception as e:
        print(e)
        return False