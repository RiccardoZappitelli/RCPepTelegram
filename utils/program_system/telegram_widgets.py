from telepot.namedtuple import InlineKeyboardButton, InlineKeyboardMarkup
from telepot.exception import TelegramError
from telepot import Bot

from re import sub
from typing import Callable, Any
from time import perf_counter, sleep

import inspect
from threading import Thread, Event
#from multiprocessing import Process
from typing import List
from collections import defaultdict
from .commands import Command
from .cancellable_thread import CancellableThread

def escape_md_v2(text: str) -> str:
    return sub(r'([_*\[\]()~`>#+\-=|{}.!])', r'\\\1', text)

def generate_help(commands: List[Command]) -> List[str]:
    """Generate help messages, splitting into multiple parts if too long."""
    # Group commands by category
    grouped = defaultdict(list)
    for cmd in commands:
        grouped[cmd.category].append(cmd)
    
    all_categories = list(grouped.keys())
    categories_with_menu_first = []
    menu_category = None
    
    for cat in all_categories:
        if cat == "menu":
            menu_category = cat
        else:
            categories_with_menu_first.append(cat)
    
    categories_with_menu_first.sort()
    
    if menu_category:
        category_order = [menu_category] + categories_with_menu_first
    else:
        category_order = categories_with_menu_first

    help_parts = []
    current_part = []
    current_length = 0
    
    for category in category_order:
        if category in grouped:
            # Format category section
            category_header = f"{category}\n"
            commands_section = ""
            
            # Add all commands for this category
            for cmd in sorted(grouped[category], key=lambda c: c.name):
                command_line = f"  /{cmd.name} - {cmd.description}\n"
                commands_section += command_line
            
            # Add separator line
            separator = "\n"
            
            # Calculate total length for this section
            section_length = len(category_header) + len(commands_section) + len(separator)
            
            # If adding this section would exceed limit, start new part
            if current_length + section_length > 2800:  # Keep under 3000 with buffer or it'll be a message too long
                if current_part:
                    help_parts.append("".join(current_part).strip())
                current_part = [category_header, commands_section, separator]
                current_length = section_length
            else:
                current_part.append(category_header)
                current_part.append(commands_section)
                current_part.append(separator)
                current_length += section_length
    
    # Add the last part if it exists
    if current_part:
        help_parts.append("".join(current_part).strip())
    
    return help_parts

all_spinners = {
    "slash": ["|", "/", "-", "\\"],
    "double_bar": ["-", "=", "~", "-"],
    "dot_wave": [".  ", ".. ", "...", " ..", "  .", "   "],
    "line_bounce": ["_", "‾"],
    "dots_3": ["⠁", "⠂", "⠄", "⠂"],
    "quarter": ["◴", "◷", "◶", "◵"],
    "half_moon": ["◐", "◓", "◑", "◒"],
    "block_corner": ["▖", "▘", "▝", "▗"],
    "clock": ["🕛", "🕐", "🕑", "🕒", "🕓", "🕔", "🕕", "🕖", "🕗", "🕘", "🕙", "🕚"],
    "arrow": ["←", "↖", "↑", "↗", "→", "↘", "↓", "↙"],
    "double_arrow": ["⇐", "⇑", "⇒", "⇓"],
    "braille": ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"],
    "colored_blocks": ["🟥⬜⬜", "🟩🟥⬜", "⬜🟩🟥", "⬜⬜🟩", "⬜⬜⬜"],
    "bouncing_bar": ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█", "▇", "▆", "▅", "▄", "▃", "▂", "▁"],
    "pixel": ["⡀", "⠄", "⠂", "⠁", "⠈", "⠐", "⠠", "⢀"],
    "circle_dots": ["◜", "◠", "◝", "◞", "◡", "◟"],
    "gear": ["⚙️", "⚙️", "⚙️", "⚙️"],  # static gear, or rotate manually
    "signal": ["▂", "▄", "▆", "▇", "█", "▇", "▆", "▄"]
}

