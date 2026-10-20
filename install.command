#!/bin/bash
# macOS built-in bash; no Python, Git, Homebrew, sudo or PATH edits required.
set -euo pipefail
root="$(cd "$(dirname "$0")" && pwd)"
mode=""
target=""
if [[ $# == 0 ]]; then
  printf 'Apple Watch 高血压通知 / Setup\n1) Codex\n2) Claude Code\n3) 仅准备当前目录 / Prepare this folder (WorkBuddy/manual)\n4) 其他 Agent 的技能目录 / Custom skills parent\nq) 退出 / Quit\n'
  read -r -p '选择 / Choose [1/2/3/4/q]: ' choice || exit 0
  case "$choice" in
    1) mode=codex ;;
    2) mode=claude ;;
    3) mode=prepare ;;
    4) mode=custom; read -r -p '输入完整父目录 / Absolute parent path: ' target ;;
    q|Q) exit 0 ;;
    *) printf '选择无效，未安装。Invalid choice.\n' >&2; exit 2 ;;
  esac
else
  case "${1:-}" in
    --agent) mode="${2:-}"; [[ $# == 2 && "$mode" =~ ^(codex|claude)$ ]] || exit 2 ;;
    --prepare) mode=prepare; [[ $# == 1 ]] || exit 2 ;;
    --target) mode=custom; target="${2:-}"; [[ $# == 2 ]] || exit 2 ;;
    *) printf 'Usage: bash install.command [--agent codex|claude | --prepare | --target /absolute/skills-parent]\n'; exit 2 ;;
  esac
fi
[[ "$(uname -s)" == Darwin ]] || { printf '需要在 Mac 本机执行。Run on your Mac.\n' >&2; exit 1; }
case "$mode" in
  codex) target="$HOME/.agents/skills" ;;
  claude) target="$HOME/.claude/skills" ;;
  custom) [[ "$target" == /* ]] || { printf '目录必须以 / 开头。Use an absolute path.\n' >&2; exit 2; } ;;
esac
if [[ "$mode" != prepare ]]; then
  destination="$target/apple-watch-hypertension"
  [[ ! -e "$destination" && ! -L "$destination" ]] || {
    printf '已有安装，未覆盖 / Existing installation, not overwritten: %s\n请参阅新手指南的更新说明。See the upgrade guide.\n' "$destination" >&2; exit 1;
  }
fi
printf '准备 uv、Python 3.11 和固定依赖；首次需要联网。不会连接手机或发送定位。\nPreparing uv, Python 3.11 and locked dependencies; first run needs internet. No phone changes.\n'
tools="$HOME/Library/Application Support/apple-watch-hypertension/tools"
uv="$tools/uv"
if [[ ! -x "$uv" ]]; then
  case "$(uname -m)" in
    arm64) platform=aarch64; digest=606b3c6949d971709f2526fa0d9f0fd23ccf60e09f117999b406b424af18a6a6 ;;
    x86_64) platform=x86_64; digest=4982dfff14b3548bc85d0fa0abec6ab8ae62836b218bf1223741ba1392ef93bf ;;
    *) printf 'Unsupported Mac architecture\n' >&2; exit 1 ;;
  esac
  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' EXIT
  archive="uv-$platform-apple-darwin"
  curl --fail --location --show-error --proto '=https' --proto-redir '=https' \
    --connect-timeout 20 --max-time 300 --retry 2 \
    "https://github.com/astral-sh/uv/releases/download/0.9.25/$archive.tar.gz" -o "$tmp/uv.tar.gz"
  printf '%s  %s\n' "$digest" "$tmp/uv.tar.gz" | shasum -a 256 -c -
  tar -xzf "$tmp/uv.tar.gz" -C "$tmp"
  mkdir -p "$tools"
  chmod 700 "$tools"
  cp "$tmp/$archive/uv" "$tools/uv.pending"
  chmod 700 "$tools/uv.pending"
  mv "$tools/uv.pending" "$uv"
fi
[[ "$("$uv" --version)" == "uv 0.9.25"* ]] || {
  printf 'uv version mismatch. 查看新手指南常见问题：仅移除 tools/uv 后重试。See the beginner guide for recovery; no phone action started.\n' >&2; exit 1;
}
if [[ "$mode" == prepare ]]; then
  destination="$root"
else
  "$uv" run --no-project --managed-python --python 3.11 python "$root/scripts/install.py" --target "$target"
fi
printf '环境准备目录 / Runtime folder: %s\n若依赖安装失败，请在此目录重新运行 install.command 并选择 3。\n' "$destination"
cd "$destination"
"$uv" sync --frozen --no-dev --managed-python --python 3.11
printf '\n安装完成 / Setup complete: %s\n请重新打开 Agent 对话并让它读取 SKILL.md。Reload your agent skills.\n' "$destination"
printf '本地工具 / Local tool: bash "%s/scripts/run.command" doctor\n' "$destination"
