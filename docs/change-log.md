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
10. Captured Omarchy's original Mise-based `gh` launcher unchanged in commit
    `ea0412a` (`Capture Omarchy gh launcher baseline`).
11. Added the keyring-backed `GH_TOKEN` wrapper, its bootstrap handling, and
    authentication documentation in commit `c8a725b` (`Add keyring-backed
    GitHub CLI for agents`). The PAT itself is intentionally not tracked.
12. Applied the committed setup again:

    ```bash
    cd ~/dotfiles
    ./bootstrap
    ```

    The original live `~/.local/bin/gh` was preserved under
    `~/.local/state/dotfiles/backups/20260915-185717/`, then replaced by the
    Stow-managed link. Hyprland configuration validation succeeded.
13. Found that Omarchy's Mise activation placed the installed `gh` ahead of
    `~/.local/bin`, bypassing the tracked wrapper. Captured the untouched
    Omarchy `.bashrc` in commit `32c3067` (`Capture Omarchy bash startup
    baseline`).
14. Added a tracked PATH preference for interactive terminals and
    non-interactive agent shells in commit `8fb03c8` (`Prefer tracked commands
    over Mise shims`).
15. Applied the committed setup again with `./bootstrap`. The original live
    `.bashrc` was preserved under
    `~/.local/state/dotfiles/backups/20260915-194943/`, then replaced by the
    Stow-managed link.
16. Verified that `command -v gh` selects the tracked wrapper and that
    `gh auth status` succeeds using `GH_TOKEN`. Neither the account name nor
    token output is recorded here.
17. Found that terminals launched during the existing UWSM session inherited
    its pre-change PATH before Bash startup. Added the supported per-user UWSM
    environment override in commit `153f58c` (`Persist user command precedence
    in UWSM`) and deployed it with `./bootstrap`. It takes effect when UWSM
    creates the next graphical session, after logout/login or reboot.
18. Configured the existing public GitHub repository as `origin` and published
    `main`. The account-specific URL is intentionally omitted from committed
    history. Authentication uses the tracked keyring-backed `gh` wrapper as a
    one-shot Git credential helper rather than modifying global Git config:

    ```bash
    git remote add origin <existing-public-repository-url>
    git -c credential.helper= \
      -c credential.helper='!gh auth git-credential' \
      push -u origin main
    ```
19. Restored `~/.config/hypr/input.lua` to Omarchy's fully commented user
    template and added that pristine template to the Stow package in commit
    `9a7cd6f` (`Track pristine Omarchy input configuration`). Applied it with
    `./bootstrap`; the previous hand-edited file remains recoverable under
    `~/.local/state/dotfiles/backups/20260915-200734/`. Hyprland reloaded and
    validated without configuration errors.
20. Clarified in commit `bc8b2f5` (`Document automatic Stow installation`)
    that GNU Stow is a deployment dependency installed automatically by
    `./bootstrap` from the tracked package inventory.
21. Enabled global Hyprland natural scrolling for the QEMU/SPICE pointer
    devices in commit `072b253` (`Enable natural scrolling for VM pointers`).
    The change was prepared and committed in a temporary Git worktree before
    `main` was fast-forwarded, ensuring the Stow-linked live file changed only
    after the commit existed. Applied and verified with:

    ```bash
    hyprctl reload
    hyprctl configerrors
    hyprctl getoption input:natural_scroll
    ```

    Hyprland reported no errors and an effective value of `true`.
22. Captured the active Foot terminal's font-size-only override at `11pt`.
    The tracked file matched its live source byte-for-byte before deployment;
    other terminal configurations remain at Omarchy defaults. Applied with
    `./bootstrap`, which replaced the unmanaged Foot config with a Stow-managed
    link while preserving its contents.
23. Kept the font capture limited to the active Foot terminal. Restored
    Alacritty and Ghostty to their shipped `9pt` defaults with:

    ```bash
    omarchy refresh config alacritty/alacritty.toml
    omarchy refresh config ghostty/config
    ```

    Both restored files matched their packaged Omarchy sources byte-for-byte
    and remain outside the Stow package.
