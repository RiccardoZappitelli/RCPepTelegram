from comtypes import CLSCTX_ALL
from ctypes import cast, POINTER
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

"""
ooo        ooooo             ooo        ooooo  o8o
`88.       .888'             `88.       .888'  `"'
 888b     d'888  oooo    ooo  888b     d'888  oooo  oooo    ooo  .ooooo.  oooo d8b 
 8 Y88. .P  888   `88.  .8'   8 Y88. .P  888  `888   `88b..8P'  d88' `88b `888""8P 
 8  `888'   888    `88..8'    8  `888'   888   888     Y888'    888ooo888  888     
 8    Y     888     `888'     8    Y     888   888   .o8"'88b   888    .o  888     
o8o        o888o     .8'     o8o        o888o o888o o88'   888o `Y8bod8P' d888b    
                 .o..P'
                 `Y8P'
"""
class CustomMixer:
    def __init__(self) -> None:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(interface, POINTER(IAudioEndpointVolume))
    
    def setVolumePercentage(self, percentage: int|float) -> None:
        percentage = float(percentage)
        if percentage in range(0, 101):
            self.volume.SetMasterVolumeLevelScalar(percentage/100, None) 
    
    def getVolumePercentage(self) -> int:
        current_volume = round(self.volume.GetMasterVolumeLevelScalar()*100)
        return current_volume

    def mute(self) -> None:
        self.setVolumePercentage(0)

    def full(self) -> None:
        self.setVolumePercentage(100)