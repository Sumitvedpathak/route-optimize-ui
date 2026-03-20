#!/bin/sh
set -e
# Cloud Run sets PORT; local fallback 8080
export PORT="${PORT:-8080}"
# Imports use `agents`, `constants` from repo root — src must be on PYTHONPATH
export PYTHONPATH="/app/src${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONUNBUFFERED=1

exec chainlit run src/app.py \
  --host 0.0.0.0 \
  --port "$PORT"
