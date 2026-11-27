set -eu

echo "[entrypoint] alembic upgrade head"
attempt=0
until alembic upgrade head; do
  attempt=$((attempt + 1))
  if [ "$attempt" -ge 10 ]; then
    echo "[entrypoint] alembic failed $attempt times, giving up" >&2
    exit 1
  fi
  echo "[entrypoint] retry $attempt/10 in 2s"
  sleep 2
done

if [ "${SEED_ON_START:-1}" = "1" ]; then
  echo "[entrypoint] seed"
  python scripts/seed.py
fi

echo "[entrypoint] starting: $*"
exec "$@"