import io, sys
import cv2
import queue
import base64
import imutils
import numpy as np
from threading import Thread
from imutils import perspective
from face_recognition import face_locations
from mediapipe.python.solutions.face_mesh import FaceMesh
from PIL import Image
from .conf import UNKNOWN_NAME, UNKNOWN_COLOR, KNOWN_COLOR


class VideoCapture:
    def __init__(self, cap):
        self.cap_ip = cap
        try:
            cap = int(cap)
        except ValueError:
            pass
        if sys.platform == 'win32':
            self.cap = cv2.VideoCapture(cap, cv2.CAP_DSHOW)
        else:
            self.cap = cv2.VideoCapture(cap)
        self.q = queue.Queue()
        self.status = True
        self.t = Thread(target=self._reader)
        self.t.daemon = True
        self.t.start()

    # read frames as soon as they are available, keeping only most recent one
    def _reader(self):
        while self.status:
            try:
                ret, f = self.cap.read()
                if not ret:
                    break
                if not self.q.empty():
                    try:
                        self.q.get_nowait()  # discard previous (unprocessed) frame
                    except queue.Empty:
                        pass
                self.q.put(f)
            except cv2.error:
                break

    def read(self):
        return self.q.get()

    def release(self):
        self.status = False
        self.cap.release()
        del self.t


def draw_faces(frame: np.array, face_locations: list, face_names: list, frame_scale=4):
    for (top, right, bottom, left), profile in zip(face_locations, face_names):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        color = UNKNOWN_COLOR if profile is None else KNOWN_COLOR
        top *= frame_scale
        right *= frame_scale
        bottom *= frame_scale
        left *= frame_scale
        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
        font = cv2.FONT_HERSHEY_COMPLEX
        name = UNKNOWN_NAME if profile is None else profile.get_fullname()
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)
    return frame


def extrac_faces(frame, border=0.1):
    faces = []
    h, w = frame.shape[:2]
    for top, right, bottom, left in face_locations(frame):
        pts = np.array([
            (int(left - border * w), int(top - border * h)),
            (int(right + border * w), int(top - border * h)),
            (int(left - border * w), int(bottom + border * h)),
            (int(right + border * w), int(bottom + border * h))])
        face = imutils.perspective.four_point_transform(frame, pts)
        faces.append(face)
    return faces


def rotate_face(frame):
    h, w, _ = frame.shape
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    landmarks = FaceMesh(max_num_faces=1).process(frame_rgb).multi_face_landmarks
    if landmarks:
        for point in landmarks:
            left_eye = point.landmark[23]
            right_eye = point.landmark[253]
            nose = point.landmark[160]
            lx, ly = int(left_eye.x * w), int(left_eye.y * h)
            rx, ry = int(right_eye.x * w), int(right_eye.y * h)
            nx, ny = int(nose.x * w), int(nose.y * h)
            if (rx - lx) == 0:
                angle = 90
            else:
                angle = np.arctan((ry - ly) / (rx - lx))
                angle = angle * 180 / np.pi
            return imutils.rotate(frame, angle)


def base64_to_numpy(image: str):
    with io.BytesIO(base64.b64decode(image)) as buf:
        image = Image.open(buf)
        return np.array(image)


def numpy_to_base64(image):
    with io.BytesIO() as buff:
        pil_img = Image.fromarray(image)
        pil_img.save(buff, format='JPEG')
        image = buff.getvalue()
        buff.close()
    return base64.b64encode(image).decode("utf-8")
