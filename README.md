# Official Omarchy Linux VM

Personal configuration for Vesa's UTM Linux VM, installed from official
Omarchy sources. `main` is the reproducible setup for this machine.
The former custom ARM VM is preserved on
[`archive/custom-arm-vm-2026-10-27`](https://github.com/vesanieminen/omarchy-dotfiles/tree/archive/custom-arm-vm-2026-10-27)
at commit `3c8a63f6cfc802356fa22f5492d68749753f7f8d`.

## Install

From a terminal in the running Omarchy desktop, as your regular user:

```bash
git clone https://github.com/vesanieminen/omarchy-dotfiles.git ~/dotfiles
cd ~/dotfiles
./bootstrap
```

Bootstrap installs only the dependencies in `packages/required.txt` using
`omarchy pkg add`, backs up conflicting files and symlinks under
`~/.local/state/dotfiles/backups/<timestamp>/`, and deploys `desktop/` with GNU
Stow. It installs the Vaadin theme, enables the user timers, removes the
excluded web-app launchers, reloads Hyprland, and runs `scripts/validate`.
Rerunning it keeps links to this checkout and does not overwrite theme updates.
A missing dependency may require your sudo password when run in a terminal.

The configured official Omarchy and Arch Linux ARM repositories remain the
source of system packages. No package repository, keyring, kernel, bootloader,
or file under `/usr/share/omarchy` is modified. `packages/explicit.txt`,
`all-with-versions.txt`, `foreign.txt`, and `omarchy-version.txt` are **audit
snapshots only**; bootstrap never restores them. This avoids reinstalling the
old custom ARM distribution or applications removed from this VM.

## Personal settings

- Finnish Macintosh keyboard (`fi`, variant `mac`), global natural scrolling,
  scroll factor `0.4`, and a flat acceleration profile at sensitivity `0` for
  the relative QEMU USB mouse. Other current Omarchy input defaults remain.
- Control–Command–Shift–S starts the screensaver; default shortcuts remain.
- Foot uses the active theme colors and an 11pt font. Existing Foot windows
  retain their font until a new window is opened.
- `~/.local/bin` precedes Mise tools in Bash and UWSM. A new login applies the
  graphical-session PATH; new Bash shells pick it up immediately.
- The existing repository preference `CODEX_FORCE_AUTH_JSON=1` remains in Bash.
- The `gh` wrapper optionally uses the personal keyring PAT, then invokes the
  official Omarchy Mise-selected CLI. If no personal PAT exists, gh's native
  keyring login continues to work. No credentials are tracked.
- `with-claude-oauth COMMAND ...` optionally launches a command with the Claude
  OAuth keyring token. Ordinary local Claude login remains unchanged. See
  [Claude authentication](docs/claude-auth.md).
- The VM's existing text clipboard bridge is tracked and started through the
  user Hyprland autostart file, with `spice-vdagent`, `xclip`, and `wl-clipboard`.
- Excluded web apps: Basecamp, Google Contacts, Google Maps, Google Messages,
  Google Photos, HEY, and Zoom. Their absence is harmless on repeat bootstrap.

## Display policy on official Omarchy

Login and config reload retain this VM's known-good `Virtual-1` mode:
**3840×2160 at 60 Hz, scale 2**. The guest advertises 1280×800 as preferred,
so blindly selecting `preferred` would lose Retina resolution. GTK uses
`GDK_SCALE=1` as in the personal setup; already running GTK applications need
restarting to inherit it.

`vm-display-scale` reads actual Hyprland outputs and scales only `Virtual-*`
outputs: 1× below 1800 pixels high and 2× at/above it. Odd physical dimensions
fall back to 1× to avoid an invalid integer-scale configuration. It preserves
the output's current resolution, refresh rate, position, and transform.
Hyprland startup, reload, and layout-change events start the helper; a user
timer checks every five seconds to catch changes arriving during an active
service run. Already correct outputs are a no-op.

This uses the official Hyprland CLI and user services. It does not install the
former `omarchy-spice-guest-tools`, rely on its `display.state`, or provision
its host-resolution/layout bridge. Automatic host-driven resolution changes
therefore depend on the official guest stack; this helper applies scaling to
whatever resolution the guest actually receives. A config reload restores the
known-good 4K mode. Manual host resize/sleep/wake testing remains useful.

## Automatic themes

The theme helper calculates Helsinki sunrise/sunset locally. It selects
**Lupine by day** and **Vaadin by night**, ten seconds after session activation
and every five minutes. It switches only when needed. Vaadin comes from
[vesanieminen/omarchy-vaadin-theme](https://github.com/vesanieminen/omarchy-vaadin-theme)
through `omarchy theme install`; the theme-set hook selects
`03-constellation.jpg`. Official Omarchy regenerates restricted executable
configuration files from the theme colors.

## Maintenance

```bash
omarchy update
cd ~/dotfiles
./scripts/validate
./scripts/snapshot-packages
git diff
```

Review and commit intentional configuration changes and refreshed snapshots.
See [commands](docs/commands.md), [migration log](docs/change-log.md), and
[GitHub authentication](docs/github-auth.md).

## Remove links / recover files

```bash
systemctl --user disable --now vm-display-scale.timer auto-omarchy-theme.timer
systemctl --user stop vm-display-scale.service auto-omarchy-theme.service
stow --dir="$HOME/dotfiles" --target="$HOME" --no-folding --delete desktop
systemctl --user daemon-reload
```

Then restore the selected files from the timestamped backup before reloading
Hyprland. Backups contain the replaced user files; the separately installed
Vaadin theme and any installed packages remain until explicitly removed.
