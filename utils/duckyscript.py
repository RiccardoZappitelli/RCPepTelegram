import pyautogui as pg

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

#actually some parts are missing since this function has been made in ~2020
def toducky(payload, execute=False) -> str:
    print(f"ducky: {payload=}", flush=True)
    duckyScript = [x.strip() for x in payload.split("\n")]
    final = ""
    defaultDelay = 0
    if duckyScript[0][:7] == "DEFAULT":
        defaultDelay = int(duckyScript[0][:13]) / 1000
    previousStatement = ""
    duckyCommands = ["WINDOWS", "GUI", "APP", "MENU", "SHIFT", "ALT", "CONTROL", "CTRL", "DOWNARROW", "DOWN",
                     "LEFTARROW", "LEFT", "RIGHTARROW", "RIGHT", "UPARROW", "UP", "BREAK", "PAUSE", "CAPSLOCK", "DELETE", "END",
                     "ESC", "ESCAPE", "HOME", "INSERT", "NUMLOCK", "PAGEUP", "PAGEDOWN", "PRINTSCREEN", "SCROLLLOCK", "SPACE", 
                     "TAB", "ENTER", " a", " b", " c", " d", " e", " f", " g", " h", " i", " j", " k", " l", " m", " n", " o", " p", " q", " r", " s", " t",
                     " u", " v", " w", " x", " y", " z", " A", " B", " C", " D", " E", " F", " G", " H", " I", " J", " K", " L", " M", " N", " O", " P",
                     " Q", " R", " S", " T", " U", " V", " W", " X", " Y", " Z"]
    pyautoguiCommands = ["win", "win", "optionleft", "optionleft", "shift", "alt", "ctrl", "ctrl", "down", "down",
                         "left", "left", "right", "right", "up", "up", "pause", "pause", "capslock", "delete", "end",
                         "esc", "escape", "home", "insert", "numlock", "pageup", "pagedown", "printscreen", "scrolllock", "space",
                         "tab", "enter", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t",
                         "u", "v", "w", "x", "y", "z", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p",
                         "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
    for line in duckyScript:
        if line[0:3] == "REM":
            previousStatement = line.replace("REM", "#")
        elif line[0:5] == "DELAY":
            previousStatement = "sleep(" + str(float(line[6:]) / 1000) + ")"
        elif line[0:6] == "STRING":
            previousStatement = "pg.typewrite(\"" + line[7:] + "\", interval=0.02)"
        elif line[0:6] == "REPEAT":
            for i in range(int(line[7:]) - 1):
                final += previousStatement
                final += "\n"
        else:
            previousStatement = "pg.hotkey("
            for j in range(len(pyautoguiCommands)):
                if line.find(duckyCommands[j]) != -1:
                    previousStatement = previousStatement + "\'" + pyautoguiCommands[j] + "\',"
            previousStatement = previousStatement[:-1] + ")"
        if defaultDelay != 0:
            previousStatement = "sleep(" + str(defaultDelay) + ")"
        final += previousStatement
        final += "\n"

    final = final.replace("pg.hotkey)\n", "")
    if execute:
        exec(final)
    return final
