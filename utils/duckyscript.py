"""
oooooooooo.                         oooo                     .oooooo..o                     o8o                 .   
`888'   `Y8b                        `888                    d8P'    `Y8                     `"'               .o8   
 888      888 oooo  oooo   .ooooo.   888  oooo  oooo    ooo Y88bo.       .ooooo.  oooo d8b oooo  oo.ooooo.  .o888oo 
 888      888 `888  `888  d88' `"Y8  888 .8P'    `88.  .8'   `"Y8888o.  d88' `"Y8 `888""8P `888   888' `88b   888   
 888      888  888   888  888        888888.      `88..8'        `"Y88b 888        888      888   888   888   888   
 888     d88'  888   888  888   .o8  888 `88b.     `888'    oo     .d8P 888   .o8  888      888   888   888   888 . 
o888bood8P'    `V88V"V8P' `Y8bod8P' o888o o888o     .8'     8""88888P'  `Y8bod8P' d888b    o888o  888bod8P'   "888" 
                                                .o..P'                                            888
                                                `Y8P'                                            o888o
"""

KEYMAP = {
    "GUI": "win",
    "WINDOWS": "win",
    "CTRL": "ctrl",
    "CONTROL": "ctrl",
    "ALT": "alt",
    "SHIFT": "shift",
    "ENTER": "enter",
    "TAB": "tab",
    "ESC": "esc",
    "ESCAPE": "esc",
    "SPACE": "space",
    "UP": "up",
    "DOWN": "down",
    "LEFT": "left",
    "RIGHT": "right",
    "DELETE": "delete",
    "DEL": "delete",
    "BACKSPACE": "backspace",
    "HOME": "home",
    "END": "end",
    "PAGEUP": "pageup",
    "PAGEDOWN": "pagedown",
    "PRINTSCREEN": "printscreen",
    "CAPSLOCK": "capslock",
    "NUMLOCK": "numlock",
}

#actually some parts are missing since this function has been made in ~2020
def toducky(payload, execute=False) -> str:
    lines = [l.strip() for l in payload.splitlines() if l.strip()]
    out = []
    default_delay = 0.0
    last_stmt = None

    def emit(stmt: str):
        nonlocal last_stmt
        out.append(stmt)
        last_stmt = stmt

    for line in lines:
        # comments
        if line.startswith(("REM", "#")):
            continue

        tokens = line.split()

        cmd = tokens[0]

        # DEFAULT_DELAY <ms>
        if cmd == "DEFAULT_DELAY":
            default_delay = float(tokens[1]) / 1000.0
            continue

        # DELAY <ms>
        if cmd == "DELAY":
            emit(f"sleep({float(tokens[1]) / 1000.0})")
            continue

        # STRING <text>
        if cmd == "STRING":
            text = line[len("STRING "):]
            emit(f"pg.write({text!r}, interval=0.01)")
        
        # STRINGLN <text>
        elif cmd == "STRINGLN":
            text = line[len("STRINGLN "):]
            emit(f"pg.write({text!r}, interval=0.01); pg.press('enter')")

        # REPEAT <n>
        elif cmd == "REPEAT":
            if last_stmt is None:
                continue
            count = int(tokens[1]) - 1
            for _ in range(count):
                out.append(last_stmt)

        # key combinations (GUI r, CTRL ALT DEL, etc.)
        else:
            keys = []
            for t in tokens:
                t = t.upper()
                if t in KEYMAP:
                    keys.append(KEYMAP[t])
                elif len(t) == 1:
                    keys.append(t.lower())
            if keys:
                emit(f"pg.hotkey({', '.join(repr(k) for k in keys)})")

        # implicit default delay
        if default_delay > 0:
            out.append(f"sleep({default_delay})")

    final = "\n".join(out)

    if execute:
        exec("import time\nimport pyautogui as pg\n" + final)

    return final

