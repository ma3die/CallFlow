FROM python:3.11-slim-bullseye
WORKDIR /app
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    python3-dev \
    libpq-dev \
    libmagic1 \
    cmake \
    build-essential \
    pkg-config \
    libffi-dev \
    libsndfile1 \
    libasound2-dev \
    libjack-dev \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
# Сначала установим numpy отдельно
RUN pip install --no-cache-dir numpy
RUN pip3 install --upgrade pip && pip3 install -r /app/requirements.txt --no-cache-dir && rm -f requirements.txt
COPY . .