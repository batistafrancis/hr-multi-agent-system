# Persisting development state

## Which terminal to use

This guide assumes Windows is your host OS and Linux runs inside the Dev
Container. The VS Code interface runs on Windows even when its integrated
terminal is connected to Linux.

| Action | Where to run it |
|---|---|
| Back up existing state (Step 1) | Linux terminal inside the current Dev Container |
| Create and seed Docker volumes (Step 2) | Windows PowerShell on the host, not inside the container |
| Rebuild (Step 3a) | VS Code Command Palette, not a terminal command |
| Check mounts and Git identity (Step 3b) | Linux terminal inside the rebuilt Dev Container |
| Check past chats (Step 3c) | VS Code/Copilot interface |
| Configure repository Git identity | Linux Dev Container terminal |
| Enable the Windows SSH-agent service | Windows PowerShell run as administrator |
| Load the SSH key and test host authentication | Normal Windows PowerShell |
| Restart VS Code and reopen the container | Windows desktop / VS Code interface |
| Test forwarded SSH authentication | Linux terminal inside the reopened Dev Container |

Windows PowerShell usually has a prompt such as `PS C:\...>`. The container
terminal uses Linux paths such as `/workspaces/hr-multi-agent-system`.
If unsure, check VS Code's lower-left remote indicator: it should identify
the Dev Container before you open a terminal for Linux commands.

Run repository-relative commands from the project root:
`C:\projects-dev\hr-multi-agent-system` on Windows, or
`/workspaces/hr-multi-agent-system` inside the container.

## What persists

The workspace is bind-mounted from the host. Repository files, local Git
configuration, and commits survive container recreation. Ollama model data,
Copilot state, and VS Code remote data use separate Docker volumes.

| Data | Persistent location |
|---|---|
| Repository and local Git identity | Host project directory, including `.git/config` |
| Ollama models | Existing Compose `ollama_data` volume |
| Copilot state | `hr-multi-agent-copilot-state` mounted at `/home/vscode/.copilot` |
| VS Code remote data | `hr-multi-agent-vscode-data` mounted at `/home/vscode/.vscode-server/data` |

The entire home directory is not persisted. SSH private keys remain on the
host; no keys or SSH agent sockets are stored in these volumes.
Volumes survive container recreation but not explicit volume deletion,
Docker Desktop data resets, or loss of the host disk. Do not run
`docker compose down -v` or volume-pruning commands if you need this state.

## Migrate an existing container before rebuilding

Do not rebuild until existing state has been backed up and restored into the
new volumes. Empty mounts can hide existing container-local data.

### 1. Back up from the current Dev Container terminal

```bash
mkdir -p .devcontainer/local-state-backup
chmod 700 .devcontainer/local-state-backup
tar -czf .devcontainer/local-state-backup/copilot.tar.gz \
  -C /home/vscode/.copilot .
tar --exclude='./logs' -czf .devcontainer/local-state-backup/vscode-data.tar.gz \
  -C /home/vscode/.vscode-server/data .
tar -tzf .devcontainer/local-state-backup/copilot.tar.gz >/dev/null
tar -tzf .devcontainer/local-state-backup/vscode-data.tar.gz >/dev/null
```

The backup directory is ignored by Git and excluded from production image
builds because `.devcontainer` is already excluded. Archives can contain
private chats, tokens, and extension state: keep them local and restrict host
filesystem access. Never commit, upload, or share them.

Active VS Code logs are excluded; they are not chat history.
This is a filesystem snapshot, not a transactionally consistent backup of
running extensions. Avoid other chat/extension activity while copying. If tar
reports files changing or another error, repeat the backup before proceeding.
Backups do not include chats held only in host-side VS Code storage.

### 2. Seed the volumes from host PowerShell

Open a separate Windows PowerShell terminal in the repository root. Docker
Desktop must be running. The development image must already exist locally.
These commands do not download an image or model.

```powershell
docker volume create hr-multi-agent-copilot-state
docker volume create hr-multi-agent-vscode-data

$backup = (Resolve-Path ".devcontainer/local-state-backup").Path
$restore = (Resolve-Path ".devcontainer/restore-local-state.sh").Path
docker run --rm --pull never --user root `
  --mount "type=bind,source=$backup,target=/backup,readonly" `
  --mount "type=bind,source=$restore,target=/restore-local-state.sh,readonly" `
  --mount "type=volume,source=hr-multi-agent-copilot-state,target=/copilot" `
  --mount "type=volume,source=hr-multi-agent-vscode-data,target=/vscode-data" `
  mcr.microsoft.com/devcontainers/python:1-3.11-bookworm `
  sh /restore-local-state.sh

if ($LASTEXITCODE -ne 0) {
  throw "State restoration failed. Do not rebuild until resolved."
}
```

