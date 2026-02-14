import ctypes
import pyautogui as pg

user32 = ctypes.windll.user32

def hide_cursor():
    user32.ShowCursor(False)

SYSTEM_CURSORS = [
    32512,  # OCR_NORMAL
    32513,  # OCR_IBEAM (text caret)
    32514,  # OCR_WAIT
    32515,  # OCR_CROSS
    32516,  # OCR_UP
    32517,  # OCR_SIZE
    32518,  # OCR_ICON
    32519,  # OCR_SIZENWSE
    32520,  # OCR_SIZENESW
    32521,  # OCR_SIZEWE
    32522,  # OCR_SIZENS
    32523,  # OCR_SIZEALL
    32524,  # OCR_NO
    32525,  # OCR_HAND
    32640,  # OCR_APPSTARTING
    32641,  # OCR_HELP
]

class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long),
                ("y", ctypes.c_long)]

class RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long),
                ("top", ctypes.c_long),
                ("right", ctypes.c_long),
                ("bottom", ctypes.c_long)]

def moused(jump) -> None:
    pos = pg.position()
    pg.moveTo(pos[0], pos[1]+jump)

def mousel(jump) -> None:
    pos = pg.position()
    pg.moveTo(pos[0]-jump, pos[1])

def mouser(jump) -> None:
    pos = pg.position()
    pg.moveTo(pos[0]+jump, pos[1])

def mouseu(jump) -> None:
    pos = pg.position()
    pg.moveTo(pos[0], pos[1]-jump)

def lock_mouse_position(coords=None):
    pt = POINT()
    user32.GetCursorPos(ctypes.byref(pt))

    if coords:
        x = coords[0]
        y = coords[1]
    else:
        x = pt.x
        y = pt.y
    x1 = x+1
    y1 = y+1
    rect = RECT(x, y, x1, y1)
    user32.ClipCursor(ctypes.byref(rect))

def hide_all_cursors():
    empty_cursor = user32.CreateCursor(
        None,
        0, 0,
        1, 1,
        (ctypes.c_byte * 1)(0),
        (ctypes.c_byte * 1)(0)
    )

    for cid in SYSTEM_CURSORS:
        user32.SetSystemCursor(empty_cursor, cid)

def restore_all_cursors():
    SPI_SETCURSORS = 0x0057
    user32.SystemParametersInfoW(SPI_SETCURSORS, 0, None, 0)

def enforce_lock(stop_event):
    while not stop_event.is_set():
        lock_mouse_position()
    else:
        print("[EnforceLock] stopped")

def unlock_mouse():
    user32.ClipCursor(None)

def reset_mouse_controller_and_visibility():
    #sets everything back to normal
    unlock_mouse()
    restore_all_cursors()