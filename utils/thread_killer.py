import threading
import time
import functools

def stoppable(func):
    """Decorator to make functions 'stoppable'"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        thread = threading.current_thread()
        thread._stop_requested = False
        
        def check_stop():
            if getattr(thread, '_stop_requested', False):
                raise StopThread()
        
        # Inject stop checks
        original_sleep = time.sleep
        def checked_sleep(seconds):
            elapsed = 0
            while elapsed < seconds:
                check_stop()
                original_sleep(min(0.1, seconds - elapsed))
                elapsed += 0.1
        
        # Monkey patch time.sleep in this thread only
        import time
        time.sleep = checked_sleep
        
        try:
            return func(*args, **kwargs, _stop_check=check_stop)
        except StopThread:
            return None
        finally:
            time.sleep = original_sleep
    
    return wrapper

class StopThread(Exception):
    pass

class ThreadWithStop(threading.Thread):
    def __init__(self, target, *args, **kwargs):
        super().__init__(target=stoppable(target), *args, **kwargs)
    
    def stop(self):
        """'Stop' the thread by raising an exception in it"""
        self._stop_requested = True

# Usage
@stoppable
def my_task(_stop_check=None):
    for i in range(10):
        print(f"Working {i}")
        time.sleep(1)  # Automatically checks for stop
        if _stop_check:
            _stop_check()  # Manual check

thread = ThreadWithStop(target=my_task)
thread.start()
time.sleep(3)
thread.stop()  # Works!
thread.join()