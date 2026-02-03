# Commands

_This file is auto-generated. Do not edit manually._

## null

### `execute`

**Label:** `null`  
**Function:** `execute`

**Positional arguments:**

- `*command`

**Keyword-only arguments:**

- `return_output`
- `shell`

> null

## 🌐 Network

### `block_http`

**Label:** `🚫 Block HTTP`  
**Function:** `block_http`

**Positional arguments:**

- `timeout`

> Block all outbound HTTP traffic (port 80).

### `block_https`

**Label:** `🚫 Block HTTPS`  
**Function:** `block_https`

**Positional arguments:**

- `timeout`

> Block all outbound HTTPS traffic (port 443).

### `block_port`

**Label:** `🚫 Block Port`  
**Function:** `block_port`

**Positional arguments:**

- `port`
- `timeout`

> Block a specific TCP/UDP port.

### `getip`

**Label:** `🌐 Get IP`  
**Function:** `getip`

> Get public IP and location.

### `urltoast`

**Label:** `🔗 URL Toast`  
**Function:** `notify_toast`

**Positional arguments:**

- `appname`
- `title`
- `message`
- `url_label`
- `url`

> Show Windows toast with URL.

### `wifiinfo`

**Label:** `📶 Wifiinfo`  
**Function:** `wifiinfo`

> Show saved WiFi credentials.

## 🎮 Input

### `capslock`

**Label:** `🔠 Capslock`  
**Function:** `<lambda>`

> Toggle Caps Lock.

### `leftclick`

**Label:** `🖱️ Left Click`  
**Function:** `leftclick`

> Left mouse click.

### `mousecontroller`

**Label:** `🎮 Mousecontroller`  
**Function:** `mousecontroller`

> Open mouse control menu.

### `moused`

**Label:** `⬇️ Move Down`  
**Function:** `moused`

> Move mouse down.

### `mousel`

**Label:** `⬅️ Move Left`  
**Function:** `mousel`

> Move mouse left.

### `mouselock`

**Label:** `🖱️ Mouselock`  
**Function:** `mouselock`

**Positional arguments:**

- `timer`

> Lock mouse position.

### `mouser`

**Label:** `➡️ Move Right`  
**Function:** `mouser`

> Move mouse right.

### `mouseu`

**Label:** `⬆️ Move Up`  
**Function:** `mouseu`

> Move mouse up.

### `randomkeyboard`

**Label:** `🎹 Randomkeyboard`  
**Function:** `randomkeyboard`

**Positional arguments:**

- `timeout`

> Send random keyboard input.

### `rightclick`

**Label:** `🖱️ Right Click`  
**Function:** `rightclick`

> Right mouse click.

### `setMouseJump`

**Label:** `🎯 Set Mouse Jump`  
**Function:** `setMouseJump`

**Positional arguments:**

- `jump`

> Set mouse jump distance.

## 🎵 Sound FX

### `behindyou_kid`

**Label:** `👶 Behind you (kid)`  
**Function:** `behindyou_kid`

> Play 'Behind you' child voice.

### `behindyou_whisper`

**Label:** `👻 Behind you (whisper)`  
**Function:** `behindyou_whisper`

> Play 'Behind you' whisper.

### `breath`

**Label:** `🌬️ Breath`  
**Function:** `breath`

> Play breathing sound.

### `fart`

**Label:** `💨 Fart`  
**Function:** `fart`

> Play fart sound.

### `knockknock`

**Label:** `🚪 Knock`  
**Function:** `knockknock`

> Play knocking sound.

### `pss`

**Label:** `👂 Psst`  
**Function:** `pss`

> Play 'psst' sound.

### `psst`

**Label:** `👂 Psst`  
**Function:** `pss`

> Alias for pss.

### `scream11s`

**Label:** `😱 11s Scream`  
**Function:** `scream_11s`

> Play 11-second scream.

### `scream15s`

**Label:** `😱 15s Scream`  
**Function:** `scream_15s`

> Play 15-second scream.

### `tralalerotralala`

