#!/bin/bash
set -e
for i in {1..10}; do
  curl -sf http://127.0.0.1:8000/healthz >/dev/null || curl -sf http://127.0.0.1:8030/healthz >/dev/null
  sleep 1
  echo -n '.'
done
echo ' OK'
