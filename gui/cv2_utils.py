import os
import sys
import json
from PIL import Image
from io import BytesIO
from jinja2 import Template
from threading import Thread
from base64 import b64encode
from queue import Queue, Empty
from cv2 import VideoCapture, error, CAP_DSHOW


def numpy_to_base64(image):
    with BytesIO() as buff:
        pil_img = Image.fromarray(image)
        pil_img.save(buff, format='JPEG')
        image = buff.getvalue()
        buff.close()
    return b64encode(image).decode("utf-8")


def get_config():
    file = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(file, 'r') as f:
        return json.load(f)


def set_config(data):
    file = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(file, 'w') as f:
        return json.dump(data, f, indent=4, ensure_ascii=False)


def template(p, context):
    with open(p) as file:
        html = Template(file.read())
        return html.render(**context)


class Capture:
    def __init__(self, capture, name, server, rotate, **kwargs):
        self.cap_ip = capture
        self.name = name
        self.server = server
        self.rotate = rotate
        try:
            cap = int(capture)
            if sys.platform == 'win32':
                self.cap = VideoCapture(cap, CAP_DSHOW)
            else:
                self.cap = VideoCapture(cap)
        except ValueError:
            self.cap = VideoCapture(capture)
        self.q = Queue()
        self.status = True
        self.t = Thread(target=self._reader)
        self.t.daemon = True
        self.t.start()

    def _reader(self):
        while self.status:
            try:
                ret, f = self.cap.read()
                if not ret:
                    break
                if not self.q.empty():
                    try:
                        self.q.get_nowait()
                    except Empty:
                        pass
                self.q.put(f)
            except error:
                break

    def read(self):
        try:
            return self.q.get()
        except AttributeError:
            exit(0)

    def release(self):
        self.status = False
        self.cap.release()
        del self.q
        del self.t
