import cv2
import numpy as np
import mss
import random
import time
import ctypes
from abc import ABC, abstractmethod


class OverlayPlayer(ABC):
    """Base class for fullscreen overlays with timeout functionality."""
    
    def __init__(self, window_name="overlay"):
        """
        Initialize overlay player.
        
        Args:
            window_name: Name of the OpenCV window (default: "overlay")
        """
        self.window_name = window_name
        self.stop_flag = False
        self.prev_frame = None
        self.elapsed = -1
        
    def hide_cursor(self):
        """Hide the system cursor."""
        ctypes.windll.user32.ShowCursor(False)
    
    def show_cursor(self):
        """Restore the system cursor."""
        ctypes.windll.user32.ShowCursor(True)
    
    def setup_window(self):
        """Setup fullscreen topmost window."""
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.setWindowProperty(self.window_name, cv2.WND_PROP_TOPMOST, 1)
    
    @abstractmethod
    def process_frame(self, frame, elapsed_time):
        """
        Process a single frame. Must be implemented by subclasses.
        
        Args:
            frame: Input frame to process
            elapsed_time: Time elapsed since overlay started
            
        Returns:
            Processed frame
        """
        pass
    
    def capture_screen(self, sct, monitor_index=1):
        """
        Capture the screen.
        
        Args:
            sct: mss instance
            monitor_index: Monitor index to capture (default: 1 = primary monitor)
            
        Returns:
            Captured frame as numpy array
        """
        monitor = sct.monitors[monitor_index]
        return np.array(sct.grab(monitor))[:, :, :3]

    def stop(self):
        """Manually stop the overlay."""
        self.stop_flag = True
        self.cleanup()

    def get_elapsed_time(self) -> int:
        return self.elapsed
    
    def run(self, timeout_seconds):
        """
        Run the overlay with timeout.
        
        Args:
            timeout_seconds: Duration to display overlay (default: 10)
            
        Returns:
            True if completed successfully (timeout reached), False if terminated early
        """
        self.stop_flag = False
        self.prev_frame = None  # Reset for new run
        self.hide_cursor()
        
        with mss.mss() as sct:
            self.setup_window()
            start = time.time()
            
            while True:
                if self.stop_flag:
                    break
                self.elapsed = time.time() - start
                if self.elapsed >= timeout_seconds:
                    break
                frame = self.capture_screen(sct)
                processed = self.process_frame(frame, self.elapsed)
                cv2.imshow(self.window_name, processed)
                key = cv2.waitKey(1)
                if cv2.getWindowProperty(self.window_name, cv2.WND_PROP_VISIBLE) < 1:
                    self.stop_flag = True
                    break
        
        self.stop_flag = True
        self.cleanup()
        # Return True if completed due to timeout, False if stopped early
        return self.elapsed >= timeout_seconds if self.elapsed != -1 else False
    
    def cleanup(self):
        """Cleanup resources."""
        try:
            cv2.destroyAllWindows()
        except:
            pass
        self.show_cursor()
        self.elapsed = -1
        self.stop_flag = False


class HDMIDrownedOverlay(OverlayPlayer):
    """HDMI corruption overlay with drowned-signal effect."""
    
    def __init__(self):
        """Initialize HDMI drowned overlay."""
        super().__init__(window_name="hdmi_drowned")
        
    def process_frame(self, frame, elapsed_time):
        """
        Apply heavy signal degradation so the image is barely visible.
        
        Args:
            frame: Input frame to process
            elapsed_time: Time elapsed since overlay started
            
        Returns:
            Processed frame with HDMI corruption effect
        """
        h, w, _ = frame.shape
        
        # Initial blur and contrast adjustment
        blur = cv2.GaussianBlur(frame, (21, 21), 0)
        blur = cv2.convertScaleAbs(blur, alpha=0.6, beta=10)
        
        # Frame blending for persistence effect
        if self.prev_frame is None:
            mixed = blur
        else:
            mixed = cv2.addWeighted(blur, 0.6, self.prev_frame, 0.4, 0)
        
        self.prev_frame = mixed.copy()
        out = mixed.copy()
        
        # Horizontal line distortions
        for _ in range(random.randint(10, 25)):
            y = random.randint(0, h - 2)
            band = random.randint(3, 12)
            offset = random.randint(-60, 60)
            out[y:y+band] = np.roll(out[y:y+band], offset, axis=1)
        
        # RGB channel shifting
        b, g, r = cv2.split(out)
        r = np.roll(r, random.randint(-15, 15), axis=1)
        g = np.roll(g, random.randint(-15, 15), axis=0)
        out = cv2.merge((b, g, r))
        
        # Add noise
        noise = np.random.normal(0, 55, out.shape).astype(np.int16)
        out = np.clip(out.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        
        # Occasional sharpening
        if random.random() < 0.05:
            kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
            out = cv2.filter2D(out, -1, kernel)
        
        # Flicker effect
        if int(elapsed_time * 25) % 2 == 0:
            out[::2] = (out[::2] * 0.65).astype(np.uint8)
        
        return out