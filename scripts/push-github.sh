#!/usr/bin/env bash
# Cursor 터미널(Git Bash / WSL)에서 GitHub로 푸시
# 사용법: bash scripts/push-github.sh "커밋 메시지"
set -euo pipefail
root="$(git rev-parse --show-toplevel)"
cd "$root"
if [[ $# -lt 1 ]]; then
  echo "사용법: $0 \"커밋 메시지\"" >&2
  exit 1
fi
git add -A
git status
git commit -m "$1"
branch="$(git branch --show-current)"
git push -u origin "$branch"
echo "완료: origin/${branch} 에 푸시했습니다."
