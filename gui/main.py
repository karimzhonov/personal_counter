import os
import eel
import json
from cv2 import rotate
from requests import get
from random import randint
from cv2_utils import (Capture,
                       numpy_to_base64,
                       get_config, set_config,
                       template)

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
        print(_exp)
        return []


def close_callback(route=None, websockets=None):
    for cap in caps:
        cap.release()
    exit(0)


@eel.expose('show_config')
def _show_config():
    context = {
        "config": json.dumps(get_config(), indent=4, ensure_ascii=False),
    }
    return template(os.path.join(src, 'templates', 'config.html'), context)


@eel.expose('update_config')
def _update_config(text):
    try:
        local_config = json.loads(text)
        set_config(local_config)
        return True
    except json.JSONDecodeError:
        return False


@eel.expose('show_captures')
def _show_captures():
    global caps
    config = get_config()
    caps = [Capture(**cap) for cap in config['captures']]

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


@eel.expose('config')
def _config():
    return get_config()


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
    eel.init(src)
    port = randint(5000, 9999)
    eel.start('templates/index.html', port=port, jinja_templates='templates', close_callback=close_callback)
