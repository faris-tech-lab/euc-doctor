#!/usr/bin/env bash
set -euo pipefail

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "This bootstrap script is for macOS only."
  exit 1
fi

REPO_URL=""
INSTALL_DIR="${HOME}/.local/share/euc-doctor"
RUN_AFTER_INSTALL="1"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)
      REPO_URL="$2"
      shift 2
      ;;
    --dir)
      INSTALL_DIR="$2"
      shift 2
      ;;
    --no-run)
      RUN_AFTER_INSTALL="0"
      shift
      ;;
    *)
      echo "Unknown argument: $1"
      echo "Usage: bootstrap_macos.sh --repo <git-url> [--dir <install-dir>] [--no-run]"
      exit 2
      ;;
  esac
done

if [[ -z "$REPO_URL" ]]; then
  echo "Missing required argument: --repo <git-url>"
  exit 2
fi

PYTHON_BIN=""
if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="python"
fi

if [[ -z "$PYTHON_BIN" ]]; then
  if command -v brew >/dev/null 2>&1; then
    echo "Python not found. Installing Python with Homebrew..."
    brew install python
    PYTHON_BIN="python3"
  else
    echo "Python 3 was not found and Homebrew is not installed."
    echo "Install Homebrew (https://brew.sh) or Python 3, then rerun."
    exit 1
  fi
fi

if ! command -v git >/dev/null 2>&1; then
  if command -v brew >/dev/null 2>&1; then
    echo "Git not found. Installing Git with Homebrew..."
    brew install git
  else
    echo "Git is required to clone the repository."
    exit 1
  fi
fi

mkdir -p "$(dirname "$INSTALL_DIR")"
if [[ -d "$INSTALL_DIR/.git" ]]; then
  echo "Updating existing install in $INSTALL_DIR..."
  git -C "$INSTALL_DIR" pull --ff-only
else
  echo "Cloning toolkit to $INSTALL_DIR..."
  rm -rf "$INSTALL_DIR"
  git clone --depth 1 "$REPO_URL" "$INSTALL_DIR"
fi

cd "$INSTALL_DIR"

echo "Creating virtual environment..."
"$PYTHON_BIN" -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate

echo "Installing toolkit..."
python -m pip install --upgrade pip
python -m pip install -e .

echo "Install complete."
if [[ "$RUN_AFTER_INSTALL" == "1" ]]; then
  echo "Launching toolkit menu..."
  python euc_doctor.py
else
  echo "Run later with:"
  echo "  cd \"$INSTALL_DIR\" && source .venv/bin/activate && python euc_doctor.py"
fi
