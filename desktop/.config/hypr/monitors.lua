-- Official Omarchy VM: retain the known-good UTM Retina mode on login.
-- The guest advertises 1280x800 as preferred even on a Retina host.
hl.env("GDK_SCALE", "1")
hl.monitor({ output = "", mode = "preferred", position = "auto", scale = 1 })
hl.monitor({ output = "Virtual-1", mode = "3840x2160@60", position = "0x0", scale = 2 })

-- Read actual Hyprland outputs; no custom SPICE bridge or state file required.
local function update_scale()
  hl.exec_cmd("systemctl --user --no-block start vm-display-scale.service")
end
hl.on("hyprland.start", update_scale)
hl.on("config.reloaded", update_scale)
hl.on("monitor.layout_changed", update_scale)
