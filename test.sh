#!/usr/bin/env bash
# Run the test suite (builds the site as part of it).
set -euo pipefail
cd "$(dirname "$0")"
exec python3 -m unittest discover -s tests -v
