import inspect
import functools
import threading
from time import sleep
from typing import Callable, Any


#The functions that contains a GIL blocking function must have cancel event argument
def cancellable(check_interval: float = 0.08):
    """
    Decorator that adds automatic cancellation checking.
    Wraps the function in a loop that checks cancel_event every ~0.08s.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, cancel_event=None, **kwargs):
            if cancel_event is None:
                # No cancellation → run once normally
                return func(*args, **kwargs)

            result = None
            while not cancel_event.is_set():
                try:
                    result = func(*args, **kwargs)
                    # If function returns → stop after first run
                    if result is not None:
                        break
                except Exception as e:
                    print(f"Function error: {e}")
                    break

                sleep(check_interval)  # frequent check

            print("Function stopped by cancel_event")
            return result

        return wrapper

    return decorator


#The functions that contains a GIL blocking function must have cancel event argument
class CancellableThread(threading.Thread):
    """
    Cancellable thread that:
    - Automatically passes cancel_event=None as kwarg if the target function accepts it
    - Does NOT force any positional arguments
    - Target can check cancel_event.is_set() to stop gracefully
    - .cancel() sets the event and runs optional cleanup
    """
    def __init__(
        self,
        target: Callable,
        args=(),
        kwargs=None,
        name: str = "",
        daemon: bool = True,
        on_cancel: Callable[[], None] | None = None,
    ):
        super().__init__(name=name, daemon=daemon)
        self._target = target
        self._args = args
        self._kwargs = kwargs or {}
        self._cancel_event = threading.Event()
        self._on_cancel = on_cancel
        self._result = None
        self._exception = None

    def cancel(self):
        """Signal cancellation and run cleanup if provided"""
        self._cancel_event.set()
        if self._on_cancel:
            try:
                self._on_cancel()
            except Exception as e:
                print(f"Cleanup error on cancel: {e}")

    def is_cancelled(self) -> bool:
        return self._cancel_event.is_set()

    def run(self):
        try:
            # Prepare kwargs — add cancel_event ONLY if the function accepts it
            call_kwargs = self._kwargs.copy()
            sig = inspect.signature(self._target)
            if "cancel_event" in sig.parameters:
                print("[CancellableThread] Cancel event is set")
                call_kwargs["cancel_event"] = self._cancel_event
            else:
                print("[CancellableThread] Cancel event is set")

            self._result = self._target(*self._args, **call_kwargs)

        except Exception as e:
            self._exception = e
            raise  # let it propagate (you can log/catch higher up)

    def join(self, timeout: float | None = None) -> bool:
        super().join(timeout)
        return not self.is_alive()

    @property
    def result(self) -> Any:
        if self._exception:
            raise self._exception
        return self._result