24. Fixed the SPICE scaling policy failing after reboot. The user systemd
    transaction had an ordering cycle because the watcher was wanted by
    `graphical-session.target` but ordered after `spice-display-bridge`, while
    the bridge itself starts after the graphical target. Removed the watcher's
    `After=spice-display-bridge.service` constraint so it can begin watching
    before the bridge writes display state. The triggered scale service remains
    ordered after the bridge. Also found that the packaged SPICE bootstrap
    replaces the Stow-managed `monitors.lua` link with its generated
    single-scale block at every graphical login. Extended the tracked scale
    helper to restore that link after bootstrap and validate the Hyprland
    configuration before applying the per-resolution policy.
25. A reboot test showed that SPICE can reuse an unchanged persisted display
    state, so `PathChanged=` alone does not guarantee a scale-policy run at
    login. Enabled `spice-display-scale.service` as a dependent of
    `spice-display-bridge.service`, with the existing ordering constraint
    keeping it after the bridge starts. The path watcher remains enabled for
    subsequent display-state changes.
26. Removed the Basecamp, Google Messages, Google Photos, HEY, and Zoom web-app
    launchers with Omarchy's supported removal command. Added an idempotent
    tracked script and invoked it from `bootstrap` so the same apps are removed
    when recreating the machine:

    ```bash
    ~/dotfiles/scripts/remove-webapps
    ```
27. Added Google Contacts and Google Maps to the tracked web-app exclusion list
    and removed their user-level launchers with the same idempotent script.
28. Fixed scaling after host sleep. Resume emitted a burst of seven SPICE
    layouts in roughly 300 milliseconds; repeated watcher activations hit
    systemd's service start limit before the final Retina layout, leaving both
    the service and path unit failed at `1x`. Added a 500-millisecond debounce
    before reading display state and disabled start limiting for the idempotent
    scale service so the settled final layout is always applied.

## 2026-09-16

1. Simplified `spice-display-scale` so unchanged scales are a no-op and a
   superseded SPICE state is never applied. The helper updates a monitor only
   when it crosses the 1800-pixel threshold: `1x` below it and `2x` at or above
   it. This preserves automatic scaling after login, sleep/wake, and host
   display changes without reapplying every layout.
2. Verified both final transitions: 2560x1440 resolves to `1x` and 3456x2160
   resolves to `2x`. Repeating the helper at the correct scale performs no
   update. The packaged SPICE bridge and scaling path watcher remain active,
   and Hyprland reports no configuration errors.
3. Added a Hyprland `config.reloaded` handler that starts the idempotent scale
   service after every successful configuration reload. This restores the
   correct scale after a temporary config error even when SPICE display state
   has not changed.
4. Set the global pointer scroll factor to `0.4` for slower Mac-like trackpad
   scrolling. The setting is global because UTM exposes the built-in trackpad
   as QEMU/SPICE mouse devices rather than a multitouch libinput touchpad.
5. Added a temporary, no-reload cleanup for stale Hyprland scale warnings.
   After each settled SPICE display event, the helper runs `hyprctl seterror
   disable` only when `hyprctl configerrors` is empty. This avoids the
   configuration reload feedback loop while preserving real parsing errors.
   Remove the cleanup after the SPICE bridge guarantees compatible mode and
   scale values atomically.

## 2026-09-17

1. Added the unused, Finnish-Mac-keyboard-friendly Control-Command-Shift-S
   shortcut to run Omarchy's supported `omarchy-launch-screensaver force`
   action. It leaves all default bindings intact, including
   Control-Command-Q for Calculator.
2. Set the emulated `qemu-qemu-usb-mouse` to a flat acceleration profile at
   sensitivity `0`. UTM forwards captured macOS pointer deltas through this
   relative device; avoiding a second libinput acceleration curve produced the
   desired macOS-like pointer feel. Natural scrolling and the global `0.4`
   scroll factor remain unchanged for the emulated pointer devices.
3. Exported `CODEX_FORCE_AUTH_JSON=1` from the tracked `.bashrc` before the
   non-interactive-shell guard, making the Codex authentication preference
   persistent for both terminal and agent Bash sessions without tracking any
   credentials.
