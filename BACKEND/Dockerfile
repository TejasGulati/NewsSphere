FROM python:3.10.8-slim-bullseye
ENV PYTHONUNBUFFERED=1

WORKDIR /BACKEND  

COPY requirements.txt /BACKEND/
RUN apt-get update && \
    apt-get install -y \
    pkg-config \
    libmariadb-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip setuptools
RUN pip install -r requirements.txt

COPY . /BACKEND/

EXPOSE 8000
