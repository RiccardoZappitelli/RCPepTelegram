import re
from time import sleep
import subprocess as sp
from threading import Thread
from subprocess import CREATE_NO_WINDOW

PROMPT_RE = re.compile(
    r'^([A-Z]:\\(?:[^\\<>:"/|?*\r\n]+\\)*[^\\<>:"/|?*\r\n]*)>.*$' #I hate this
)

def extract_cwd_from_prompt(line: str) -> str | None:
    m = PROMPT_RE.match(line)
    return m.group(1) if m else None


class CMDSession:
    def __init__(self, remove_prompt: bool = True, command_line: str = "cmd.exe"):
        self.last_input: str = ""
        self.remove_prompt = remove_prompt
        self.reading_allowed = True
        self.cwd: str | None = None

        self.cmd_session = sp.Popen(
            [command_line],
            stdout=sp.PIPE,
            stderr=sp.PIPE,
            stdin=sp.PIPE,
            text=True,
            bufsize=1,
            encoding="mbcs",
            creationflags=CREATE_NO_WINDOW
        )

    def kill(self) -> None:
        self.write_input("exit")
        self.cmd_session.stdin.close()
        self.cmd_session.wait()
        self.cmd_session.kill()

    def read_output(self, parsing_function=print):
        self.reading_allowed = True
        while self.reading_allowed:
            line = self.cmd_session.stdout.readline()
            if not line:
                break

            line = line.rstrip("\r\n")

            cwd = extract_cwd_from_prompt(line)
            if cwd:
                self.cwd = cwd
                print(f"CMDSession Debug: {self.cwd=}")
                if self.remove_prompt:
                    continue

            parsing_function(line)

    def read_error(self, parsing_function=print):
        self.reading_allowed = True
        while self.reading_allowed:
            line = self.cmd_session.stderr.readline()
            if not line:
                break
            parsing_function(line.rstrip("\r\n"))

    def run_output_reader_thread(self, parsing_function_output=print, parsing_function_error=print):
        Thread(target=self.read_output, args=(parsing_function_output,), daemon=True).start()
        Thread(target=self.read_error, args=(parsing_function_error,), daemon=True).start()

    def stop_output_readed_thread(self):
        self.reading_allowed = False

    def write_input(self, message: str):
        self.last_input = message
        self.cmd_session.stdin.write(message + "\n")
        self.cmd_session.stdin.flush()

    def get_cwd(self) -> str | None:
        """Return last known working directory (cached from prompt)."""
        return self.cwd