**Label:** `🎶 Tralalero`  
**Function:** `<lambda>`

> Play Italian brainrot sound.

## 🏠 Menu

### `mainmenu`

**Label:** `🏠 Main Menu`  
**Function:** `mainmenu`

> Open the main menu.

### `menu_audio`

**Label:** `🔊 Audio & Volume`  
**Function:** `menu_audio`

> Open Audio & Volume menu.

### `menu_camera`

**Label:** `📸 Camera & Screen`  
**Function:** `menu_camera`

> Open Camera & Screen menu.

### `menu_cantopen`

**Label:** `🔒 Can't Open List`  
**Function:** `menu_cantopen`

> Open Can't Open List menu.

### `menu_control`

**Label:** `💻 System Control`  
**Function:** `menu_control`

> Open System Control menu.

### `menu_duckyscript`

**Label:** `🦆 DuckyScript`  
**Function:** `menu_ducky`

> Opens ducky quick keys.

### `menu_input`

**Label:** `🎮 Input / Device Control`  
**Function:** `menu_input`

> Open Input / Device Control menu.

### `menu_keylogger`

**Label:** `🧠 Keylogger`  
**Function:** `menu_keylogger`

> Open Keylogger menu.

### `menu_messaging`

**Label:** `📋 Messaging`  
**Function:** `menu_messaging`

> Open Messaging menu.

### `menu_misc`

**Label:** `🦑 Misc`  
**Function:** `menu_misc`

> Open Misc menu.

### `menu_mitm`

**Label:** `🕵️‍♂️ MITM`  
**Function:** `menu_mitm`

> Open MITM menu.

### `menu_network`

**Label:** `🌐 Network & Remote Access`  
**Function:** `menu_network`

> Open Network & Remote Access menu.

### `menu_plugins`

**Label:** `🔌 Your Plugins`  
**Function:** `menu_plugins`

> Open Plugins menu.

### `menu_pranks`

**Label:** `😈 Pranks & Visuals`  
**Function:** `menu_pranks`

> Open Pranks & Visuals menu.

### `menu_soundfx`

**Label:** `🎵 Sound Effects`  
**Function:** `menu_soundfx`

> Open Sound Effects menu.

### `menu_system`

**Label:** `🛑 System & Shutdown`  
**Function:** `menu_system`

> Open System & Shutdown menu.

### `menu_utilities`

**Label:** `🔧 Utility`  
**Function:** `menu_utilities`

> Open Utilities Menu

## 💻 System Control

### `cmdsession`

**Label:** `</> CMDSession`  
**Function:** `cmdsession`

> Open interactive CMD session.

### `disk_info`

**Label:** `💿 List Drives`  
**Function:** `get_disk_info`

> Sends infos about the connected drives.

### `execute_withoutput`

**Label:** `⚙️ Execute`  
**Function:** `<lambda>`

**Positional arguments:**

- `x`

> Execute system command.

### `processkiller`

**Label:** `💀 Process Killer`  
**Function:** `process_killer`

**Positional arguments:**

- `page`

> Kill process from list.

### `procmonadd`

**Label:** `➕ Procmon Add`  
**Function:** `processmonitoradd`

**Positional arguments:**

- `processname`

> Add process to monitor.

### `procmonmenu`

**Label:** `📊 Procmon Menu`  
**Function:** `processmonitormenushow`

> Show process monitor menu.

### `procmonrem`

**Label:** `➖ Procmon Remove`  
**Function:** `processmonitorrem`

**Positional arguments:**

- `processname`

> Remove process from monitor.

### `terminateprocess`

**Label:** `🛑 Terminate Process`  
**Function:** `terminate_process_by_name`

**Positional arguments:**

- `process_name`

> Terminate process by name.

## 📋 Messaging

### `bsend`

**Label:** `📤 Bsend`  
**Function:** `bsend`

**Positional arguments:**

- `text`
- `retries`
- `parse_mode`
- `reply_markup`

> Send text message.

### `deleteallmessages`

