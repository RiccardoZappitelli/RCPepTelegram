import subprocess as sp

class CMDSession:
    def __init__(self):
        self.cmd_session = sp.Popen(
            ["cmd.exe"],
            stdout=sp.PIPE,
            stderr=sp.PIPE,
            stdin=sp.PIPE,
            text=True,
            bufsize=1,
        )
    
    def read_output(self, parsing_function=print):
        """Read stdout line by line and print."""
        while True:
            line = self.cmd_session.stdout.readline()
            if not line:
                break
            parsing_function(line)
    
    def read_error(self, parsing_function=print):
        """Read stderr line by line and print."""
        while True:
            line = self.cmd_session.stderr.readline()
            if not line:
                break
            parsing_function(line)
    
    def write_input(self, message: str):
        """Write message to stdin."""
        self.cmd_session.stdin.write(message + "\n")
        self.cmd_session.stdin.flush()
    
    def exit(self):
        """Exit the cmd session."""
        self.write_input("exit")
        self.cmd_session.stdin.close()
        self.cmd_session.wait()