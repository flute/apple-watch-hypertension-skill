#!/bin/bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
if [[ ! -x "$root/.venv/bin/python" ]]; then
  printf '请先运行安装程序，选择 3 准备当前目录。Run install.command and choose 3 first.\n' >&2
  exit 1
fi
cd "$root"
exec "$root/.venv/bin/python" "$root/scripts/watchbp.py" "$@"
