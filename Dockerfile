FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies INCLUDING PostgreSQL dev libraries
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Create static directory
RUN mkdir -p /app/staticfiles

# Collect static files (skip if DB is needed)
# RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

# Default command
CMD ["gunicorn", "online_poll.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120"]