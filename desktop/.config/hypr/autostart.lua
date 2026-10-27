-- Preserve this official VM's working host/guest text clipboard integration.
o.launch_on_start(os.getenv("HOME") .. "/.local/bin/omarchy-vm-clipboard-bridge")
