-- UTM controls resolution in fullscreen and windowed mode.
hl.env("GDK_SCALE", "1")
hl.monitor({ output = "", mode = "preferred", position = "auto", scale = 1 })

-- Preserve live virtual modes on reload. On cold startup, fall back to the
-- 16-inch MacBook Pro fullscreen area previously requested by UTM (below the
-- notch). Host-driven resizes override this for windows and external displays.
local monitors = hl.get_monitors()
if #monitors == 0 then
  hl.monitor({ output = "Virtual-1", mode = "3456x2160@60", position = "0x0", scale = 2 })
else
  for _, m in ipairs(monitors) do
    if m.name:match("^Virtual%-") and m.width > 0 and m.height > 0 then
      hl.monitor({ output = m.name,
        mode = string.format("%dx%d@%.5f", m.width, m.height, m.refresh_rate),
        position = string.format("%dx%d", m.x, m.y),
        scale = m.scale, transform = m.transform })
    end
  end
end

local function update_scale()
  hl.exec_cmd("systemctl --user --no-block start vm-display-scale.service")
end
hl.on("hyprland.start", update_scale)
hl.on("config.reloaded", update_scale)
hl.on("monitor.layout_changed", update_scale)
