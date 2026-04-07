FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libffi-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Non-root user
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid appuser --shell /bin/bash --create-home appuser

# Python dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir ".[dev]"

# Application code
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput --settings=config.settings.prod 2>/dev/null || true

RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 16000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:16000", "--workers", "4", "--timeout", "120"]
