import os
import cv2
import pytz
import pickle
from datetime import datetime, timedelta

import numpy as np
from face_recognition import face_encodings

from django.db import models
from django.core.files.base import ContentFile
from project.logger import logger
from project.settings import TIME_ZONE
from compare_face.cv2 import numpy_to_base64


class Personal(models.Model):
    surname = models.CharField(max_length=255, null=True, blank=True, verbose_name='Surname')
    name = models.CharField(max_length=255, null=True, blank=True, verbose_name='Name')
    image = models.ImageField(null=True, blank=True, upload_to='images', verbose_name='Last Image')
    face_encodings = models.BinaryField(null=True, blank=True)

    class Meta:
        verbose_name = 'Персонал'
        verbose_name_plural = 'Персонал'
        ordering = ['pk']

    def __str__(self):
        return self.get_fullname()

    def get_fullname(self):
        text = []
        if self.surname: text.append(self.surname)
        if self.name: text.append(self.name)
        return ' '.join(text) if text else f'{self.pk}'

    @classmethod
    def get_personals_with_encodings(cls):
        personals = cls.objects.all()
        encs = []
        pers = []
        for p in personals:
            if p.face_encodings:
                for e in pickle.loads(p.face_encodings):
                    encs.append(e)
                    pers.append(p)
        return pers, encs

    def set_image(self, image: np.array, face_enc: np.array = None, save: bool = True):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        _, image = cv2.imencode('.jpg', image)
        if os.path.exists(self.image.path): os.remove(self.image.path)
        self.image.save(f'{self.get_fullname()}.jpg', ContentFile(image), False)

        if face_enc is None: face_enc = face_encodings(image)[0]
        self.set_face_enc(face_enc, False)
        if save: self.save()

    def get_image(self):
        image = cv2.imread(self.image.path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return numpy_to_base64(image)

    def set_face_enc(self, face_encoding, save: bool = True):
        self.face_encodings = pickle.dumps([face_encoding], pickle.HIGHEST_PROTOCOL)
        if save: self.save()

    @classmethod
    def create(cls, face_image: np.array, face_enc: np.array = None):
        instance = cls()
        instance.set_image(face_image, face_enc)
        return instance


class Visit(models.Model):
    visit_at = models.DateTimeField(auto_now=True, null=True, blank=True, verbose_name='Last visit')
    personal = models.ForeignKey(Personal, models.CASCADE)

    @classmethod
    def add_visit(cls, personal: Personal):
        visits = cls.objects.filter(personal_id=personal.id).order_by("-visit_at")
        if not visits or datetime.now() - visits[0].visit_at.replace(tzinfo=None) > timedelta(0, 60, hours=3):
            visit = cls.objects.create(personal_id=personal.id)
            logger.debug(f'Create visit: Personal id - {visit.personal.pk}')

