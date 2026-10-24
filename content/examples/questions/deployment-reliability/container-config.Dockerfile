# Multi-Stage Production Container Configuration
# Stage 1: Build & Dependency Wheel Compilation
FROM python:3.11-slim@sha256:7f8582236dc99b9c97b5e4ff5bfdae9d3d922119bbce2bbd03831b748f3ee8b8 AS builder

WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip wheel --no-cache-dir --no-deps --wheel-dir /build/wheels -r requirements.txt

# Stage 2: Minimal Distroless/Hardened Runtime
FROM python:3.11-slim@sha256:7f8582236dc99b9c97b5e4ff5bfdae9d3d922119bbce2bbd03831b748f3ee8b8 AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080 \
    APP_HOME=/home/appuser/app

# Create unprivileged application user and group (UID/GID 10001)
RUN groupadd --gid 10001 appgroup \
    && useradd --uid 10001 --gid appgroup --create-home --home-dir /home/appuser appuser

WORKDIR ${APP_HOME}

# Copy compiled wheels from builder and install
COPY --from=builder /build/wheels /tmp/wheels
RUN pip install --no-cache-dir /tmp/wheels/* && rm -rf /tmp/wheels

# Copy application code with unprivileged ownership
COPY --chown=appuser:appgroup app.py .

# Switch to non-root execution context
USER 10001:10001

EXPOSE 8080

HEALTHCHECK --interval=15s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/healthz')"

CMD ["python", "app.py"]
