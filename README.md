# Vesa's Omarchy machine configuration

This repository contains personal configuration layered on top of Omarchy.
Omarchy-owned files under `/usr/share/omarchy` are intentionally not modified
or copied here.

## Rebuild

Install Omarchy, clone this repository as `~/dotfiles`, then run:

```bash
cd ~/dotfiles
./bootstrap
```

The bootstrap script:

1. restores the tracked explicit package set through Omarchy's package helpers;
2. backs up conflicting stock files that the repository will manage;
3. links the `desktop` package into the home directory;
4. enables resolution-aware SPICE display scaling;
5. reloads and validates Hyprland.

## Layout

- `desktop/` — files deployed into `$HOME` by Stow.
- `packages/explicit.txt` — explicitly installed packages.
- `packages/all-with-versions.txt` — complete package snapshot for auditing.
- `packages/foreign.txt` — packages outside the configured sync databases.
- `scripts/snapshot-packages` — refreshes the package snapshots.
- `scripts/install-packages` — restores the tracked explicit package set.
- `docs/commands.md` — reproducible commands and maintenance workflow.
- `docs/github-auth.md` — keyring-backed GitHub CLI authentication for agents.

## GitHub authentication for agents

The tracked `~/.local/bin/gh` wrapper retrieves a fine-grained GitHub PAT from
the desktop keyring and exposes it as `GH_TOKEN` only to the `gh` process. The
secret itself is never stored in this repository. Follow
`docs/github-auth.md` once on each machine to populate the keyring. The tracked
`.bashrc` keeps `~/.local/bin` ahead of Mise-managed tools in both interactive
terminal shells and non-interactive agent shells.

## Monitor policy

SPICE owns the virtual monitor resolution and layout. Virtio supplies a fake
physical display size, so Hyprland cannot infer DPI correctly. The personal
policy uses integer scaling based on each virtual display's pixel height:

- below 1800 pixels high: `1x`;
- 1800 pixels high or above: `2x`.

This gives a 2560x1440 external display `1x` scaling and the MacBook Pro's
3456x2160 Retina display `2x` scaling. A user path unit reapplies the policy
whenever SPICE writes a new display state.

## Updating the snapshot

After installing or removing packages:

```bash
cd ~/dotfiles
./scripts/snapshot-packages
git add packages
git commit -m "Update package snapshot"
```

`packages/all-with-versions.txt` records the exact observed versions for
auditing. Arch is rolling-release, so restoration installs the currently
available versions of the explicitly tracked packages rather than attempting
unsafe downgrades to historical package builds.
