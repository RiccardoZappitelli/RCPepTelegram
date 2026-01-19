import re
import socket
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