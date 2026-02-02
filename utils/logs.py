import sys
import threading
from typing import Optional, Callable

class DebugLogger:
    def __init__(self):
        self._lock = threading.RLock()
        self._stdout_orig = None
        self._stderr_orig = None
        self._buffer: list[str] = []

        #not implemented
        self._binds: dict[str, Callable] = {}

    def _write(self, s: str, orig):
        with self._lock:
            self._buffer.append(s)
            #orig(s) #uncommenting this will re-enable console logging

    # Not Implemented Yet
    def bind(self, string, function):
        "Intercepts strings in the stdout buffer and if 'string' is found it calls 'function'"
        raise NotImplemented
        self._binds.update({string: function})

    def activate(self):
        with self._lock:
            if self._stdout_orig is None:
                self._stdout_orig = sys.stdout.write
                self._stderr_orig = sys.stderr.write

                sys.stdout.write = lambda s: self._write(s, self._stdout_orig)
                sys.stderr.write = lambda s: self._write(s, self._stderr_orig)

    def disable(self):
        with self._lock:
            if self._stdout_orig is not None:
                sys.stdout.write = self._stdout_orig
                sys.stderr.write = self._stderr_orig
                self._stdout_orig = None
                self._stderr_orig = None

    def get_logs(self) -> Optional[str]:
        with self._lock:
            return "".join(self._buffer) if self._buffer else None

    def clear(self):
        with self._lock:
            self._buffer.clear()

    def __enter__(self):
        self.activate()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.disable()
        return False

