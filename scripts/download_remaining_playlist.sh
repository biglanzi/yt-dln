#!/usr/bin/env bash
set -Eeuo pipefail

PLAYLIST_URL="https://www.youtube.com/playlist?list=PLBs_kjykua9V2ut1nQwOcLecggUMfaE2-"
PLAYLIST_ITEMS="${PLAYLIST_ITEMS:-12-99}"
OUTPUT_DIR="${OUTPUT_DIR:-downloads/remaining-playlist}"
SLEEP_REQUESTS="${SLEEP_REQUESTS:-0.75}"
SLEEP_INTERVAL="${SLEEP_INTERVAL:-10}"
MAX_SLEEP_INTERVAL="${MAX_SLEEP_INTERVAL:-20}"
CONCURRENT_FRAGMENTS="${CONCURRENT_FRAGMENTS:-1}"
RATE_LIMIT="${RATE_LIMIT:-}"

YTDL_BIN="${YTDL_BIN:-ytdl}"

if ! command -v "$YTDL_BIN" >/dev/null 2>&1; then
  printf 'Error: ytdl command not found. Install this project or set YTDL_BIN.\n' >&2
  printf 'Example: YTDL_BIN=/path/to/ytdl %s\n' "$0" >&2
  exit 127
fi

mkdir -p "$OUTPUT_DIR"

args=(
  --playlist \
  --playlist-items "$PLAYLIST_ITEMS" \
  --ignore-errors \
  --output-dir "$OUTPUT_DIR" \
  --sleep-requests "$SLEEP_REQUESTS" \
  --sleep-interval "$SLEEP_INTERVAL" \
  --max-sleep-interval "$MAX_SLEEP_INTERVAL" \
  --concurrent-fragments "$CONCURRENT_FRAGMENTS"
)

if [[ -n "$RATE_LIMIT" ]]; then
  args+=(--rate-limit "$RATE_LIMIT")
fi

exec "$YTDL_BIN" "${args[@]}" "$@" "$PLAYLIST_URL"
