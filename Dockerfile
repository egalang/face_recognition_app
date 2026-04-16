FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    pkg-config \
    libopenblas-dev \
    liblapack-dev \
    libjpeg62-turbo-dev \
    libpng-dev \
    libtiff5-dev \
    libwebp-dev \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt

RUN python -m pip install --upgrade "pip<25.1" wheel \
    && python -m pip install --no-cache-dir "setuptools<82" \
    && python -m pip install --no-cache-dir -r /app/requirements.txt \
    && python -c "import pkg_resources; import face_recognition_models; import face_recognition; print('Imports OK')"

COPY app /app/app
COPY .env.example /app/.env.example
COPY README.md /app/README.md
COPY docker-entrypoint.sh /app/docker-entrypoint.sh

RUN mkdir -p /app/data/faces \
    && chmod +x /app/docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
