import inspect
import functools
import threading
from time import sleep
from typing import Callable, Any


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


class CancellableThread(threading.Thread):
    """
    Smart cancellable thread:
    - Accepts forced 'thread' as first positional arg (for backward compatibility)
    - Converts it to cancel_event kwarg if target accepts it
    - Or ignores it if target doesn't need cancellation
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
            # Prepare call args/kwargs
            real_args = list(self._args)
            real_kwargs = self._kwargs.copy()

            # If target expects 'thread' as first positional → provide it
            # Otherwise, convert to cancel_event kwarg if accepted
            sig = inspect.signature(self._target)

            if "thread" in sig.parameters and sig.parameters["thread"].kind in (
                inspect.Parameter.POSITIONAL_ONLY,
                inspect.Parameter.POSITIONAL_OR_KEYWORD
            ):
                # Old style: pass thread as positional
                real_args.insert(0, self)
            elif "cancel_event" in sig.parameters:
                # Modern style: pass as keyword
                real_kwargs["cancel_event"] = self._cancel_event

            # Run the target
            self._result = self._target(*real_args, **real_kwargs)

        except Exception as e:
            self._exception = e
            raise

    def join(self, timeout: float | None = None) -> bool:
        super().join(timeout)
        return not self.is_alive()

    @property
    def result(self) -> Any:
        if self._exception:
            raise self._exception
        return self._result