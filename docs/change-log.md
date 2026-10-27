# Migration log

## 2026-10-27 — official Omarchy Linux VM

The user designated this freshly installed official Omarchy VM as the
canonical Linux VM and approved migration of personal settings while excluding
the former custom package distribution.

1. Cloned `https://github.com/vesanieminen/omarchy-dotfiles.git` to `~/dotfiles`.
2. Preserved the old main commit `3c8a63f6cfc802356fa22f5492d68749753f7f8d`
   on `archive/custom-arm-vm-2026-10-27` and pushed that branch before editing.
   Historical setup and migration records remain on that branch.
3. Installed GNU Stow from the configured official Arch Linux ARM `extra`
   repository using `pkexec pacman -S --needed --noconfirm stow` because this
   agent session cannot enter a password in an interactive terminal.
4. Replaced bulk package restoration with the minimal dependencies in
   `packages/required.txt`. Preserved the installed official Omarchy packages,
   repository configuration, kernel, bootloader, and existing application set.
5. Replaced the custom SPICE-state scaling integration with a user helper
   reading Hyprland monitors, event triggers, and a reconciliation timer.
   Retained the working 3840×2160@60 2× virtual-monitor startup mode.
6. Preserved the working clipboard helper and tracked its portable autostart.
7. Retained current Omarchy input-template comments and defaults while adding
   the Finnish Macintosh layout and personal pointer settings.
8. Kept native GitHub CLI keyring authentication as a fallback when no optional
   personal PAT entry is provisioned. Removed automatic global Mise changes
   and the release-age bypass from the old wrapper.
9. Updated bootstrap to back up all file/link conflicts, deploy via Stow,
   install the user's Vaadin theme through the official Omarchy theme command,
   enable theme/scaling timers, apply web-app exclusions, and validate.
10. Applied the setup with `./bootstrap`; backups remain outside Git under
    `~/.local/state/dotfiles/backups/`. No credentials were copied or printed.

Verification completed:

- `./bootstrap` succeeded twice; the second run did not create additional
  backups or change the selected theme.
- `scripts/validate` passed: every tracked desktop file links to this checkout,
  both user timers are enabled/active, both services report `Result=success`,
  the Vaadin wallpaper exists, and excluded custom packages are absent.
- Hyprland reports no configuration errors. Effective settings are `fi/mac`,
  natural scrolling enabled, scroll factor `0.4`, and 3840×2160@60 at scale 2.
- Confirmed the new helper's `hyprctl eval` monitor configuration is accepted
  using the existing display mode and scale, without changing resolution.
- GitHub API access succeeds through the new wrapper and the existing native
  keyring login. The optional custom PAT setup was not needed.
- The active background resolves to `03-constellation.jpg`; the installed
  Vaadin source commit is `6941847158cac946c99bb465c736579542201fc6`.
- Refreshed all package audit snapshots with `scripts/snapshot-packages`.
- Shell syntax, display-policy regression tests, and `git diff --check` passed.

The original user files remain under
`~/.local/state/dotfiles/backups/20261027-220437-340544958/`.
No reboot or logout was performed. Host-driven resize and sleep/wake have not
been manually exercised; the official guest stack supplies available display
modes, and config reload intentionally restores this VM's 4K startup mode.

Publication: commit the verified setup on `main` and push with the one-shot
GitHub CLI credential helper documented in `docs/commands.md`.


## 2026-10-27 — command record in bootstrap

Audited bootstrap and its supporting scripts against the migration session.
All configuration-changing steps were already covered by the executable
workflow. Added the successful one-time checkout/archive, PolicyKit package
installation, verification, package snapshot, and Git publication commands as
a comment block in bootstrap itself. This preserves the command record without
making future installations recreate branches, commit, or push automatically.
No deployed configuration or provisioning behavior changed.
