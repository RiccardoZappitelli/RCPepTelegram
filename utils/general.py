import re
import os
import socket
import platform
import shutil
import requests

def get_public_ip() -> str:
    r = requests.get("https://ifconfig.co", 
        headers={"User-Agent": "curl/8.0"}
    )
    return r.text

def escape_md(text: str) -> str:
    """Escape text for Telegram MarkdownV2."""
    return re.sub(r'([_*\[\]()~`>#+-=|{}.!])', r'\\\1', text)

def check_connection():
    try:
        s = socket.socket()
        s.connect(("www.google.com", 80))
    except socket.gaierror:
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
        f"🆓 Free: {free}"
    )