**Label:** `🗑️ Deleteallmessages`  
**Function:** `deleteallmessages`

> Delete all messages.

### `deletemessages`

**Label:** `❌ Deletemessages`  
**Function:** `deleteallmessages`

> Delete recent messages.

### `id`

**Label:** `🆔 Id`  
**Function:** `<lambda>`

> Send chat ID.

## 📸 Camera

### `camerawallpaper`

**Label:** `📷 Camera Wallpaper`  
**Function:** `setCameraAsWallpaper`

**Positional arguments:**

- `seconds`

> Set webcam as wallpaper.

### `checkforface`

**Label:** `🔍 Check for Face`  
**Function:** `checkforface`

> Check for face presence.

### `displaymode`

**Label:** `🖼️ Display Options`  
**Function:** `display_mode`

> Change display mode.

### `fullclip`

**Label:** `🎞️ Record Full Clip`  
**Function:** `record_webcam_and_screen`

**Positional arguments:**

- `capture_duration`
- `caption`

> Record webcam and screen.

### `recordjum`

**Label:** `🎙️ Record Audio Jump`  
**Function:** `record_jumpscare_reaction`

**Positional arguments:**

- `onlycamera`

> Record jumpscare reaction.

### `screenclip`

**Label:** `🖥️ Record Screen`  
**Function:** `record_screen`

**Positional arguments:**

- `duration`
- `caption`

> Record screen only.

### `screenshot`

**Label:** `🖼️ Take Screenshot`  
**Function:** `screenshot`

> Capture screen.

### `screenstreamstart`

**Label:** `🖥️🟢 Start Screen Stream`  
**Function:** `start_screen_tunnel`

> Start screen stream.

### `screenstreamstop`

**Label:** `🖥️🔴 Stop Screen Stream`  
**Function:** `stop_screen_tunnel`

**Positional arguments:**

- `verbose`

> Stop screen stream.

### `selfie`

**Label:** `🤳 Webcam Snapshot`  
**Function:** `selfie`

**Positional arguments:**

- `caption`
- `reply_markup`

> Take webcam photo.

### `selfieandscreenshot`

**Label:** `🤳🖼️ Take Screenshot&Webcam`  
**Function:** `screenshotandselfie`

> Caputre screen and webcam in the same image

### `setvideowallpaper`

**Label:** `🎞️ Set Video Wallpaper`  
**Function:** `setvideowallpaper`

**Positional arguments:**

- `videofilename`

> Set video as wallpaper.

### `stop_all_tunnels`

**Label:** `❌🔴 Stop All Streams`  
**Function:** `stop_all_tunnels`

> Stop all active streams.

### `waitforface`

**Label:** `⏳ Waiting for Face`  
**Function:** `waitforface`

**Positional arguments:**

- `timeout`

> Capture photo when face detected.

### `webcamandscreenstreamstart`

**Label:** `📹🖥️🟢 Start Both Streams`  
**Function:** `start_webcam_and_screen_tunnel`

> Start webcam and screen streams.

### `webcamandscreenstreamstop`

**Label:** `📹🖥️🔴 Stop Both Streams`  
**Function:** `stop_webcam_and_screen_tunnel`

**Positional arguments:**

- `verbose`

> Stop webcam and screen streams.

### `webcamclip`

**Label:** `🎥 Record Webcam`  
**Function:** `record_webcam`

**Positional arguments:**

- `duration`
- `caption`

> Record webcam only.

### `webcamstreamstart`

**Label:** `📹🟢 Start Webcam Stream`  
**Function:** `start_webcam_tunnel`

> Start webcam stream.

### `webcamstreamstop`

**Label:** `📹🔴 Stop Webcam Stream`  
**Function:** `stop_webcam_tunnel`

**Positional arguments:**

- `verbose`

> Stop webcam stream.

## 🔊 Audio

### `disturbed_overlay_and_random_noise`

**Label:** `🌀📻 Video&Sound Disturbance`  
**Function:** `disturbed_overlay_and_random_noise`

