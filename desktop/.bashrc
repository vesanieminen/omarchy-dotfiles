# Omarchy environment (OMARCHY_PATH + PATH), needed even for non-interactive shells
[[ -r /usr/share/omarchy/default/bash/env-bootstrap ]] && source /usr/share/omarchy/default/bash/env-bootstrap

# Keep Codex authentication in auth.json instead of the system credential store.
export CODEX_FORCE_AUTH_JSON=1

prefer_local_bin() {
  local path_without_local_bin=":${PATH:-}:"
  path_without_local_bin=${path_without_local_bin//:"$HOME/.local/bin":/:}
  path_without_local_bin=${path_without_local_bin#:}
  path_without_local_bin=${path_without_local_bin%:}
  export PATH="$HOME/.local/bin${path_without_local_bin:+:$path_without_local_bin}"
}

# Prefer tracked user commands to Mise shims in non-interactive agent shells.
prefer_local_bin

# If not running interactively, don't do anything else (leave this above the rc source)
if [[ $- != *i* ]]; then
  unset -f prefer_local_bin
  return
fi

# All the default Omarchy aliases and functions
# (don't mess with these directly, just overwrite them here!)
source "$OMARCHY_PATH/default/bash/rc"

# Mise activation prepends installed tools, so restore the user-command order.
prefer_local_bin
unset -f prefer_local_bin

# Add your own exports, aliases, and functions here.
#
# Make an alias for invoking commands you use constantly
# alias p='python'
