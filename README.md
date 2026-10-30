# Omarchy dotfiles for a Mac running UTM

Personal settings for **Omarchy Linux running in a UTM virtual machine on a
Mac**. This setup is used on a **2023 16-inch MacBook Pro with an M3 Max**, with
both its Retina screen and an external monitor.

“Dotfiles” are configuration files for the desktop, terminal, and other tools.
This repository customizes an existing Omarchy installation inside the Linux
VM. The Mac runs macOS and UTM; Omarchy runs inside UTM.

## What it adds

- Automatic display resizing when switching between fullscreen and windowed
  mode, with scaling for Retina and lower-resolution displays.
- Text clipboard sharing between macOS and Linux.
- Chromium that follows desktop scaling on Retina and external displays, using
  software rendering for compatibility with the VM graphics driver.
- Finnish Mac keyboard layout, natural scrolling, and mouse adjustments.
- Lupine theme during the day and Vaadin at night, based on Helsinki daylight.
- A themed Foot terminal and optional GitHub and Claude authentication helpers.
- Codex colors that follow light/dark terminal theme changes.

These are personal preferences. Installing also removes the Linux web-app
launchers for Basecamp, Google Contacts, Google Maps, Google Messages,
Google Photos, HEY, and Zoom.

## Install

Start with a working Omarchy Linux VM in UTM. This repository does not install
the operating system or create the VM. The tested setup uses UTM’s QEMU backend
on Apple Silicon. Enable **Auto Resolution** in UTM for automatic display resizing.

Open a terminal **inside the Linux desktop**, as your normal user, and run:

```bash
git clone https://github.com/vesanieminen/omarchy-dotfiles.git ~/dotfiles
cd ~/dotfiles
./bootstrap
```

The setup script installs its dependencies, backs up conflicting settings,
links the configuration files, and starts the display and theme helpers.
It may ask for your Linux password to install packages. You can rerun it to
reapply the settings.

Backups are saved under `~/.local/state/dotfiles/backups/` inside the VM.
Keep `~/dotfiles` in place: the desktop uses files from this checkout.
Open a new terminal window for the font change; log out and back in to apply
all session settings.

## Using the display

Resize the UTM window, enter fullscreen, or move it to another Mac display.
The Linux desktop should follow after about one second. Move the UTM window
to the display you want to use; connecting a monitor alone does not move it.

Fullscreen/windowed transitions, Retina and 2560×1440 external displays, and
Mac sleep/wake were tested on this setup. The adapter supports **one virtual
display** and estimates scaling from the requested resolution.

If the size looks wrong or the screen keeps blinking, see the
[display troubleshooting guide](docs/display.md).

## Check the setup

Run inside the VM:

```bash
cd ~/dotfiles
./scripts/validate
```

This checks configuration links, Hyprland errors, and the theme/scaling helpers.
If it reports a file that is no longer linked, that setting may have been
changed locally.

## More details

The Codex launcher uses the Mise-managed installation with `FORCE_COLOR=1`
and `tui.theme="ansi"`. This keeps syntax, diff, and status colors on the
terminal's 16-color theme palette and avoids cached RGB backgrounds after
day/night theme changes. It reduces the available color range from truecolor.
Bash routes `codex` through this launcher even when Mise rewrites `PATH`
after entering a project directory.
Restart existing Codex sessions to apply it; run `source ~/.bashrc` in an existing
Bash shell before starting `codex resume`. Personal Codex configuration and
credentials are not stored in this repository.

- [Setup commands and checks](docs/commands.md)
- [Display settings, logs, and rollback](docs/display.md)
- [Remove the configuration and restore backups](docs/recovery.md)
- [GitHub authentication](docs/github-auth.md)
- [Claude authentication](docs/claude-auth.md)
- [Change history](docs/change-log.md)

`desktop/` contains the configuration files, `scripts/` contains setup helpers,
and `packages/required.txt` lists dependencies. Other package lists are records
of this machine’s installed packages, not lists to reinstall.

The older custom ARM setup is preserved on the
[`archive/custom-arm-vm-2026-10-27`](https://github.com/vesanieminen/omarchy-dotfiles/tree/archive/custom-arm-vm-2026-10-27)
branch. Use `main` for the current setup.
