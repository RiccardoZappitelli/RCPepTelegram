from winotify import audio as toastaudio, Notification as WinNotification
from typing import Callable

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