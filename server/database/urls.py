from django.urls import path
from .views import face_recognize


urlpatterns = [
    path('face-recognize', face_recognize),
]