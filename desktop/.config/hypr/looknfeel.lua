-- Preserve alpha-capable buffer formats on the UTM virtio GPU.
-- Hyprland 0.57's default otherwise makes transparent shell surfaces opaque,
-- covering the wallpaper and windows with black.
-- https://github.com/omacom/omarchy/issues/17061
hl.config({ quirks = { skip_non_kms_dmabuf_formats = false } })
