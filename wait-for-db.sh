#!/usr/bin/env bash
# wait-for-db.sh HOST PORT -- COMMAND...
# Example: ./wait-for-db.sh db 5432 -- python manage.py runserver 0.0.0.0:8000

set -e

HOST="$1"
PORT="$2"
shift 2

if [ -z "$HOST" ] || [ -z "$PORT" ]; then
  echo "Usage: $0 host port -- command"
  exit 2
fi

echo "Waiting for $HOST:$PORT..."

# Try until success (timeout after 60 attempts -> ~60s)
COUNT=0
MAX=60
until nc -z "$HOST" "$PORT"; do
  COUNT=$((COUNT + 1))
  if [ "$COUNT" -ge "$MAX" ]; then
    echo "Timeout waiting for $HOST:$PORT"
    exit 1
  fi
  echo "  [$COUNT] waiting..."
  sleep 1
done

echo "$HOST:$PORT is available — running command"
exec "$@"
