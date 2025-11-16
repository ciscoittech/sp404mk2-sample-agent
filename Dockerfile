# Multi-stage build for SP404MK2 Sample Agent

# Stage 1: Backend builder
FROM python:3.11-slim as backend-builder

WORKDIR /app/backend

# Install system dependencies for audio processing and Essentia
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    libsndfile1 \
    libsndfile1-dev \
    ffmpeg \
    libyaml-dev \
    libfftw3-dev \
    libavcodec-dev \
    libavformat-dev \
    libavutil-dev \
    libsamplerate0-dev \
    libtag1-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY backend/requirements.txt .

# Install requirements, making Essentia optional in Docker
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt || \
    (echo "Warning: Some packages failed to install" && \
     pip install --no-cache-dir $(grep -v essentia requirements.txt | grep -v '^#' | grep -v '^$') && \
     echo "Continuing without Essentia - will use librosa fallback")

# Stage 2: Frontend builder
FROM node:20-alpine as frontend-builder

WORKDIR /app/frontend

# Copy frontend files
COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./

# Stage 3: Final runtime image
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies for audio processing and Essentia
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    libsndfile1 \
    libyaml-0-2 \
    libfftw3-3 \
    libavcodec58 \
    libavformat58 \
    libavutil56 \
    libsamplerate0 \
    libtag1v5 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=backend-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-builder /usr/local/bin /usr/local/bin

# Copy application code
COPY backend/ ./backend/
COPY --from=frontend-builder /app/frontend ./frontend/
COPY src/ ./src/
COPY sp404_chat.py ./
COPY requirements.txt ./

# Create necessary directories
RUN mkdir -p /app/downloads/metadata /app/downloads/test /app/data

# Environment variables
ENV PYTHONPATH=/app/backend:/app
ENV PYTHONUNBUFFERED=1

# Expose ports
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command - run the backend API
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]