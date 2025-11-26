# Dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install build tools (kept minimal)
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /app/

# Ensure static dir exists
RUN mkdir -p /app/staticfiles

EXPOSE 8000

# Run migrations then start gunicorn
CMD ["bash", "-lc", "python manage.py migrate --noinput && gunicorn online_poll.wsgi:application --bind 0.0.0.0:8000 --workers 3"]
