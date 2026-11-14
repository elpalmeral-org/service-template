#!/usr/bin/env bash
# Genera lockfiles reales para el nombre de paquete ya renderizado — nunca por sed, que
# corrompería los hashes de uv.lock/package-lock.json.
set -euo pipefail

echo "==> uv lock (apps/backend)"
(cd apps/backend && uv lock)

echo "==> npm install --package-lock-only (apps/frontend)"
(cd apps/frontend && npm install --package-lock-only --no-audit --no-fund)
