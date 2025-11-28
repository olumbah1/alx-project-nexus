FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies (libpq for psycopg)
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

# Create static dir (WhiteNoise will serve from here)
RUN mkdir -p /app/staticfiles

# Do NOT run migrations here in build; run them during start instead.
# Collect static now so the build contains static files (optional)
RUN python manage.py collectstatic --noinput || true

# Expose default container port (informational only)
EXPOSE 8000

# Use CMD that a render dockerCommand can override.
# NOTE: This binds to $PORT when dockerCommand uses it or when Render runs the command.
CMD ["bash", "-lc", "gunicorn online_poll.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120"]
