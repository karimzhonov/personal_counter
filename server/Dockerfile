FROM animcogn/face_recognition:cpu


RUN apt-get update -y
RUN apt-get install python3-opencv gunicorn -y
RUN apt-get clean

WORKDIR /app

ENV TZ="Europe/Moscow"
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY . .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install pytz