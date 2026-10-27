# Reproducible commands for the official Omarchy VM

## First installation

```bash
git clone https://github.com/vesanieminen/omarchy-dotfiles.git ~/dotfiles
cd ~/dotfiles
./bootstrap
```

Run bootstrap in the active graphical session as your regular user. Its
tracked scripts are the authoritative provisioning workflow:

1. `scripts/install-packages` installs only `packages/required.txt` via
   `omarchy pkg add`; it never restores audit snapshots or custom repositories.
2. Back up conflicting user files and symlinks under
   `~/.local/state/dotfiles/backups/<timestamp>/`.
3. `stow --dir="$HOME/dotfiles" --target="$HOME" --no-folding --restow desktop`.
4. `systemctl --user daemon-reload` and
   `systemctl --user set-environment GDK_SCALE=1`.
5. `hyprctl reload` and `hyprctl configerrors`.
6. Enable/start `vm-display-scale.timer` and run `vm-display-scale.service`.
7. On first installation,
   `omarchy theme install https://github.com/vesanieminen/omarchy-vaadin-theme.git`.
8. Enable/start `auto-omarchy-theme.timer` and run `auto-omarchy-theme.service`.
9. `scripts/remove-webapps`, `omarchy restart terminal`, and `scripts/validate`.

Open a new Foot window for the font setting. Log in again to apply the UWSM
session PATH; restart GTK applications for their changed GDK_SCALE.

## Verification and snapshots

```bash
cd ~/dotfiles
./scripts/validate
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests
hyprctl -j monitors
hyprctl getoption input:kb_layout
hyprctl getoption input:kb_variant
hyprctl getoption input:natural_scroll
hyprctl getoption input:scroll_factor
systemctl --user list-timers vm-display-scale.timer auto-omarchy-theme.timer
./scripts/snapshot-packages
git diff --check
git diff
```

Snapshots record current package versions for auditing and are never used to
install an obsolete kernel or custom ARM packages.

## GitHub writes

For this machine's existing GitHub CLI keyring authentication, a one-shot
credential helper avoids persisting additional global Git configuration:

```bash
git -c credential.helper= -c 'credential.helper=!gh auth git-credential' push origin main
```

No tokens appear in Git configuration, command arguments, or repository files.
