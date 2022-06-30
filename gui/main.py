import os
import eel
import json
from cv2 import rotate
from requests import get
from random import randint
from cv2_utils import Capture, numpy_to_base64, template

admin_url = "http://192.168.1.24/admin"

capture_example = {
    "name": "capture1",
    "server": "192.168.1.28",
    "capture": "0",
    "rotate": None,
    "timeout": 300
}

captures = []

caps = []


def frame(capture_name):
    for cap in caps:
        if str(cap.name) == str(capture_name):
            image = cap.read()
            image_rgb = image[:, :, ::-1]
            if cap.rotate is not None: image_rgb = rotate(image_rgb, cap.rotate)
            return numpy_to_base64(image_rgb), cap


def profiles(capture_name):
    image, cap = frame(capture_name)
    data = {
        "capture": capture_name,
        "image": image
    }
    try:
        response = get(f'http://{cap.server}/api/face-recognize', json=data)
        return response.json()['profiles']
    except Exception as _exp:
        return []


def close_callback(route=None, websockets=None):
    for cap in caps:
        cap.release()
    if websockets:
        for websocket in websockets:
            websocket.close()
    exit(0)


@eel.expose('show_captures')
def _show_captures():
    global caps
    caps = [Capture(**cap) for cap in captures]
    html = []
    for cap in caps:
        image, _ = frame(cap.name)
        context = {
            "name": cap.name,
            "capture": cap.cap_ip,
            "server": cap.server,
            "image": image,
            "profiles": []
        }
        html_card = template(os.path.join(src, 'templates', 'card.html'), context)
        html.append(html_card)
    return '\n'.join(html)


@eel.expose('show_add_capture')
def _show_add_capture():
    return template(os.path.join(src, 'templates', 'add_capture.html'), capture_example)


@eel.expose('add_capture')
def _add_capture(text):
    capture = json.loads(text)
    captures.append(capture)
    caps.append(Capture(**capture))
    image, _ = frame(capture['name'])
    context = {
        "name": capture['name'],
        "capture": capture['capture'],
        "server": capture['server'],
        "image": image,
        "profiles": []
    }
    return template(os.path.join(src, 'templates', 'card.html'), context)


@eel.expose('captures')
def _captures():
    return captures


@eel.expose('admin_url')
def _admin_url():
    return admin_url


@eel.expose('get_frame')
def _get_frame(capture_name):
    return frame(capture_name)


@eel.expose('get_profiles')
def _get_profiles(capture_name):
    return profiles(capture_name)


@eel.expose('close')
def _close():
    close_callback()


if __name__ == '__main__':
    this_dir = os.path.dirname(__file__)
    src = os.path.join(this_dir, 'src')
    eel.init(src, js_result_timeout=5)
    port = randint(5000, 9999)
    eel.start('templates/index.html', port=port, jinja_templates='templates', close_callback=close_callback)
