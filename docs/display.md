# Display setup and troubleshooting

The display policy follows UTM resize requests through SPICE and Hyprland.
Validated on 2026-10-28 with fullscreen/windowed transitions, Retina and
2560×1440 external displays, and host sleep/wake.

- Cold startup (no outputs yet) requests **3456×2160 at 60 Hz, scale 2**.
  This matches the fullscreen area UTM previously requested on this 16-inch
  M3 Max MacBook Pro below the notch. The old 3840×2160 fallback had a wider
  aspect ratio and could leave unused space when no host resize arrived.
  Configuration reloads preserve the live virtual display resolution, layout,
  and scale instead of resetting a UTM-selected mode to the laptop fallback.
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

If an existing session is stuck at the old 3840×2160 fallback on the laptop,
apply the previously measured fullscreen size once:

```bash
hyprctl eval 'hl.monitor({ output = "Virtual-1", mode = "3456x2160@60", position = "0x0", scale = 2 })'
hyprctl reload
hyprctl configerrors
```

This is a laptop fullscreen correction. UTM Auto Resolution must still be
enabled for subsequent host window and display changes. Reloading or rerunning
bootstrap intentionally preserves the live size; it cannot discover the host
window dimensions without a SPICE request.

## Chromium scaling

`desktop/.config/chromium-flags.conf` selects native Wayland without a forced
device scale factor. Chromium follows the guest output's scale as the VM moves
between host displays, including the existing resolution-based Retina policy
above. The desktop's text-size preference still applies independently.

The `chromium` launcher in `desktop/.local/bin/` selects Mesa software rendering;
the flags disable GPU rendering and accelerated video decoding because the
current UTM graphics backend cannot create Chromium's required GL context.
This trades graphics performance for compatibility. Both files are installed
by bootstrap through Stow, and Chromium is included in the required packages.

After changing flags, open `chrome://restart` to restart the existing browser.
Opening another window alone keeps the old process and its scaling flags.

## Display diagnostics

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

