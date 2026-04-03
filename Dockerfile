FROM python:3.12-slim-bookworm

WORKDIR /app
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY adapters adapters/
COPY core core/
COPY db db/
COPY ingest.py .

CMD ["python", "ingest.py"]
