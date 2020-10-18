import logging
from http import server
from http.server import BaseHTTPRequestHandler
from io import BytesIO
from multiprocessing import Condition, Value
from typing import Callable, Tuple
from urllib.parse import parse_qs, urlparse

from PIL import Image

from birdthing.camera import RESOLUTION

PAGE = f"""\
<!DOCTYPE html>
<html>
    <head>
        <title>birdthing</title>
    </head>
    <body>
        <img src="stream.mjpeg" width="{RESOLUTION[0]}" height="{RESOLUTION[1]}" />
    </body>
</html>
"""


def run(
    frame: Value,
    new_frame: Condition,
    target_offset_x: Value,
    target_offset_y: Value,
    address: Tuple[str, int],
):
    http_server = Server(
        frame, new_frame, target_offset_x, target_offset_y, address, Handler
    )
    logging.info(f"running server on {address[0]}:{address[1]}")
    http_server.serve_forever()


class Server(server.ThreadingHTTPServer):
    allow_reuse_address = True

    def __init__(
        self,
        frame: Value,
        new_frame: Condition,
        target_offset_x: Value,
        target_offset_y: Value,
        server_address: Tuple[str, int],
        RequestHandlerClass: Callable[..., BaseHTTPRequestHandler],
    ):
        super().__init__(server_address, RequestHandlerClass)
        self.frame = frame
        self.new_frame = new_frame
        self.target_offset_x = target_offset_x
        self.target_offset_y = target_offset_y


class Handler(server.BaseHTTPRequestHandler):
    server: Server

    def do_POST(self):
        url = urlparse(self.path)
        if url.path == "/move":
            query_params = parse_qs(url.query)
            direction = query_params["direction"]
            if direction == "up":
                self.server.target_offset_x.value = 0
                self.server.target_offset_y.value = 0.5
            elif direction == "down":
                self.server.target_offset_x.value = 0
                self.server.target_offset_y.value = 0.5
            elif direction == "left":
                self.server.target_offset_x.value = 0.5
                self.server.target_offset_y.value = 0
            elif direction == "right":
                self.server.target_offset_x.value = 0.5
                self.server.target_offset_y.value = 0
            self.send_response(204)
            self.end_headers()

    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/":
            self.send_response(301)
            self.send_header("Location", "/index.html")
            self.end_headers()
        elif url.path == "/index.html":
            content = PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        elif url.path == "/stream.mjpeg":
            self.send_response(200)
            self.send_header("Age", str(0))
            self.send_header("Cache-Control", "no-cache, private")
            self.send_header("Pragma", "no-cache")
            self.send_header(
                "Content-Type", "multipart/x-mixed-replace; boundary=FRAME"
            )
            self.end_headers()
            try:
                while True:
                    new_frame: Condition = self.server.new_frame
                    with new_frame:
                        new_frame.wait()

                    with BytesIO() as buffer:
                        frame = self.server.frame
                        with frame:
                            Image.frombytes("RGB", RESOLUTION, frame.get_obj()).save(
                                buffer, format="jpeg"
                            )
                        data = buffer.getvalue()
                        self.wfile.write(b"--FRAME\r\n")
                        self.send_header("Content-Type", "image/jpeg")
                        self.send_header("Content-Length", str(len(data)))
                        self.end_headers()
                        self.wfile.write(data)
                        self.wfile.write(b"\r\n")
            except Exception as e:
                logging.warning(
                    "Removed streaming client %s: %s", self.client_address, str(e)
                )
        else:
            self.send_error(404)
            self.end_headers()
