FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src
ENV APSO_ROOT_DIR=/app
ENV APSO_CONFIG_DIR=/workspace/config

WORKDIR /app

COPY pyproject.toml /app/pyproject.toml
RUN pip install --no-cache-dir .

COPY src /app/src
COPY migrations /app/migrations
COPY alembic.ini /app/alembic.ini

RUN useradd --create-home --shell /usr/sbin/nologin apso \
    && mkdir -p /var/lib/apso/repositories /var/lib/apso/artifacts \
    && chown -R apso:apso /app /var/lib/apso

EXPOSE 8000

USER apso

CMD ["uvicorn", "apso_backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
