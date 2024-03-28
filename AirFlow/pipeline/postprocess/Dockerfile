FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN  apt-get update && apt-get install ffmpeg libsm6 libxext6 mc  -y && apt autoclean

COPY postprocess.py /app/postprocess.py