emoji_dict = {
    "stop": "🛑",
    "warning": "⚠️",
    "error": "❌",
    "success": "✅",
    "loading": "⏳",
    "wifi": "🛜",
    "ip": "🌐",
    "key": "🔑",
    "lock": "🔒",
    "unlock": "🔓",
    "id": "🆔",
    "camera": "📸",
    "microphone": "🎤",
    "volume_high": "🔊",
    "volume_medium": "🔉",
    "volume_mute": "🔇",
    "video": "🎥",
    "photo": "📷",
    "play": "▶️",
    "pause": "⏸️",
    "file": "📄",
    "folder": "📁",
    "document": "📑",
    "checkbox": "☑️",
    "radio": "🔘",
    "next": "➡️",
    "previous": "⬅️",
    "close": "❌",
    "shutdown": "⏻",
    "mouse": "🖱️",
    "keyboard": "⌨️",
    "screen": "🖥️",
    "ghost": "👻",
    "robot": "🤖",
    "thinking": "🤔",
    "spinner": "🌀",
    "hourglass": "⏳",
    "progress": "▰",
    "empty_progress": "▱",
    "arrow_up": "⬆️",
    "arrow_down": "⬇️",
    "arrow_left": "⬅️",
    "arrow_right": "➡️",
    "double_arrow": "⇆",
    "full_block": "█",
    "empty_block": "░",
    "loading_block": "▒",
    "settings": "⚙️",
    "home": "🏠",
    "back": "↩️",
    "refresh": "🔄",
    "speaker": "🔈",
    "muted_speaker": "🔇",
    "sound_waves": "🔊",
    "plankton": "🦑",
    "john_pork": "🐷",
    "gabinetto": "🚽"
}

"""
oooooooooo.                  .       .                                  ooo        ooooo
`888'   `Y8b               .o8     .o8                                  `88.       .888'
 888     888 oooo  oooo  .o888oo .o888oo  .ooooo.  ooo. .oo.    .oooo.o  888b     d'888   .ooooo.  ooo. .oo.   oooo  oooo  
 888oooo888' `888  `888    888     888   d88' `88b `888P"Y88b  d88(  "8  8 Y88. .P  888  d88' `88b `888P"Y88b  `888  `888  
 888    `88b  888   888    888     888   888   888  888   888  `"Y88b.   8  `888'   888  888ooo888  888   888   888   888  
 888    .88P  888   888    888 .   888 . 888   888  888   888  o.  )88b  8    Y     888  888    .o  888   888   888   888  
o888bood8P'   `V88V"V8P'   "888"   "888" `Y8bod8P' o888o o888o 8""888P' o8o        o888o `Y8bod8P' o888o o888o  `V88V"V8P' 
"""
class ButtonsMenu:
    def __init__(self, chat_id: int, bot: Bot, buttons: dict[str, Callable], label: str = "Choose an action", autosend: bool=True, next_btn: bool=False, page_limit: int = 32, page: int=0, next_btn_lab: str = "next_page", prev_btn_lab: str = "previous_page", close_btn_lab="close_page", keyboard_rows=2) -> None:
        self.bot = bot
        self.label = label
        self.chat_id = chat_id
        self.buttons = buttons
        self._page_limit = page_limit
        self._page = page 
        self.keyboard_rows = keyboard_rows
        self.next_btn = next_btn
        self.next_btn_lab = next_btn_lab
        self.prev_btn_lab = prev_btn_lab
        self.close_btn_lab = close_btn_lab
        self.sent = False

        if autosend:
            self.send_keyboard()

    def create_keyboard(self) -> Any:
        start_index = self._page * self._page_limit
        button_list = [InlineKeyboardButton(text=k, callback_data=self.buttons[k]) for k in list(self.buttons.keys())[start_index:start_index + self._page_limit]]

        if self.next_btn:
            if self._page > 0:
                button_list.append(InlineKeyboardButton(text="⬅️ Previous", callback_data=self.prev_btn_lab))
            if (self._page + 1) * self._page_limit < len(self.buttons):
                button_list.append(InlineKeyboardButton(text="Close ❌", callback_data=self.close_btn_lab)) 
                button_list.append(InlineKeyboardButton(text="Next ➡️", callback_data=self.next_btn_lab)) 
        else:
            button_list.append(InlineKeyboardButton(text="Close ❌", callback_data=self.close_btn_lab)) 

        keyboard_rows = [button_list[i:i+self.keyboard_rows] for i in range(0, len(button_list), self.keyboard_rows)]
        return InlineKeyboardMarkup(inline_keyboard=keyboard_rows)

    def send_keyboard(self) -> int:
        self.keyboard = self.create_keyboard()
        self.sent = True
        self.message_id = self.bot.sendMessage(self.chat_id, self.label, reply_markup=self.keyboard)["message_id"]
        return self.message_id

    def send_next_page(self) -> None:
        self._page += 1
        self.send_keyboard()
    
    def send_previous_page(self) -> None:
        self._page -= 1
        self.send_keyboard()

    def edit_keyboard(self, buttons: dict) -> int:
        self.buttons = buttons
        self.keyboard = self.create_keyboard()
        self.message_id = self.bot.editMessageReplyMarkup((self.chat_id, self.message_id), reply_markup=self.keyboard)["message_id"]
        return self.message_id

    def delete(self):
        try:
            if self.sent:
                self.bot.deleteMessage((self.chat_id, self.message_id))
        except TelegramError:
            ...

