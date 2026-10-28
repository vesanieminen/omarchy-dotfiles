# Remove the configuration and restore backups

These commands run inside the Linux VM. They remove links created by this
repository; they do not uninstall Omarchy or remove the VM from UTM.

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
