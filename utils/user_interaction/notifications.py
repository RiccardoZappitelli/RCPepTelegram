from winotify import audio as toastaudio, Notification as WinNotification
from typing import Callable

# Map user-friendly names to winotify audio constants
AUDIO_MAP = {
    "default": toastaudio.Default,
    "im": toastaudio.IM,
    "mail": toastaudio.Mail,
    "reminder": toastaudio.Reminder,
    "sms": toastaudio.SMS,
    "alarm": toastaudio.Alarm,
    "looping_alarm": toastaudio.LoopingAlarm,
    "looping_call": toastaudio.LoopingCall,
    "silent": toastaudio.Silent,
}

def notify_toast_with_url(appname: str, title: str, message: str, url_label: str, url: str) -> None:
    toast = WinNotification(
        app_id=appname, 
        title=title,
        msg=message,
        duration="short",
    )

    toast.add_actions(label=url_label, launch=url)
    toast.set_audio(toastaudio.Default, loop=False)
    toast.show()

def notify_toast(appname: str, title: str, message: str, callback: Callable|None=None) -> None:
    toast = WinNotification(
        app_id=appname,
        title=title,
        msg=message,
        duration="short"
    )
    if callback:
        toast.add_actions(launch=callback)
    toast.set_audio(toastaudio.Default, loop=False)