**Positional arguments:**

- `duration`

> Noise overlay with audio.

### `fullvolume`

**Label:** `🔊 Full Volume`  
**Function:** `<lambda>`

> Set volume to maximum.

### `getvolume`

**Label:** `📊 Get Volume`  
**Function:** `<lambda>`

> Get current volume.

### `microphone`

**Label:** `🎙️ Microphone`  
**Function:** `send_record_audio`

**Positional arguments:**

- `seconds`
- `caption`

> Record microphone audio.

### `mixermenu`

**Label:** `🎛️ Mixer Menu`  
**Function:** `mixer_menu`

> Open audio mixer menu.

### `mutevolume`

**Label:** `🔇 Mute Volume`  
**Function:** `<lambda>`

> Mute system volume.

### `playfromurl`

**Label:** `🔗 Play from URL`  
**Function:** `play_from_url`

**Positional arguments:**

- `url`
- `filename`
- `delete_after_playing`

> Play audio from URL.

### `playrandomnoise`

**Label:** `📡 Play Noise`  
**Function:** `playrandomnoise`

**Positional arguments:**

- `duration`

> Play static/interference noise.

### `setvolume`

**Label:** `🎚️ Set Volume`  
**Function:** `setVolumePercentage`

**Positional arguments:**

- `percentage`

> Set volume percentage.

## 🔒 Can't Open

### `cantopenadd`

**Label:** `🚫 Cantopenadd`  
**Function:** `cantopen`

**Positional arguments:**

- `process`

> Block process execution.

### `cantopenmenu`

**Label:** `📋 Cantopenmenu`  
**Function:** `cantopenmenu`

> Show blocked processes.

### `cantopenremove`

**Label:** `❌ Cantopenremove`  
**Function:** `removefromcantopen`

**Positional arguments:**

- `process`

> Unblock process execution.

## 🔧 Utility

### `get_logs`

**Label:** `📄 Get Logs`  
**Function:** `get_logs`

> Gets the program logs ins a file

### `help`

**Label:** `❓ Help`  
**Function:** `show_help`

> Show help menu.

### `nothing`

**Label:** `Nothing`  
**Function:** `<lambda>`

> No-op command.

### `stop`

**Label:** `🛑 Stop`  
**Function:** `stop`

> Stop current operation.

### `test`

**Label:** `🧪 Test`  
**Function:** `test`

> Run test routine.

## 🕵️‍♂️ MITM

### `block_http`

**Label:** `Block HTTP`  
**Function:** `block_http`

**Positional arguments:**

- `timeout`

> Blocks traffic http

### `block_https`

**Label:** `Block HTTPS`  
**Function:** `block_https`

**Positional arguments:**

- `timeout`

> Blocks traffic on a specific port.

### `block_port`

**Label:** `Block Port`  
**Function:** `block_port`

**Positional arguments:**

- `port`
- `timeout`

> Blocks traffic on a specific port.

## 😈 Pranks

### `camerawallpaper`

**Label:** `📷 Camera Wallpaper`  
**Function:** `setCameraAsWallpaper`

**Positional arguments:**

- `seconds`

> Webcam as wallpaper.

### `distortedscreen`

**Label:** `🌀 Distorted Screen`  
**Function:** `distorted_screen`

> Distort screen output.

### `disturbed_overlay_and_random_noise`

**Label:** `🌀📻 Video&Sound Disturbance`  
**Function:** `disturbed_overlay_and_random_noise`

**Positional arguments:**

- `duration`

> Noise overlay + audio.

### `fakebsod`

**Label:** `💀 Fake BSOD`  
**Function:** `fake_bsod`

**Positional arguments:**

- `duration`
- `qr_url`

> Show fake Blue Screen of Death.

### `hdmi_drowning_effect`

**Label:** `🖥️🌀 Video Signal Drowning Effect`  
**Function:** `wrapper_for_hdmi_overlay`

**Positional arguments:**

- `timeout_seconds`

> Noise overlay effect.

### `invertedscreen`

