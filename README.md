# RCPepTelegram

**RCPepTelegram** is a Telegram-controlled remote control bot for Windows, inspired by a previous project named *Peppino*.  
It provides a wide set of remote interaction features, including system control, media capture, automation, and prank-oriented actions.

**Tested on:** Windows 10 / Windows 11 only.

---

## 📌 Overview

RCPepTelegram runs locally on a Windows machine and exposes its functionality through a Telegram bot.
Commands, media uploads, and plugins allow real-time interaction with the target system.

The project is intended for educational, experimental, and controlled environments.

---

## 📚 Documentation

- 📄 **Commands:** `docs/COMMANDS.md`
- 🧩 **Plugins:** `docs/PLUGINS.md`

---

## ✨ Features

- Screen recording (fixed duration)
- Webcam recording
- Live screen and webcam streaming (via tunnel providers)
- Screenshot capture
- Microphone audio recording
- Keylogging with Telegram delivery
- Remote command execution
- Duckyscript payload execution
- Custom message boxes
- System control (shutdown, simulated actions, etc.)
- Media-based pranks (popups, jumpscares, wallpaper video)

---

## ⌨️ Command System

### File & Media Input Commands

- **Send a photo**  
  Displays the photo as a pop-up on the screen.

- **Send a photo with `/jumpscare` caption**  
  Displays the image as a jumpscare.

- **Send a video with `/setvideowallpaper` caption**  
  Plays the video as a desktop wallpaper (avoid long videos).

- **Send an audio or voice message**  
  Plays the audio in the background.

- **Send a `.dd` file**  
  Executes the file as Duckyscript  
  (`/duckyhelp` for available commands).

- **Send a file with `/save <path>` caption**  
  Saves the file to the specified path, regardless of extension.  
  Example:  
  `photo.jpg /save C:\Users\YOURUSER\Pictures`

---

### 📚 Multi-Command Execution

Multiple commands can be executed in sequence by separating them with a comma.

**Example:**
```
/fullclip 10; /jumpscare
```

This command:
1. Starts a full recording
2. Waits 5 seconds
3. Triggers a jumpscare while recording screen and webcam

---

## 🧩 Plugin System

RCPepTelegram supports **class-based plugins** that integrate directly with the bot, UI, and messaging system.

Refer to: `docs/PLUGINS.md`

### 📁 Plugin Structure

```
plugins/
├── plugin_base.py
├── system_plugins.py
└── custom_plugins.py
```

### 🧪 Minimal Plugin Example

```python
from .plugin_base import Plugin
import os

class ShutdownTimed(Plugin):
    def __init__(self):
        super().__init__("⏻ Schedule Shutdown", "shutdown_timed")

    def action(self, seconds: int = 60):
        os.system(f"shutdown -s -t {seconds}")
        self.pep2.bsend(f"Shutdown scheduled in {seconds} seconds.")
```

### 🧠 Plugin Rules

- Must inherit from `Plugin`
- `__init__(label, command)` defines button label and Telegram command
- `action(...)` is triggered on command or button click
- `self.pep2` references the active `PeppinoTelegram` instance

### 📌 Plugin Registration

```python
plugins = [
    ShutdownTimed,
    ToggleCapsLock,
    LockWorkstation
]
```

---

## 🛠 Installation

### 1. Clone the repository

```bash
git clone https://github.com/RiccardoZappitelli/RCPepTelegram
cd RCPepTelegram
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuration

Create a Telegram bot using [BotFather](https://core.telegram.org/bots#botfather) and obtain:

- **Bot Token**
- **Chat ID**

Create an `auth.json` file in the project root:

```json
{
    "token": "<YOUR BOT TOKEN>",
    "chatid": "<YOUR CHAT ID>",
    "ngrok_token": "<YOUR NGROK TOKEN>",
    "tunnel_provider": "ngrok"
}
```

`tunnel_provider` can be either `"ngrok"` or `"localtunnel"`.

---

## 🏗 Build (Nuitka)

1. Download [the official builder](https://github.com/RiccardoZappitelli/RCPepTelegramMaker)
2. Clone the repository inside the builder's directory
3. Start compiling!
---

## ⚠️ Security & Ethical Warning

This project contains functionality that can significantly impact system security and user privacy.

Included capabilities such as:
- Remote system control
- Keylogging
- Webcam and microphone access
- Screenshot and screen recording
- Duckyscript execution

**must only be used on systems you own or are explicitly authorized to test.**

---

## ⚖️ Ethical Considerations

- Unauthorized access is illegal and unethical
- Recording audio, video, or keystrokes without consent is a serious privacy violation
- The project can be abused if deployed irresponsibly

---

## 🔐 Security Risks

- Exposure of sensitive data (Telegram tokens, chat IDs, recordings)
- Potential remote exploitation if deployed insecurely

---

## ✅ Recommendations

- Use only in controlled environments
- Secure all credentials and generated data
- Comply with applicable laws and regulations

By using this code, you accept full responsibility for its usage.  
The author is not responsible for misuse, damage, or legal consequences.

