import re
from time import sleep
import subprocess as sp
from threading import Thread
from subprocess import CREATE_NO_WINDOW

def is_cmd_prompt(line: str) -> bool:
    pattern = r'^[A-Z]:\\(?:[^\\<>:"/|?*\r\n]+\\)*[^\\<>:"/|?*\r\n]*>.*$'
    return bool(re.match(pattern, line))

class CMDSession:
    def __init__(self, remove_prompt: bool = True):
        self.last_input: str = ""
        self.remove_prompt = remove_prompt
        self.reading_allowed = True
        self.cmd_session = sp.Popen(
            ["cmd.exe"],
            stdout=sp.PIPE,
            stderr=sp.PIPE,
            stdin=sp.PIPE,
            text=True,
            bufsize=1,
            encoding="mbcs",
            creationflags=CREATE_NO_WINDOW
        )
    
    def read_output(self, parsing_function=print):
        while self.reading_allowed:
            line = self.cmd_session.stdout.readline()
            if not line:
                break
            if not is_cmd_prompt(line) and self.remove_prompt:
                parsing_function(line)
    
    def read_error(self, parsing_function=print):
        while self.reading_allowed:
            line = self.cmd_session.stderr.readline()
            if not line:
                break
            if not is_cmd_prompt(line) and self.remove_prompt:
                parsing_function(line)

    def stop_output_readed_thread(self):
        self.reading_allowed = False
        sleep(.25)
        self.reading_allowed = True

    def run_output_reader_thread(self, parsing_function_output=print, parsing_function_error=print):
        oth = Thread(target=self.read_output, args=(parsing_function_output,))
        eth = Thread(target=self.read_error, args=(parsing_function_error,))
        oth.start()
        eth.start()
    
    def write_input(self, message: str):
        """Write message to stdin."""
        self.last_input = message
        self.cmd_session.stdin.write(message + "\n")
        self.cmd_session.stdin.flush()
    
    def exit(self):
        """Exit the cmd session."""
        self.write_input("exit")
        self.cmd_session.stdin.close()
        self.cmd_session.wait()