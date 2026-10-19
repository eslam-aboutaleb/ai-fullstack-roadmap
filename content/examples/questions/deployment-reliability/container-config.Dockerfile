FROM python:3.11-slim@sha256:REPLACE_WITH_REVIEWED_DIGEST
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN useradd --create-home learner
COPY app.py .
USER learner
CMD ["python", "app.py"]
