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

The display policy follows UTM resize requests through SPICE and Hyprland.
Validated on 2026-10-28 with fullscreen/windowed transitions, Retina and
2560×1440 external displays, and host sleep/wake.

- Cold startup (no outputs yet) requests **3840×2160 at 60 Hz, scale 2**.
  Configuration reloads preserve the live virtual display resolution, layout,
  and scale instead of resetting a UTM-selected mode to 4K.
- `vm-spice-display-agent` receives UTM monitor requests from the packaged
  SPICE daemon and applies them through Hyprland. The packaged session agent
  handles other traffic through a private Unix socket. A user service drop-in
  runs the adapter as the existing `spice-vdagent.service`; no system package
  or additional service unit is installed. It supports one active virtual output.
  Complete requests are coalesced until no new request arrives for one second.
  Malformed or multi-output layouts are rejected without partial application.
  Requests are structured protocol messages, not parsed debug logs.
  See upstream [local framing](https://gitlab.freedesktop.org/spice/linux/vd_agent/-/blob/master/src/udscs.h)
  and [monitor messages](https://spice.pages.freedesktop.org/spice-space/agent-protocol.html).
- `vm-display-scale` waits for three matching samples over one second before
  applying a scale-only change. If resizing continues for five seconds, it
  defers to the next event or timer tick. Sleeping/disabled/zero-sized outputs are ignored.
- Scale switches to 2× at **1900 pixels high or above**, to 1× at **1600 or
  below**, and stays unchanged between those thresholds. Odd dimensions also
  retain their scale in the scale-only helper. The native adapter rounds a
  requested 2× mode down by at most one pixel per dimension so odd window sizes
  do not cause scale flips. Neither helper identifies physical Retina density.
  SPICE monitor requests do not include refresh rate: the adapter retains the
  guest output refresh rate (currently 60 Hz).
- Immediately before applying, compositor-side guards reject a stale sampled
  size/scale. The rule uses the compositor's live mode, position, and transform.
- Hyprland startup, reload, and layout events start the helper. A timer checks
  every 15 seconds (one-second timer accuracy); already-correct outputs are a
  no-op. Only attempted scale changes or failures are logged by the helper.
- GTK uses `GDK_SCALE=1`; existing GTK applications need restarting to inherit it.

Inspect actual resolution and scaling changes:

```bash
journalctl --user -u spice-vdagent.service -u vm-display-scale.service -f -o cat
~/.local/bin/vm-display-scale --dry-run
```

Try fullscreen → windowed → fullscreen, moving UTM between Retina and non-Retina
screens, and host lid close/open. Note the timestamp of any blink. The helper
cannot fix host/guest transport failures or determine the host display density.
UTM Auto Resolution must be enabled and the VM must be visible on the intended
host screen. Attaching a monitor alone does not move the VM to that monitor.

To return to the configuration before the native resize work from a clean
checkout (this checks out the historical commit in detached HEAD mode):

```bash
cd ~/dotfiles
systemctl --user stop spice-vdagent.service
rm ~/.config/systemd/user/spice-vdagent.service.d/60-native-display.conf
rm ~/.local/bin/vm-spice-display-agent
git switch --detach 52cf117
systemctl --user daemon-reload
hyprctl reload
hyprctl configerrors
systemctl --user restart vm-display-scale.timer
systemctl --user restart spice-vdagent.service
```

## Temporarily test stock display behavior

The personal display policy and native SPICE adapter are reversible. The
adapter handles host resolution requests; the separate scale-only helper
reconciles resolutions already reported by Hyprland. For a stock test, disable
both the adapter and scale policy. Clipboard integration is separate.

To test the installed Omarchy monitor defaults, disable the scale timer and
replace the personal monitor-config **symlink** with a copy of the shipped
configuration:

```bash
# Remove only the deployed adapter drop-in symlink for the stock test.
rm ~/.config/systemd/user/spice-vdagent.service.d/60-native-display.conf
systemctl --user daemon-reload
systemctl --user restart spice-vdagent.service
systemctl --user disable --now vm-display-scale.timer
cp --remove-destination /usr/share/omarchy/config/hypr/monitors.lua "$HOME/.config/hypr/monitors.lua"
hyprctl reload
systemctl --user stop vm-display-scale.service
# Match the shipped monitor template's GDK_SCALE=2 on this installation.
systemctl --user set-environment GDK_SCALE=2
hyprctl configerrors
```

`--remove-destination` is essential: it replaces the symlink instead of writing
through it into the Git checkout. Loading the shipped file removes the custom
monitor event handlers as well as the fixed 4K override. Disabling only the
timer is insufficient because the personal event handlers also start the
service. Stopping the service after reload covers a run queued by an old
handler during the transition.

These commands change the active display policy immediately; stock `preferred`
may select 1280×800 or fractional scaling. Restart GTK applications for their
new environment, or log out/in to test session startup as well. You can then
resize the host window and test host sleep/wake with the personal display
policy absent. Keyboard, clipboard, themes, and other personal settings remain
in use; this is a display-policy comparison, not a completely stock desktop.

Restore the personal display policy and timers with:

```bash
cd ~/dotfiles
./bootstrap
```

Bootstrap backs up the temporary stock monitor file and reinstates the tracked
symlink, branch-specific display policy, SPICE adapter, event handlers, timer,
and `GDK_SCALE=1`. It also reapplies the other documented settings. `scripts/validate` intentionally fails
while stock-display testing is active because the monitor file is temporarily
outside Stow and the scaling timer is disabled.

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
systemctl --user stop spice-vdagent.service
stow --dir="$HOME/dotfiles" --target="$HOME" --no-folding --delete desktop
systemctl --user daemon-reload
systemctl --user restart spice-vdagent.service
```

Then restore the selected files from the timestamped backup before reloading
Hyprland. Backups contain the replaced user files; the separately installed
Vaadin theme and any installed packages remain until explicitly removed.
