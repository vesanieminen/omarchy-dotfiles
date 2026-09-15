# Change log

This log records material machine mutations made while establishing the
repository. Read-only diagnostics are omitted because they do not contribute
to recreating the machine; reproducible provisioning commands live in
`docs/commands.md` and `bootstrap`.

## 2026-09-15

1. Disabled and removed the first, untracked version of the SPICE scaling
   units and helper.
2. Restored `~/.config/hypr/monitors.lua` byte-for-byte from the pre-change
   backup `~/.config/hypr/monitors.lua.bak.20260915-173325`.
3. Initialized this repository:

   ```bash
   git init -b main ~/dotfiles
   ```

4. Captured the unmodified monitor configuration and initial package state in
   commit `a78ecd3` (`Capture initial Omarchy machine state`).
5. Added the resolution-aware display policy, watcher, bootstrap, package
   inventory tooling, and documentation in commit `3625ccc`
   (`Add reproducible SPICE display scaling`).
6. Attempted the customary package command:

   ```bash
   omarchy pkg add stow
   ```

   The non-interactive agent session could not accept a `sudo` password, so
   installation was completed through desktop PolicyKit authentication:

   ```bash
   pkexec pacman -S --needed --noconfirm stow
   ```

   Installed package: GNU Stow 2.4.1-1.
7. Applied the committed setup:

   ```bash
   cd ~/dotfiles
   ./bootstrap
   ```

   The prior live monitor file was preserved under
   `~/.local/state/dotfiles/backups/20260915-182342/`, the `desktop` package
   was linked into `$HOME`, and `spice-display-scale.path` was enabled.
8. Refreshed package inventories after installing Stow:

   ```bash
   ./scripts/snapshot-packages
   ```

9. Verified the live state: `Virtual-1` was 3456x2160 at scale 2, the path
   watcher was enabled and active, all deployed files resolved into this
   repository, and `hyprctl configerrors` returned no errors.