**Label:** `🔄 Inverted Screen`  
**Function:** `inverted_screen`

> Invert screen colors.

### `jumpscare`

**Label:** `👻 Jumpscare`  
**Function:** `jumpscare`

**Positional arguments:**

- `image`
- `audio`
- `playaudio`
- `showimage`
- `setvolume`

> Trigger random jumpscare.

### `jumpscarenoaudio`

**Label:** `😶‍🌫️ Jumpscare noaudio`  
**Function:** `jumpscarenoaudio`

> Jumpscare without sound.

### `messagebox`

**Label:** `💬 Message Box`  
**Function:** `message_box`

**Positional arguments:**

- `text`
- `title`

> Show custom message box.

### `messagespam`

**Label:** `📨 Message Spam`  
**Function:** `spam_windows`

**Positional arguments:**

- `n`
- `text`

> Spam message boxes.

### `setvideowallpaper`

**Label:** `🎞️ Set Video Wallpaper`  
**Function:** `setvideowallpaper`

**Positional arguments:**

- `videofilename`

> Video as wallpaper.

### `showqr`

**Label:** `QR Overlay`  
**Function:** `show_qr_overlay`

**Positional arguments:**

- `url`
- `text`
- `duration`

> Display QR code overlay with custom text. Args: url [text] [duration]

### `whisper_overlay`

**Label:** `👻 Red Text Overlay`  
**Function:** `whisper_overlay`

**Positional arguments:**

- `duration`
- `whispers`

> Display creepy whisper overlay.

## 🛑 System

### `altf4`

**Label:** `⌨️ Altf4`  
**Function:** `altf4`

> Send Alt+F4.

### `clear`

**Label:** `🧹 Clear`  
**Function:** `clear`

> Clean windows, webcam, temp files.

### `fakeshutdown`

**Label:** `🎭 Fakeshutdown`  
**Function:** `fake_shutdown`

> Fake shutdown sequence.

### `fakeuac`

**Label:** `Fake UAC`  
**Function:** `fakeuac`

> Fake UAC prompt.

### `selfdestruction`

**Label:** `💣 Selfdestruction`  
**Function:** `selfdestruction`

> Remove program permanently.

### `shutdown`

**Label:** `🛑 Shutdown`  
**Function:** `shutdown`

**Positional arguments:**

- `seconds`

> Power off PC.

## 🦑 Misc

### `browser`

**Label:** `🌐 Browser`  
**Function:** `open`

**Positional arguments:**

- `url`
- `new`
- `autoraise`

> Open URL in browser.

### `duckyhelp`

**Label:** `❓ Duckyhelp`  
**Function:** `<lambda>`

> Show DuckyScript help.

### `duckyscript`

**Label:** `⌨️ Duckyscript`  
**Function:** `<lambda>`

**Positional arguments:**

- `*args`

> Execute DuckyScript.

### `gabinetti`

**Label:** `🛋️ Gabinetti`  
**Function:** `gabinetti`

> Play Gabinetti meme.

### `johnpork`

**Label:** `🐷 Johnpork`  
**Function:** `johnpork`

**Positional arguments:**

- `audio`

> John Pork jumpscare.

### `johnporknoaudio`

**Label:** `🔕 Johnpork no audio`  
**Function:** `johnporknoaudio`

> John Pork without audio.

### `plankton`

**Label:** `🦑 Plankton`  
**Function:** `plankton`

**Positional arguments:**

- `audio`

> Plankton jumpscare.

### `planktonnoaudio`

**Label:** `🔇 Plankton no audio`  
**Function:** `planktonnoaudio`

> Plankton without audio.

## 🧠 Keylogger

### `keylogger`

**Label:** `⌨️ Keylogger`  
**Function:** `keylogger`

**Positional arguments:**

- `timeout`

> Log keystrokes to file.

### `livekeylogger`

**Label:** `📡 Livekeylogger`  
**Function:** `live_keylogger`

**Positional arguments:**

- `timeout`

> Live keystroke monitoring.