"""
oooooooooooo       .o8   o8o      .              .o8       oooo            ooo        ooooo
`888'     `8      "888   `"'    .o8             "888       `888            `88.       .888'
 888          .oooo888  oooo  .o888oo  .oooo.    888oooo.   888   .ooooo.   888b     d'888   .ooooo.   .oooo.o  .oooo.o  .oooo.    .oooooooo  .ooooo.  
 888oooo8    d88' `888  `888    888   `P  )88b   d88' `88b  888  d88' `88b  8 Y88. .P  888  d88' `88b d88(  "8 d88(  "8 `P  )88b  888' `88b  d88' `88b 
 888    "    888   888   888    888    .oP"888   888   888  888  888ooo888  8  `888'   888  888ooo888 `"Y88b.  `"Y88b.   .oP"888  888   888  888ooo888 
 888       o 888   888   888    888 . d8(  888   888   888  888  888    .o  8    Y     888  888    .o o.  )88b o.  )88b d8(  888  `88bod8P'  888    .o 
o888ooooood8 `Y8bod88P" o888o   "888" `Y888""8o  `Y8bod8P' o888o `Y8bod8P' o8o        o888o `Y8bod8P' 8""888P' 8""888P' `Y888""8o `8oooooo.  `Y8bod8P' 
                                                                                                                                  d"     YD
                                                                                                                                  "Y88888P'
"""
class EditableMessage:
    def __init__(self, bot: Bot, chat_id, content: str, autosend: bool=True,
                 bold: bool=False, reply_markup=None) -> None:
        self.bot = bot
        self.bold = bold
        self.chat_id = chat_id
        self.content = content
        self.reply_markup = reply_markup
        self.sent = False
        if autosend:
            self.send()
    
    def send(self) -> int|None:
        if self.bold:
            self.content = f"<b>{self.content}</b>"
        try:
            self.message_id = self.bot.sendMessage(
                self.chat_id,
                self.content,
                parse_mode="HTML" if self.bold else None,
                reply_markup=self.reply_markup
            )["message_id"]
            self.sent = True
            return self.message_id
        except Exception:
            return None
    
    def edit(self, new_content: str, reply_markup=None) -> bool:
        if new_content.strip() == self.content.strip() and reply_markup == self.reply_markup:
            return False
        if self.bold:
            new_content = f"<b>{new_content}</b>"
        try:
            self.bot.editMessageText(
                (self.chat_id, self.message_id),
                new_content,
                parse_mode="HTML" if self.bold else None,
                reply_markup=reply_markup
            )
            self.content = new_content
            self.reply_markup = reply_markup
            return True
        except TelegramError:
            return False

    
    def delete(self) -> None:
        try:
            if self.sent:
                self.bot.deleteMessage((self.chat_id, self.message_id))
        except TelegramError:
            pass#since we have no way of notifying the user
    
    def delete_and_send(self, message: str) -> None:
        self.delete()
        self.bot.sendMessage(self.chat_id, message)

"""
      .o.                           o8o   o8o        .o.                    o8o                                  .    o8o
     .888.                          `"'   `"'       .888.                   `"'                                .o8    `"'
    .8"888.      .oooo.o  .ooooo.  oooo  oooo      .8"888.     ooo. .oo.   oooo  ooo. .oo.  .oo.    .oooo.   .o888oo oooo   .ooooo.  ooo. .oo.   
   .8' `888.    d88(  "8 d88' `"Y8 `888  `888     .8' `888.    `888P"Y88b  `888  `888P"Y88bP"Y88b  `P  )88b    888   `888  d88' `88b `888P"Y88b  
  .88ooo8888.   `"Y88b.  888        888   888    .88ooo8888.    888   888   888   888   888   888   .oP"888    888    888  888   888  888   888  
 .8'     `888.  o.  )88b 888   .o8  888   888   .8'     `888.   888   888   888   888   888   888  d8(  888    888 .  888  888   888  888   888  
o88o     o8888o 8""888P' `Y8bod8P' o888o o888o o88o     o8888o o888o o888o o888o o888o o888o o888o `Y888""8o   "888" o888o `Y8bod8P' o888o o888o 
"""
class AsciiAnimation(EditableMessage):
    def __init__(self, bot, chat_id, frames, autosend=True, bold=False):
        super().__init__(bot, chat_id, content=frames[0], autosend=autosend, bold=bold)
        self.frames = frames
    
    def play(self, repeat: int):
        for i in range(repeat):
            for frame in self.frames:
                self.edit(frame)
                sleep(0.5)

