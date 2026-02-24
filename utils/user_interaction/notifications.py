from winotify import audio as toastaudio, Notification as WinNotification
from typing import Callable

AUDIO_MAP: dict[str, object] = {

    # 🔔 Standard notifications
    "default": toastaudio.Default,
    "im": toastaudio.IM,
    "mail": toastaudio.Mail,
    "reminder": toastaudio.Reminder,
    "sms": toastaudio.SMS,

    # 🚨 Looping alarms
    "loop_alarm": toastaudio.LoopingAlarm,
    "loop_alarm2": toastaudio.LoopingAlarm2,
    "loop_alarm3": toastaudio.LoopingAlarm3,
    "loop_alarm4": toastaudio.LoopingAlarm4,
    "loop_alarm6": toastaudio.LoopingAlarm6,
    "loop_alarm8": toastaudio.LoopingAlarm8,
    "loop_alarm9": toastaudio.LoopingAlarm9,
    "loop_alarm10": toastaudio.LoopingAlarm10,

    # 📞 Looping calls
    "loop_call": toastaudio.LoopingCall,
    "loop_call2": toastaudio.LoopingCall2,
    "loop_call3": toastaudio.LoopingCall3,
    "loop_call4": toastaudio.LoopingCall4,
    "loop_call5": toastaudio.LoopingCall5,
    "loop_call6": toastaudio.LoopingCall6,
    "loop_call7": toastaudio.LoopingCall7,
    "loop_call8": toastaudio.LoopingCall8,
    "loop_call9": toastaudio.LoopingCall9,
    "loop_call10": toastaudio.LoopingCall10,

    # 🔇 Silent
    "silent": toastaudio.Silent,
}

def notify_toast_with_url(appname: str, title: str, message: str, url_label: str, url: str, audio:str) -> None:
    toast = WinNotification(
        app_id=appname, 
        title=title,
        msg=message,
        duration="short",
    )

    toast.add_actions(label=url_label, launch=url)
    toast.set_audio(AUDIO_MAP.get(audio.lower(), toastaudio.Default), loop=False)
    toast.show()

def notify_toast(appname: str, title: str, message: str, audio: str, callback: Callable|None=None) -> None:
    toast = WinNotification(
        app_id=appname,
        title=title,
        msg=message,
        duration="short"
    )
    if callback:
        toast.add_actions(launch=callback)
    toast.set_audio(AUDIO_MAP.get(audio.lower(), toastaudio.Default), loop=False)
    toast.show()