# Reproducible commands

The repository records desired state and the commands that recreate it. It
does not preserve transient diagnostics or blindly replay shell history.

## Initial application

```bash
git clone <your-dotfiles-repository> ~/dotfiles
cd ~/dotfiles
./bootstrap
```

`bootstrap` contains the actual provisioning commands. In order, the material
operations are:

```bash
"$HOME/dotfiles/scripts/install-packages"
stow --dir="$HOME/dotfiles" --target="$HOME" --restow desktop
systemctl --user daemon-reload
systemctl --user enable --now spice-display-scale.path
systemctl --user start spice-display-scale.service
systemctl --user set-environment GDK_SCALE=1
hyprctl reload
hyprctl configerrors
```

## Package inventory

```bash
cd ~/dotfiles
./scripts/snapshot-packages
```

The versioned complete package list is an audit snapshot. On a fresh Omarchy
installation, `bootstrap` restores explicitly installed repository packages
through Omarchy's package helpers. It does not attempt to downgrade packages
to the historical versions in the audit snapshot.

## Remove the desktop links

```bash
systemctl --user disable --now spice-display-scale.path
stow --dir="$HOME/dotfiles" --target="$HOME" --delete desktop
```

This removes only Stow-managed links. Backups made by `bootstrap` remain under
`~/.local/state/dotfiles/backups/`.

## GitHub authentication

Store the fine-grained PAT once using the commands in `docs/github-auth.md`.
After that, both humans and approved local agents can use the normal `gh`
command. The tracked wrapper retrieves the token without printing it.
