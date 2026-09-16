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

GNU Stow is required for deployment. On an existing Omarchy installation,
`./bootstrap` installs it automatically from the tracked package inventory
before linking the `desktop` package, so no separate Stow installation step is
needed.

The bootstrap script:

1. restores the tracked explicit package set through Omarchy's package helpers;
2. backs up conflicting stock files that the repository will manage;
3. links the `desktop` package into the home directory;
4. enables resolution-aware SPICE display scaling;
5. reloads and validates Hyprland.

## Layout

- `desktop/` — files deployed into `$HOME` by Stow.
- `desktop/.config/hypr/input.lua` — pristine Omarchy user input template,
  tracked so future personal input overrides are reviewed and reproducible.
- `packages/explicit.txt` — explicitly installed packages.
- `packages/all-with-versions.txt` — complete package snapshot for auditing.
- `packages/foreign.txt` — packages outside the configured sync databases.
- `scripts/snapshot-packages` — refreshes the package snapshots.
- `scripts/install-packages` — restores the tracked explicit package set.
- `scripts/remove-webapps` — removes stock web apps excluded from this setup.
- `docs/commands.md` — reproducible commands and maintenance workflow.
- `docs/github-auth.md` — keyring-backed GitHub CLI authentication for agents.

## GitHub authentication for agents

The tracked `~/.local/bin/gh` wrapper retrieves a fine-grained GitHub PAT from
the desktop keyring and exposes it as `GH_TOKEN` only to the `gh` process. The
secret itself is never stored in this repository. Follow
`docs/github-auth.md` once on each machine to populate the keyring. The tracked
`.bashrc` keeps `~/.local/bin` ahead of Mise-managed tools in both interactive
terminal shells and non-interactive agent shells. The matching UWSM `env.d`
override establishes the same order for the entire graphical session after
login.

## Monitor policy

SPICE owns virtual monitor resolution and layout. Virtio exposes the same fake
physical dimensions at every host resolution, so Hyprland's native `auto`
policy chooses fractional scaling at 2560x1440. The personal policy instead
uses `1x` below 1800 pixels high and `2x` at or above 1800 pixels.

A debounced path service checks each settled SPICE display state after login,
sleep/wake, and host-display changes. It skips outputs already at the desired
scale and applies a monitor update only when crossing the 1x/2x threshold. This
keeps the packaged SPICE bridge responsible for every normal layout update.
A Hyprland `config.reloaded` handler invokes the same idempotent service, so a
successful reload also restores the correct scale after a temporary config
error.

## Input policy

Natural scrolling is enabled at Hyprland's global pointer level. QEMU/SPICE
exposes the Mac trackpad to the VM as emulated pointer devices, not as a
libinput touchpad, so settings under `input.touchpad` do not apply to it. The
global scroll factor is `0.4` for slower, more trackpad-like scrolling. UTM does
not pass finger-count or multitouch contacts to this Linux guest, so clickfinger,
three-finger drag, tap/drag, palm rejection, and Hyprland touchpad gestures
cannot be implemented in the guest.

## Terminal font size

The active Foot terminal uses an `11pt` font. Its configuration otherwise
retains Omarchy's defaults and continues importing the active theme's
generated colors. Other terminal configurations remain at Omarchy defaults.

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
