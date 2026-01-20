import cv2
import mss
import ctypes
import numpy as np
from os import remove
from time import sleep, time
from PIL import Image, ImageTk
from os.path import join, exists
from moviepy.editor import VideoFileClip
from tkinter import Tk, Canvas, Label, NW
from random import randint, choice, uniform, random

from .audio_player import play_wav


class OverlayManager:
    def __init__(self, pep, burn_directory: str):
        self.pep = pep
        self.root = None
        self.burn_dir = burn_directory

    def _safe_destroy(self):
        try:
            if self.root:
                self.root.destroy()
        except:
            pass
        self.root = None

    def whisper_overlay(self, duration, whispers=None):
        if whispers is None:
            whispers = [
                "can you hear me", "i'm here", "look behind you", "don't turn around",
                "i can see you", "you're not alone", "the screen", "close your eyes",
                "i'm in the room", "check the door", "someone's behind you", "don't look",
                "i know you're there", "your reflection", "the window", "i'm watching",
                "not alone", "behind the screen", "in your system", "can you see me",
                "turn around", "i'm closer", "the darkness", "your shadow", "in the corner",
                "don't scream", "it's me", "behind you", "i'm inside", "the silence"
            ]
        elif isinstance(whispers, str):
            whispers = whispers.split(",")

        def run():
            try:
                self.root = Tk()
                self.root.overrideredirect(True)
                self.root.attributes("-topmost", 1)
                self.root.attributes("-transparentcolor", "black")
                self.root.config(bg="black")

                w, h = 250, 30
                sw = self.root.winfo_screenwidth()
                sh = self.root.winfo_screenheight()
                self.root.geometry(f"{w}x{h}+{sw-w-10}+{sh-h-10}")

                label = Label(self.root, fg="#8B0000", bg="black", font=("Segoe UI", 9))
                label.pack(expand=True)

                start = time()
                last = 0
                bar = self.pep.new_loading_bar(duration, label="👻 Whisper Overlay")

                def update():
                    nonlocal last
                    now = time()
                    bar.update(now - start)

                    if bar.canceled:
                        bar.fill_and_delete()
                        self._safe_destroy()
                        return

                    if now - last > uniform(2, 5):
                        label.config(text=choice(whispers))
                        last = now

                        if random() < 0.3:
                            for a in (0.3, 0.7, 1, 0.7, 0.3):
                                self.root.attributes("-alpha", a)
                                self.root.update()
                                sleep(0.05)
                            self.root.attributes("-alpha", 1)

                    if now - start < duration:
                        self.root.after(100, update)
                    else:
                        bar.fill_and_delete()
                        self._safe_destroy()

                self.root.after(100, update)
                self.root.mainloop()

            except:
                self._safe_destroy()

        run()

    def video_note_overlay(self, path):
        TRANSPARENT_COLOR = "#FF00FF"
        temp_audio = join(self.burn_dir, f"{randint(100000,999999)}.wav")

        try:
            clip = VideoFileClip(path)
            if clip.audio:
                clip.audio.write_audiofile(temp_audio, logger=None)
                play_wav(temp_audio)
            clip.close()
        except:
            pass

        cap = cv2.VideoCapture(path)
        fps = cap.get(5) or 30
        delay = int(1000 / fps)

        try:
            self.root = Tk()
            self.root.overrideredirect(True)
            self.root.attributes("-topmost", 1)
            self.root.attributes("-transparentcolor", TRANSPARENT_COLOR)
            self.root.config(bg=TRANSPARENT_COLOR)

            size = 300
            sw = self.root.winfo_screenwidth()
            sh = self.root.winfo_screenheight()
            self.root.geometry(f"{size}x{size}+{sw-size-10}+{sh-size-10}")

            canvas = Canvas(
                self.root,
                width=size,
                height=size,
                bg=TRANSPARENT_COLOR,
                highlightthickness=0
            )
            canvas.pack()

            # Allow the overlay window to be dragged with the mouse
            def start_move(event):
                self.root.x = event.x
                self.root.y = event.y

            def stop_move(event):
                self.root.x = None
                self.root.y = None

            def do_move(event):
                deltax = event.x - self.root.x
                deltay = event.y - self.root.y
                x = self.root.winfo_x() + deltax
                y = self.root.winfo_y() + deltay
                self.root.geometry(f"+{x}+{y}")

            canvas.bind('<Button-1>', start_move)
            canvas.bind('<ButtonRelease-1>', stop_move)
            canvas.bind('<B1-Motion>', do_move)

            self.root.bind('<Escape>', lambda e: self._safe_destroy())

            def frame():
                ret, img = cap.read()
                if not ret:
                    cap.release()
                    self._safe_destroy()
                    if exists(temp_audio):
                        remove(temp_audio)
                    return

                h, w = img.shape[:2]
                s = min(h, w)
                img = img[(h-s)//2:(h+s)//2, (w-s)//2:(w+s)//2]

                # Generate a circular mask to clip the video into a round shape
                mask = np.zeros((s, s), np.uint8)
                cv2.circle(mask, (s//2, s//2), s//2, 255, -1)

                out = np.full((s, s, 3), (255, 0, 255), dtype=np.uint8)

                for i in range(3):
                    out[:, :, i] = np.where(mask == 255, img[:, :, i], out[:, :, i])

                pil = Image.fromarray(
                    cv2.cvtColor(out, cv2.COLOR_BGR2RGB)
                ).resize((size, size))

                if pil.mode != 'RGBA':
                    pil = pil.convert('RGBA')

                tkimg = ImageTk.PhotoImage(pil)
                canvas.img = tkimg
                canvas.delete("all")
                canvas.create_image(0, 0, anchor=NW, image=tkimg)

                self.root.after(delay, frame)

            frame()
            self.root.mainloop()

        except Exception as e:
            print(f"Error in video overlay: {e}")
            cap.release()
            self._safe_destroy()


class OpenCVOverlayPlayer:
    def __init__(self, name="overlay"):
        self.name = name
        self.stop_flag = False
        self.prev_frame = None
        self.elapsed = -1

    def hide_cursor(self):
        ctypes.windll.user32.ShowCursor(False)

    def show_cursor(self):
        ctypes.windll.user32.ShowCursor(True)

    def setup(self):
        cv2.namedWindow(self.name, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(self.name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.setWindowProperty(self.name, cv2.WND_PROP_TOPMOST, 1)

    def run(self, timeout):
        self.hide_cursor()
        self.setup()
        start = time()

        with mss.mss() as sct:
            while time() - start < timeout and not self.stop_flag:
                frame = np.array(sct.grab(sct.monitors[1]))[:, :, :3]
                out = self.process_frame(frame, time() - start)
                cv2.imshow(self.name, out)
                if cv2.waitKey(1) & 0xFF == 27:
                    break

        self.cleanup()

    def cleanup(self):
        cv2.destroyAllWindows()
        self.show_cursor()

    def process_frame(self, frame, elapsed):
        h, w, _ = frame.shape

        # Base blur
        blur = cv2.GaussianBlur(frame, (21, 21), 0)
        blur = cv2.convertScaleAbs(blur, alpha=0.6, beta=10)

        if self.prev_frame is not None:
            # Gradually blend previous distorted frame with current frame
            decay = 0.85  # 1 = full glitch, 0 = normal frame
            blur = cv2.addWeighted(blur, 1 - decay, self.prev_frame, decay, 0)

        self.prev_frame = blur.copy()
        out = blur.copy()

        # Horizontal glitch bands
        glitch_intensity = max(1.0 - elapsed/5, 0)  # gradually fade over 5 seconds
        for _ in range(int(randint(10, 25) * glitch_intensity)):
            y = randint(0, h - 2)
            band = randint(3, 12)
            offset = int(randint(-60, 60) * glitch_intensity)
            out[y:y + band] = np.roll(out[y:y + band], offset, axis=1)

        # RGB channel desync
        b, g, r = cv2.split(out)
        r_offset = int(randint(-15, 15) * glitch_intensity)
        g_offset = int(randint(-15, 15) * glitch_intensity)
        r = np.roll(r, r_offset, axis=1)
        g = np.roll(g, g_offset, axis=0)
        out = cv2.merge((b, g, r))

        # Noise
        noise_amp = int(55 * glitch_intensity)
        if noise_amp > 0:
            noise = np.random.normal(0, noise_amp, out.shape).astype(np.int16)
            out = np.clip(out.astype(np.int16) + noise, 0, 255).astype(np.uint8)

        # Occasional sharpening spike, also decays
        if random() < 0.05 * glitch_intensity:
            out = cv2.filter2D(out, -1, np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]]))

        # Scanline effect
        if int(elapsed * 25) % 2 == 0:
            out[::2] = (out[::2] * (0.65 + 0.35*(1-glitch_intensity))).astype(np.uint8)

        return out
