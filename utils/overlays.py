import cv2
import mss
import ctypes
import qrcode
import numpy as np
from os import remove
from time import sleep, time
from PIL import Image, ImageTk
from os.path import join, exists
from moviepy.editor import VideoFileClip
from tkinter import Tk, Canvas, Label, NW, Frame
from random import randint, choice, uniform, random

from .audio_player import play_wav
from typing import Any


def screen_and_webcam_pic(cap: cv2.VideoCapture, screen: Any | str = None) -> tuple[bool, Any]:
    if screen is None:
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            shot = sct.grab(monitor)

        screen = np.array(shot)
        screen = cv2.cvtColor(screen, cv2.COLOR_BGRA2BGR)
    else:
        if isinstance(screen, str):
            if exists(screen):
                screen = cv2.imread(screen)
            else:
                return False, None

    ret, cam = cap.read()
    if not ret:
        return False, None

    cam_h, cam_w = cam.shape[:2]
    cam = cv2.resize(cam, (cam_w // 2, cam_h // 2))

    h, w = cam.shape[:2]
    screen[0:h, 0:w] = cam

    return True, screen


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

    def fake_bsod(self, duration: float = 20.0, qr_code_url: str = None):
        #this is ass
        try:
            self._safe_destroy()

            root = Tk()
            root.overrideredirect(True)
            root.attributes("-topmost", True)

            # Exact fullscreen geometry (no -fullscreen flag → no conflict)
            sw = root.winfo_screenwidth()
            sh = root.winfo_screenheight()
            root.geometry(f"{sw}x{sh}+0+0")
            root.configure(bg="#0078d4")

            # Main content frame
            frame = Frame(root, bg="#0078d4")
            frame.place(relx=0.5, rely=0.5, anchor="center")

            # Sad face + main title (exact offset & sizing from real BSOD)
            sad_title = Label(
                frame,
                text=":(\nYour PC ran into a problem and needs to restart. We're\njust collecting some error info, and then we'll restart for you.",
                font=("Segoe UI", 38, "bold"),
                fg="white",
                bg="#0078d4",
                justify="left"
            )
            sad_title.pack(anchor="w", padx=180, pady=(140, 60))

            # Secondary text block
            secondary_text = [
                "(0% complete)",
                "",
                "If you'd like to know more, you can search online for this error:",
                "CRITICAL_PROCESS_DIED",
                "",
                "Stop code: CRITICAL_PROCESS_DIED"
            ]

            for line in secondary_text:
                lbl = Label(
                    frame,
                    text=line,
                    font=("Segoe UI", 24),
                    fg="white",
                    bg="#0078d4",
                    anchor="w"
                )
                lbl.pack(anchor="w", padx=180, pady=6)

            # Progress section
            progress_frame = Frame(frame, bg="#0078d4")
            progress_frame.pack(pady=(80, 0), padx=180, fill="x")

            # Main progress bar (blue background + yellow fill)
            main_bar = Frame(progress_frame, bg="#005a9e", height=54, width=1400)
            main_bar.pack(fill="x", pady=(0, 30))
            main_fill = Frame(main_bar, bg="#ffff00", width=0, height=54)
            main_fill.place(x=0, y=0, relheight=1)

            main_percent = Label(
                main_bar,
                text="(0% complete)",
                font=("Segoe UI", 22, "bold"),
                fg="black",
                bg="#ffff00"
            )
            main_percent.place(relx=0.5, rely=0.5, anchor="center")

            # Secondary "Preparing Automatic Repair" bar (yellow pulsing)
            repair_bar = Frame(progress_frame, bg="#005a9e", height=54, width=1400)
            repair_bar.pack(fill="x")
            repair_fill = Frame(repair_bar, bg="#ffff00", width=0, height=54)
            repair_fill.place(x=0, y=0, relheight=1)

            repair_label = Label(
                repair_bar,
                text="Preparing Automatic Repair",
                font=("Segoe UI", 22, "bold"),
                fg="black",
                bg="#ffff00"
            )
            repair_label.place(relx=0.5, rely=0.5, anchor="center")

            # QR code area (real position: bottom right-ish)
            if qr_code_url:
                qr_container = Frame(frame, bg="#0078d4")
                qr_container.place(relx=0.82, rely=0.68, anchor="center")
                try:
                    import qrcode
                    qr = qrcode.QRCode(version=1, box_size=10, border=4)
                    qr.add_data(qr_code_url)
                    qr.make(fit=True)
                    qr_img = qr.make_image(fill_color="black", back_color="white")
                    qr_photo = ImageTk.PhotoImage(qr_img)
                    qr_label = Label(qr_container, image=qr_photo, bg="#0078d4")
                    qr_label.image = qr_photo
                    qr_label.pack()
                    Label(qr_container, text="Scan to get help", font=("Segoe UI", 18),
                        fg="#ffff00", bg="#0078d4").pack(pady=8)
                except:
                    Label(qr_container, text="QR code area", font=("Segoe UI", 18),
                        fg="#ffff00", bg="#0078d4").pack(pady=8)

            start_time = time()

            def update_progress():
                if not root.winfo_exists():
                    return

                elapsed = time() - start_time
                if elapsed >= duration:
                    self._safe_destroy()
                    return

                prog = min(int(elapsed / duration * 100), 99)

                # Main bar
                fill_w = int(1400 * (prog / 100))
                main_fill.configure(width=fill_w)
                main_percent.configure(text=f"({prog}% complete)")

                # Pulsing yellow bar
                pulse = (elapsed * 3.5) % 100
                pulse_w = int(1400 * (pulse / 100))
                repair_fill.configure(width=pulse_w)

                # Blinking cursor
                if int(elapsed * 5) % 2 == 0:
                    main_percent.configure(text=f"({prog}% complete) _")
                else:
                    main_percent.configure(text=f"({prog}% complete)")

                root.after(180, update_progress)  # ~5.5 fps update

            update_progress()
            root.mainloop()

        except Exception as e:
            print(f"BSOD overlay failed: {e}")
            self._safe_destroy()

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

    def qr_overlay(self, url: str, custom_text: str = "Scan me", 
               duration: float | None = None, position: str = "center",
               text_color: str = "#00ff00", bg_color: str = "black",
               qr_size: int = 400):
        """
        Displays a QR code overlay with custom text below it.
        
        Args:
            url: The URL/data to encode in the QR code
            custom_text: Text to show below (or above) the QR
            duration: How long to show it (seconds). None = until ESC or manual close
            position: "center", "top-left", "top-right", "bottom-left", "bottom-right"
            text_color: Color of the custom text (hex)
            bg_color: Background color (hex) - use transparent-friendly color if needed
            qr_size: Size of the QR code in pixels (square)
        """
        try:
            self._safe_destroy()

            # Step 1: Create root window FIRST
            self.root = Tk()
            self.root.withdraw()  # hide it temporarily — we only need it for PhotoImage

            # Step 2: Now generate QR + PhotoImage (root exists → no error)
            import qrcode
            qr = qrcode.QRCode(version=1, box_size=10, border=4)
            qr.add_data(url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            qr_photo = ImageTk.PhotoImage(img.resize((qr_size, qr_size), Image.Resampling.LANCZOS))

            # Step 3: Now configure the visible window
            self.root.deiconify()               # show it again
            self.root.overrideredirect(True)
            self.root.attributes("-topmost", True)
            self.root.attributes("-alpha", 0.92)
            self.root.configure(bg=bg_color)

            # Position
            sw = self.root.winfo_screenwidth()
            sh = self.root.winfo_screenheight()
            w = qr_size + 100
            h = qr_size + 200

            pos_map = {
                "top-left": (20, 20),
                "top-right": (sw - w - 20, 20),
                "bottom-left": (20, sh - h - 20),
                "bottom-right": (sw - w - 20, sh - h - 20),
                "center": ((sw - w) // 2, (sh - h) // 2)
            }
            x, y = pos_map.get(position, pos_map["center"])
            self.root.geometry(f"{w}x{h}+{x}+{y}")

            # QR label
            qr_label = Label(self.root, image=qr_photo, bg=bg_color)
            qr_label.image = qr_photo  # keep reference
            qr_label.pack(pady=20)

            # Custom text
            text_label = Label(
                self.root,
                text=custom_text,
                font=("Segoe UI", 24, "bold"),
                fg=text_color,
                bg=bg_color,
                wraplength=w - 40
            )
            text_label.pack(pady=10)

            # Auto-close if duration given
            if duration is not None:
                def auto_close():
                    if self.root and self.root.winfo_exists():
                        self._safe_destroy()
                self.root.after(int(duration * 1000), auto_close)

            # ESC to close
            self.root.bind("<Escape>", lambda e: self._safe_destroy())

            self.root.mainloop()

        except Exception as e:
            print(f"QR overlay error: {e}")
            self._safe_destroy()

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
            self._safe_destroy()
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