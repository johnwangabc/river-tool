#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ALLOW_INTERACTIVE="${ALLOW_INTERACTIVE:-0}"

if [ -f "$REPO_ROOT/.env.local" ]; then
  set -a
  # shellcheck disable=SC1090
  source "$REPO_ROOT/.env.local"
  set +a
fi

if [ -z "${EXPO_TOKEN:-}" ]; then
  if npx eas whoami >/dev/null 2>&1; then
    :
  else
    if [ "$ALLOW_INTERACTIVE" = "1" ]; then
      echo "未检测到 EXPO_TOKEN，将进入交互式 Expo 登录..."
      npx expo login
    else
      echo "缺少 EXPO_TOKEN 且未检测到已登录。请在 .env.local 写入 EXPO_TOKEN=...，或使用 ALLOW_INTERACTIVE=1 npm run eas -- <命令> 手动登录。" >&2
      exit 1
    fi
  fi
fi

cd "$REPO_ROOT"

if [ "$ALLOW_INTERACTIVE" = "1" ]; then
  npx eas "$@"
else
  npx eas --non-interactive "$@"
fi
