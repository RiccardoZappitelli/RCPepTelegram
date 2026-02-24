import sys
import threading
from typing import Optional, Callable


class DebugLogger:
    def __init__(self):
        self._lock = threading.RLock()
        self._stdout_orig = None
        self._stderr_orig = None
        self._buffer: list[str] = []
        self._binds: dict[str, Callable[[], None]] = {}   # string → callback function

    def _write(self, s: str, orig):
        with self._lock:
            self._buffer.append(s)

            # Check all registered bindings
            for trigger_str, callback in list(self._binds.items()):
                if trigger_str in s:          # substring match (case sensitive)
                    try:
                        callback()            # call the function
                    except Exception as e:
                        # Prevent bind callback from breaking logging
                        self._buffer.append(
                            f"[DebugLogger] Error in bind callback for '{trigger_str}': {e}\n"
                        )

            orig(s)  # uncomment if you want console output too

    def bind(self, string: str, function: Callable[[], None]):
        """
        Whenever 'string' appears in stdout/stderr output,
        automatically call function().
        
        Example:
            logger.bind("camera opened", lambda: print("CAMERA READY!"))
            logger.bind("ERROR", lambda: bot.bsend("⚠️ Something broke!"))
        """
        with self._lock:
            self._binds[string] = function

    def unbind(self, string: str) -> bool:
        """Remove a previously bound trigger. Returns True if it existed."""
        with self._lock:
            return self._binds.pop(string, None) is not None

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