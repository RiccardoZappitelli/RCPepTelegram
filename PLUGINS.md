# RCPepTelegram Plugins Documentation

This document explains how to create, integrate, and use plugins with RCPepTelegram.

## Plugin Basics

- All plugins must inherit from `Plugin`
- The `__init__(label, command)` sets the Telegram button name and command name
- The `action(...)` method is triggered when the command/button is clicked
- `self.pep2` refers to the running `PeppinoTelegram` instance

## Core Utilities Available in Plugins

| Method | Description |
|--------|-------------|
| `bsend(text: str)` | Send a message to the bot owner. |
| `new_editable_message(content: str, autosend: bool=True)` | Create a message that can be updated later. |
| `new_loading_bar(total: int, autodelete: bool=False, showperc: bool=False, label=None)` | Create a LoadingBar for progress visualization. |
| `new_menu(menu: dict, autosend: bool=True, label: str="Choose an option: ", page: int=0, next_btn: bool=False, next_btn_lab: str="next_page", prev_btn_lab: str="previus_page", close_btn_lab: str="close_page", rows=2)` | Create a buttons menu. |
| `prompt(text: str, default: str="")` | Ask the user for a text input and return it. |
| `ask_yes_no(text: str, default: bool=True)` | Ask the user a yes/no question, returns `True` or `False`. |

## Audio & Volume Methods

| Method | Description |
|--------|-------------|
| `get_volume()` | Returns the current system volume (0–100). |
| `set_volume(level: int)` | Sets system volume (0–100). |
| `mute_volume()` | Mutes volume (0). |
| `full_volume()` | Sets volume to 100. |
| `play_from_url(url: str)` | Plays audio from a URL. |
| `urltoast(url: str)` | Shows a toast opening a URL. |
| `breath()`, `pss()`, `fart()`, `knockknock()` | Play sound effects. |
| `microphone_record(seconds: int)` | Record mic audio. |

## Screenshots & Webcam

| Method | Description |
|--------|-------------|
| `screenshot()` | Capture desktop screenshot. |
| `selfie()` | Take a webcam photo. |
| `screen_clip(duration: int)` | Record screen. |
| `webcam_clip(duration: int)` | Record webcam. |
| `full_clip(duration: int)` | Record both screen and webcam. |
| `record_jumpscare()` | Record jumpscare clip. |
| `wait_for_face(timeout: int)` | Wait until face is detected. |

## Visual & Pranks

| Method | Description |
|--------|-------------|
| `jumpscare()`, `jumpscare_no_audio()` | Trigger jumpscare. |
| `inverted_screen()`, `distorted_screen()` | Visual effects. |
| `message_box(text, title)`, `message_spam(...)` | Message box effects. |
| `camera_wallpaper()`, `set_video_wallpaper(path)` | Set webcam/video as wallpaper. |
| `hdmi_drowning_effect()`, `stop_hdmi_drowning_effect()` | Screen distortion overlay. |

## System Control

| Method | Description |
|--------|-------------|
| `execute(command: str)` | Run system command. |
| `process_killer()`, `terminate_process(name)` | Kill or manage processes. |
| `procmon_menu()`, `procmon_add(name)`, `procmon_remove(name)` | Process monitor features. |
| `cmd_session()` | Start local cmd session. |
| `shutdown_timed(seconds)` | Schedule shutdown. |
| `restart_now()` | Immediate restart. |
| `lock_workstation()` | Lock PC. |
| `toggle_network(interface)` | Enable/disable network interface. |

## Input / Device Control

| Method | Description |
|--------|-------------|
| `capslock()` | Toggle Caps Lock. |
| `random_keyboard()` | Randomize keyboard input. |
| `mouse_controller()`, `mouse_lock()` | Control or lock mouse. |
| `set_mouse_jump(value)` | Configure mouse jump sensitivity. |

## Keylogger & Misc

| Method | Description |
|--------|-------------|
| `keylogger()`, `live_keylogger()` | Record keyboard events. |
| `plankton()`, `plankton_no_audio()`, `johnpork()`, `johnpork_no_audio()`, `gabinetti()` | Fun animations/pranks. |
| `ducky_script(code)` | Execute Duckyscript. |
| `ducky_help()` | Show Duckyscript tutorial. |
| `browser(url)` | Open URL in default browser. |

## File Input Commands & Multi-command

- Send photo/video/audio with optional captions to trigger effects.  
- Multi-commands supported using semicolon `;` to chain commands in one message.

---

## Security & Ethical Notice

Use responsibly. Misuse may violate privacy, computer crime, and copyright laws.
