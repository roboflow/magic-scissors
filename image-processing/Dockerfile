FROM python:3.10

RUN apt-get update
RUN apt install -y libgl1-mesa-glx

RUN pip install Flask gunicorn numpy opencv-python-headless shapely supervision roboflow

COPY src app/
WORKDIR /app

ENV PORT 8080

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 app:app