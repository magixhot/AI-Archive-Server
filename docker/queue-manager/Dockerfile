FROM python:3.12-slim


WORKDIR /app


COPY pyproject.toml .


RUN pip install --no-cache-dir \
    fastapi \
    "uvicorn[standard]"


COPY src ./src


EXPOSE 8080


CMD ["uvicorn", "src.queue_manager.main:app", "--host", "0.0.0.0", "--port", "8080"]