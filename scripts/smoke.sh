#!/usr/bin/env sh
set -eu

docker compose config --quiet
docker compose up --build -d
cleanup() {
  docker compose logs --tail=200
}
trap cleanup EXIT

attempt=0
until curl --fail --silent http://localhost:8080/health/ready >/dev/null; do
  attempt=$((attempt + 1))
  if [ "$attempt" -ge 30 ]; then
    echo "RepoChronicle did not become ready in time." >&2
    exit 1
  fi
  sleep 2
done

curl --fail --silent http://localhost:8080/v1/status
echo
