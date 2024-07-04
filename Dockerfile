FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["bash", "-c"]
CMD ["if [ \"$MODE\" = \"worker\" ]; then celery -A app.worker.celery worker --loglevel=info --autoscale=10,3; else uvicorn app.main:app --host 0.0.0.0 --port 8000; fi"]
