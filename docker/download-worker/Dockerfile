FROM python:3.12-slim

WORKDIR /app

COPY src /app/src

CMD ["python", "-u", "-m", "src.download_worker.main"]