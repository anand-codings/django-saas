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

# Python dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir ".[dev]"

# Application code
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput --settings=config.settings.prod 2>/dev/null || true

EXPOSE 16000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:16000", "--workers", "4", "--timeout", "120"]
