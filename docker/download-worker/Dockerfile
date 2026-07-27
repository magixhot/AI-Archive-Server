FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .

COPY src ./src

RUN pip install --no-cache-dir .

CMD ["python", "-u", "-m", "src.download_worker.main"]