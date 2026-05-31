#!/bin/sh
set -e

if [ "$DATABASE_URL" != "" ]; then
  echo "Waiting for database..."
  python - <<'PY'
import os, time, sys
import psycopg
url = os.environ.get("DATABASE_URL", "")
for i in range(30):
    try:
        conn = psycopg.connect(url)
        conn.close()
        sys.exit(0)
    except Exception:
        time.sleep(1)
sys.exit(1)
PY
fi

exec "$@"