Restoration refuses nonempty volumes instead of overwriting them. If it fails,
inspect the error and retain the backups; do not delete volumes blindly.
The [restore script](../.devcontainer/restore-local-state.sh) avoids nested
shell quoting, which Windows PowerShell can alter when invoking native commands.
It validates both archives before extracting either one.
For a fresh installation with no state to migrate, Compose creates the volumes
automatically. The development Dockerfile creates their mount points with
`vscode` ownership before Docker attaches the volumes.

### Rebuild fails with a VS Code server permission error

If the log reports `mkdir: cannot create directory
'/home/vscode/.vscode-server/bin': Permission denied`, the container started,
but VS Code could not install its remote server. Mounting only the nested
`data` directory into the base image can cause Docker to create the
`.vscode-server` parent as `root:root`. Restoring the data volume does not
change ownership of that parent.

Compose now builds the [development Dockerfile](../.devcontainer/Dockerfile),
which creates the parent and mount points owned by `vscode` before connection.
Use **Dev Containers: Rebuild Container** to apply this image change; simply
reopening an old container will not repair it. Do not delete or re-seed the
state volumes. Their existing contents and the backup archives are retained.
This repair must happen before connection, not in `postCreateCommand`.

### 3. Rebuild and verify

#### 3a. Rebuild using the VS Code interface on Windows

Only proceed after Step 2 prints `State restored successfully.`
In the VS Code window connected to the existing container, press
**Ctrl+Shift+P** and select **Dev Containers: Rebuild Container**.
This is a Command Palette action, not a PowerShell or Bash command.
Wait for VS Code to reconnect and dependency installation to finish.

#### 3b. Verify using the rebuilt container's Linux terminal

In the reconnected VS Code window, select **Terminal -> New Terminal**.
Run the following in that Linux terminal, not Windows PowerShell:

```bash
cd /workspaces/hr-multi-agent-system
findmnt -T /home/vscode/.copilot
findmnt -T /home/vscode/.vscode-server/data
test -w /home/vscode/.copilot && echo "Copilot directory is writable"
test -w /home/vscode/.vscode-server/data && echo "VS Code data directory is writable"
git config --local --get user.name
git config --local --get user.email
```

Both state directories should be separate mounts and writable. The Git
commands should print `Francis Batista` and
`batistafrancis@users.noreply.github.com`. Missing output or a failed command
needs investigation before treating migration as complete.

#### 3c. Verify chat history using the VS Code/Copilot interface

Open the same chat/session view you used before rebuilding and check that
past conversations are available. This is an interface check, not a terminal
command. Preserving
files does not guarantee that every extension version or chat interface will
rediscover its history. Keep backups until you have verified restoration.
Afterward, delete only the two named backup archives if no longer needed.

## Git identity

Run in the Linux Dev Container terminal from
`/workspaces/hr-multi-agent-system`, not Windows PowerShell.
Configure identity once, without changing global Git settings:

```bash
git config --local user.name "Francis Batista"
git config --local user.email "batistafrancis@users.noreply.github.com"
```

These values live in the persistent repository's `.git/config`, not tracked
source files. A new clone needs its own identity configuration.
If Step 3b already prints the correct values, no configuration change is needed.

## Host SSH-agent forwarding

Do not generate or copy a private key into this container just to fix a push.
Dev Containers supports forwarding a host SSH agent.

### A. Enable the agent on Windows (administrator PowerShell)

Open a separate Windows PowerShell window with **Run as administrator**.
Do not run these commands in the Dev Container:

```powershell
Set-Service ssh-agent -StartupType Automatic
Start-Service ssh-agent
```

### B. Load your key on Windows (normal PowerShell)

Open normal, non-administrator Windows PowerShell on the host. Run:

```powershell
ssh-add "$env:USERPROFILE\.ssh\id_ed25519"
ssh-add -l
ssh -T git@github.com
```

Replace the filename with your actual existing key. Its public key must be
registered with GitHub. Confirm any first-connection host-key fingerprint
against GitHub's published fingerprints; do not disable host-key checking.
GitHub's SSH test can exit with status 1 even when authentication succeeds;
read the authentication message.

### C. Reconnect using the Windows desktop and VS Code interface

Save your work. Fully restart VS Code after starting/loading the host agent if necessary,
then reopen the Dev Container through the Dev Containers extension. The agent
must be forwarded by VS Code; a hard-coded socket path in Compose is not a
portable substitute.

### D. Verify forwarding inside Linux (Dev Container terminal)

After VS Code reconnects, select **Terminal -> New Terminal** and run these
commands inside the Linux container, not Windows PowerShell:

```bash
cd /workspaces/hr-multi-agent-system
test -n "$SSH_AUTH_SOCK" && test -S "$SSH_AUTH_SOCK"
ssh-add -l
ssh -T git@github.com
git ls-remote origin HEAD
```

If the agent socket is absent, check the host agent and Dev Containers logs.
If it exists but has no identities, load the key on the host. If identities
exist but GitHub rejects authentication, check the registered public key.
None of these checks pushes or rewrites remote history.
