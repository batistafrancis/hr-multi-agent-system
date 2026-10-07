#!/bin/sh
set -eu

backup=${1:-/backup}
copilot=${2:-/copilot}
vscode_data=${3:-/vscode-data}

test -d "$copilot"
test -d "$vscode_data"
if [ -n "$(ls -A "$copilot")" ] || [ -n "$(ls -A "$vscode_data")" ]; then
    echo "Volumes are not empty; refusing to overwrite existing state" >&2
    exit 1
fi

tar -tzf "$backup/copilot.tar.gz" >/dev/null
tar -tzf "$backup/vscode-data.tar.gz" >/dev/null
tar -xzf "$backup/copilot.tar.gz" -C "$copilot"
tar -xzf "$backup/vscode-data.tar.gz" -C "$vscode_data"
chown -R vscode:vscode "$copilot" "$vscode_data"
echo "State restored successfully."
