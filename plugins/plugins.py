import os
import ctypes
import pyautogui as pg
import subprocess as sp
from threading import Thread
from time import sleep, time
from psutil import process_iter

from .plugin_base import Plugin

# -------------------------------
# Utilities
# -------------------------------
ONLOAD_PLUGINS_MARKER = "<ONLOADSCRIPT>"
STARTUP_SCRIPT_MARKER = "<STARTUPSCRIPT>"

def wait_for_process_to_run(name: str):
    """Wait until a process with a given name starts running."""
    while not any(p.name() == name for p in process_iter()):
        sleep(1)

def message_box(text: str, title: str = "Warning") -> int:
    """Display a message box in a separate thread."""
    def run():
        ctypes.windll.user32.MessageBoxW(0, text, title, 0x1000)
    Thread(target=run, daemon=True).start()


# -------------------------------
# Plugins
# -------------------------------
class OnStart(Plugin): # THIS IS A SPECIAL PLUGIN WHICH WILL BE EXECUTED AS SOON AS THE BOT IS READY
    def __init__(self):
        super().__init__(STARTUP_SCRIPT_MARKER, "startupscript", "this is the startupscript")

    def action(self):
        pass
        #example return self.pep2.bsend("On Start")

    def bind_pep(self, pep2):
        res = super().bind_pep(pep2)
        self.pep2.startupscript = self.action
        return res

class OnLoad(Plugin): #THIS IS A SPECIAL PLUGIN THAT WILL BE EXECUTED AS SOON AS ITS LOADED
    def __init__(self):
        super().__init__(ONLOAD_PLUGINS_MARKER, "onloadscript", "onloadscrpit")

    def action(self):
        pass
        # example: return self.pep2.bsend("On Load")

# -------------------------------
# Plugin List
# -------------------------------

plugins = [
    OnStart,
    OnLoad
]

