import cv2
import imutils.perspective
import numpy as np
import face_recognition
from database.models import Personal, Visit

from .cv2 import VideoCapture, draw_faces


def compare_face(capture_name):
    cap = VideoCapture(capture_name)
    while True:
        frame = cap.read()
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = small_frame[:, :, ::-1]
        face_locations, face_names = find_faces(rgb_small_frame)
        frame = draw_faces(frame, face_locations, face_names)
        cv2.imshow(str(capture_name), frame)
        if cv2.waitKey(1) == ord('q'):
            break
    cap.cap.release()


def find_faces(frame, border=0.1):
    # Find all the faces and face encodings in the current frame of video
    h, w = frame.shape[:2]
    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)

    face_names = []
    personals, known_face_encodings = Personal.get_personals_with_encodings()
    for face_encoding, (top, right, bottom, left) in zip(face_encodings, face_locations):
        pts = np.array([
            (int(left - border * w), int(top - border * h)),
            (int(right + border * w), int(top - border * h)),
            (int(left - border * w), int(bottom + border * h)),
            (int(right + border * w), int(bottom + border * h))])
        face = imutils.perspective.four_point_transform(frame, pts)
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        if matches:
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                personal = personals[best_match_index]
                personal.set_image(face, face_encoding)
                Visit.add_visit(personal)
                face_names.append(personal)
                continue
        personal = Personal.create(face, face_encoding)
        Visit.add_visit(personal)
        face_names.append(personal)
    return face_locations, face_names
