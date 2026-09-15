# GitHub CLI authentication for local agents

The fine-grained GitHub PAT lives in GNOME Keyring through the freedesktop
Secret Service API. GNOME Shell is not required; Omarchy's Hyprland session
already includes `gnome-keyring`, `libsecret`, and `secret-tool`.

The tracked `~/.local/bin/gh` wrapper looks up the PAT and exports `GH_TOKEN`
only for the lifetime of the real GitHub CLI process. It then delegates to
Omarchy's original Mise-based `gh` launcher behavior.

The tracked `~/.bashrc` gives `~/.local/bin` precedence after Omarchy's Mise
activation. This ensures that the wrapper is selected by both interactive
terminals and non-interactive agent shells, while the wrapper deliberately
uses `mise x gh` to invoke the real CLI without recursion.

The tracked `~/.config/uwsm/env.d/90-dotfiles-path` also puts
`~/.local/bin` first in the graphical session inherited by terminals and other
UWSM-launched applications. UWSM loads this file on login, so log out and back
in—or reboot—after deploying it for the first time.

## Store or replace the token

Run this manually in a terminal so the PAT never passes through an agent or
appears in shell history:

```bash
read -rsp "Fine-grained GitHub PAT: " token
echo
printf '%s' "$token" | secret-tool store \
  --label="GitHub CLI fine-grained PAT" \
  service github-cli \
  host github.com \
  user "$USER"
unset token
```

The desktop may ask you to unlock the login keyring.

## Verify

```bash
gh auth status
gh repo list --limit 5
```

Do not run `gh auth status --show-token`, print `GH_TOKEN`, or add the PAT to
the repository, `~/.bashrc`, `config.toml`, an environment file, or a command
argument.

## Agent behavior and security boundary

Agents may invoke the normal `gh` command. Network and command approvals still
apply independently. The PAT should be fine-grained, repository-restricted,
short-lived, and limited to only the permissions agents actually need.

If `GH_TOKEN` is already supplied by a trusted automation environment, the
wrapper uses that value and does not query the desktop keyring.
