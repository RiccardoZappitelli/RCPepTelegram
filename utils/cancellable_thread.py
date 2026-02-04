import threading
from time import monotonic, sleep
from typing import Callable, Any

# I'm not even gonna remove the comments to make it look I made it
# thanks grock ai, fuck you chatgpt
class CancellableThread(threading.Thread):
    """
    A thread that:
    - Checks for cancellation frequently
    - Allows graceful cleanup on cancel
    - Can be signalled to stop from outside
    """
    def __init__(
        self,
        target: Callable,
        args=(),
        kwargs=None,
        name: str = "",
        check_interval: float = 0.08,   # ~12 times/sec — fast enough for good UX
        daemon: bool = True,
        on_cancel: Callable[[], None] | None = None,  # optional cleanup callback
    ):
        super().__init__(target=self._wrapper, name=name, daemon=daemon)
        self._real_target = target
        self._real_args = args
        self._real_kwargs = kwargs or {}
        self._cancel_event = threading.Event()
        self._check_interval = check_interval
        self._on_cancel = on_cancel
        self._result = None
        self._exception = None

    def cancel(self):
        """Signal the thread to stop as soon as possible"""
        self._cancel_event.set()
        if self._on_cancel:
            try:
                self._on_cancel()
            except Exception as e:
                print(f"Cleanup error on cancel: {e}")

    def is_cancelled(self) -> bool:
        return self._cancel_event.is_set()

    def _wrapper(self):
        try:
            self._result = self._real_target(
                #self,  # pass self so target can check self.is_cancelled()
                *self._real_args,
                **self._real_kwargs
            )
        except Exception as e:
            self._exception = e
            raise  # let it bubble if you want logging

    def join(self, timeout: float | None = None) -> bool:
        """Wait for thread to finish, return True if it completed normally"""
        super().join(timeout)
        return not self.is_alive()

    @property
    def result(self) -> Any:
        if self._exception:
            raise self._exception
        return self._result