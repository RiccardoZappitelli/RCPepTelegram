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