"""
ooooo                                  .o8   o8o                         oooooooooo.
`888'                                 "888   `"'                         `888'   `Y8b
 888          .ooooo.   .oooo.    .oooo888  oooo  ooo. .oo.    .oooooooo  888     888  .oooo.   oooo d8b 
 888         d88' `88b `P  )88b  d88' `888  `888  `888P"Y88b  888' `88b   888oooo888' `P  )88b  `888""8P 
 888         888   888  .oP"888  888   888   888   888   888  888   888   888    `88b  .oP"888   888     
 888       o 888   888 d8(  888  888   888   888   888   888  `88bod8P'   888    .88P d8(  888   888     
o888ooooood8 `Y8bod8P' `Y888""8o `Y8bod88P" o888o o888o o888o `8oooooo.  o888bood8P'  `Y888""8o d888b    
                                                              d"     YD
                                                              "Y88888P'
"""
class LoadingBar:
    def __init__(self, total: int, chat_id: int, bot: Bot, autosend: bool=True,
                 autodelete: bool=True, showperc: bool=True, label=None,
                 spinner_enabled: bool=True, full_char: str="🔲", empty_char="🔶",
                 spinner_frames=all_spinners["braille"], spinner_pos: str="left",
                 bar_lenght: int=10, pin_message: bool=False, cancel_button: bool=True,
                 on_complete: Callable = None):
        
        self.bot = bot
        self.tot = int(total)
        self.chat_id = chat_id
        self.showperc = showperc
        self.label = label
        self.autodelete = autodelete
        self.spinner_enabled = spinner_enabled
        self.full_char = full_char
        self.empty_char = empty_char
        self.spinner = spinner_frames
        self.spinner_index = 0
        self.spinner_delay = 0.2
        self.spinner_pos = spinner_pos
        self.bar_lenght = bar_lenght
        self.progress = 0
        self.done = False #if the bar was stopped or completed
        self.completed = False # if the bar reached 100%
        self.deleted = False
        self.pin_message = pin_message
        self.cancel_button = cancel_button
        self.on_complete = on_complete
        self.parse_mode = "HTML"
        if cancel_button:
            self.canceled = False
        self.ETDMessage = None

        if autosend:
            self.setup()

    def get_bar(self):
        self.perc_progress = min(round((self.progress / self.tot) * 100, 1), 100)
        self.int_perc_progress = int(self.perc_progress)
        bar = self.full_char * (self.int_perc_progress//self.bar_lenght) + \
              self.empty_char * (self.bar_lenght - (self.int_perc_progress//self.bar_lenght))
        if self.showperc:
            bar += f" {self.perc_progress}%"
        if self.label:
            bar = f"{self.label}\n{bar}"
        if self.spinner_enabled:
            bar = f"<code>{self.spinner[self.spinner_index]}{bar}</code>" if self.spinner_pos=="left" else f"<code>{bar}{self.spinner[self.spinner_index]}</code>"
        return bar

    def setup(self):
        bar_text = self.get_bar()
        reply_markup = None
        if self.cancel_button:
            keyboard = [[InlineKeyboardButton(text="Cancel", callback_data=f"cancel_loading:{id(self)}")]]
            reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

        self.ETDMessage = self.bot.sendMessage(self.chat_id, bar_text, reply_markup=reply_markup, parse_mode=self.parse_mode)
        
        if self.pin_message:
            self.bot.pinChatMessage(self.chat_id, self.ETDMessage["message_id"])
        
        if self.spinner_enabled:
            t = Thread(target=self.spinner_cycle)
            t.start()

    def spinner_cycle(self):
        while not self.done and self.progress < self.tot:
            self.spinner_index = (self.spinner_index + 1) % len(self.spinner)
            self.update()
            sleep(self.spinner_delay)

    def update(self, new_progress: int=None):
        if new_progress is not None:
            self.progress = new_progress
        if self.perc_progress >= 100:
            self.completed = True
            self.done = True
        if self.completed and self.on_complete:
            self.on_complete()
        if self.canceled:
            self.cancel()
        if self.done:
            return
        try:
            self.bot.editMessageText(
                (self.chat_id, self.ETDMessage["message_id"]),
                self.get_bar(),
                reply_markup=self.ETDMessage.get("reply_markup"),  # keep the cancel button,
                parse_mode=self.parse_mode
            )
        except TelegramError:
            ...

    def cancel(self):
        self.done = True
        self.delete()

    def delete(self):
        try:
            if not self.deleted:
                self.deleted = True
                self.bot.deleteMessage((self.chat_id, self.ETDMessage["message_id"]))
        except TelegramError as e:
            print("cant delete this shit", e)

    def fill_and_delete(self) -> None:
        self.set100()
        self.delete()
    
    def set100(self):
        try:
            self.progress = self.tot
            self.update()
        except:...

"""
ooooo                                  .o8   o8o                         oooooooooo.
`888'                                 "888   `"'                         `888'   `Y8b
 888          .ooooo.   .oooo.    .oooo888  oooo  ooo. .oo.    .oooooooo  888     888  .oooo.   oooo d8b
 888         d88' `88b `P  )88b  d88' `888  `888  `888P"Y88b  888' `88b   888oooo888' `P  )88b  `888""8P
 888         888   888  .oP"888  888   888   888   888   888  888   888   888    `88b  .oP"888   888
 888       o 888   888 d8(  888  888   888   888   888   888  `88bod8P'   888    .88P d8(  888   888
o888ooooood8 `Y8bod8P' `Y888""8o `Y8bod88P" o888o o888o o888o `8oooooo.  o888bood8P'  `Y888""8o d888b
                                                              d"     YD
                                                              "Y88888P'
oooooo   oooooo     oooo                    oooo
 `888.    `888.     .8'                     `888
  `888.   .8888.   .8'    .ooooo.  oooo d8b  888  oooo   .ooooo.  oooo d8b
   `888  .8'`888. .8'    d88' `88b `888""8P  888 .8P'   d88' `88b `888""8P
    `888.8'  `888.8'     888   888  888      888888.    888ooo888  888
     `888'    `888'      888   888  888      888 `88b.  888    .o  888
      `8'      `8'       `Y8bod8P' d888b    o888o o888o `Y8bod8P' d888b
"""
class LoadingBarTimedWorker:
    def __init__(
        self,
        label: str,
        duration: int,
        chat_id: int,
        bot: Bot,
        target: Callable,
        on_cancel: Callable|None=None,
        on_complete: Callable|None=None,
        block_default_cancel: bool = False,
        args=(),
        loading_bar_kwargs: dict = {}
    ) -> None:
        self._duration = duration
        self._target = target
        self._args = args
        self._label = label
        self.on_complete = on_complete
        self._loading_bar = LoadingBar(duration, chat_id, bot, False, label=label, on_complete=on_complete, **loading_bar_kwargs)
        self.running = False
        self.on_cancel = on_cancel
        self.block_default_cancel = block_default_cancel
        self._thread: CancellableThread | None = None   # ← store reference
        self.worker_name = f"Worker-{self._label}"
        print(f"[LoadingBarTimedWorker]({self.worker_name}) Initialized bar")

    def get_loading_bar(self) -> LoadingBar:
        return self._loading_bar

    def stop(self) -> None:
        if not self.running:
            raise RuntimeError("The process was not running.")

        try:
            print(f"[LoadingBarTimedWorker]({self.worker_name}) {self.on_cancel=}")
            if self.on_cancel:
                self.on_cancel()
        except Exception as e:
            print(f"[LoadingBarTimedWorker]({self.worker_name}) error executing on_cancel function:\n{e}")

        if self._thread and self._thread.is_alive():
            print(f"[{self._label}] Cancelling thread...")
            if self.block_default_cancel:
                return
            self._thread.cancel()
            # Give it time to notice and exit gracefully
            self._thread.join(timeout=2.0)
            if self._thread.is_alive():
                print(f"[{self._label}] Thread did not stop in time (timeout hit)")
            else:
                print(f"[{self._label}] Thread stopped cleanly")

    def start(self) -> None:
        self.running = True

        # No forced wrapper — target is called directly
        self._thread = CancellableThread(
            target=self._target,
            args=self._args,
            name=f"Worker-{self._label}",
            daemon=True
        )
        self._thread.start()

        self._loading_bar.setup()
        start_time = perf_counter()

        while True:
            if self._loading_bar.canceled:
                print(f"[LoadingBarTimedWorker] {self.worker_name} stopping...")
                self._thread.cancel()   # ← sets event automatically
                self.stop()
                print(f"[LoadingBarTimedWorker] {self.worker_name} stopped.")
                break

            elapsed = perf_counter() - start_time
            self._loading_bar.update(elapsed)

            if self._loading_bar.completed or self._loading_bar.done:
                break

            sleep(0.4)

        self.running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        self._loading_bar.fill_and_delete()