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
- `desktop/.config/hypr/bindings.lua` — personal Hyprland shortcuts, including
  Control-Command-Shift-S to start the Omarchy screensaver on a Finnish Mac
  keyboard.
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

## Codex authentication

The tracked `.bashrc` exports `CODEX_FORCE_AUTH_JSON=1` before its interactive
shell guard, making the setting available to terminal and agent Bash sessions.
The repository records only the behavior flag; it does not contain Codex
credentials or `auth.json`.

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
error. As a temporary workaround for the packaged bridge briefly applying an
odd-sized mode at scale `2`, the helper clears a stale Hyprland error string
with `hyprctl seterror disable`, but only when `hyprctl configerrors` is empty.
It deliberately does not reload Hyprland. Remove this workaround after the
bridge guarantees a compatible mode and scale in the same transaction.

## Input policy

Natural scrolling is enabled at Hyprland's global pointer level. QEMU/SPICE
exposes the Mac trackpad to the VM as emulated pointer devices, not as a
libinput touchpad, so settings under `input.touchpad` do not apply to it. The
global scroll factor is `0.4` for slower, more trackpad-like scrolling. UTM does
not pass finger-count or multitouch contacts to this Linux guest, so clickfinger,
three-finger drag, tap/drag, palm rejection, and Hyprland touchpad gestures
cannot be implemented in the guest.

Captured relative pointer movement arrives through `qemu-qemu-usb-mouse` after
macOS has processed it. That device uses a flat profile at sensitivity `0` so
libinput does not add a second acceleration curve. UTM's uncaptured absolute
tablet path bypasses guest pointer acceleration. This preserves the tested
macOS-like pointer speed and acceleration in both modes.

## Terminal font size

The active Foot terminal uses an `11pt` font. Its configuration otherwise
retains Omarchy's defaults and continues importing the active theme's
generated colors. Other terminal configurations remain at Omarchy defaults.

## Keyboard shortcuts

Control-Command-Shift-S starts Omarchy's screensaver. Hyprland reports the Mac
Command key as `SUPER`; using the letter `S` avoids Finnish-layout symbol-key
differences. The combination is otherwise unused, so all Omarchy defaults,
including Control-Command-Q for Calculator, remain available.

## Keyboard layout

Hyprland uses XKB's Finnish Macintosh layout (`fi` with the `mac` variant) for
the QEMU keyboard. Command remains `SUPER`, Left Option remains conventional
`ALT` for Omarchy shortcuts, and Right Option selects the Macintosh symbol
layer. For example, Right Option-Shift-8 produces `{`.

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
