# Claude Code OAuth authentication for Harbor

The Claude Code OAuth token lives in GNOME Keyring through the freedesktop
Secret Service API. It is never stored in this repository or exported from a
shell profile.

The tracked `~/.local/bin/with-claude-oauth` launcher retrieves the token and
exports `CLAUDE_CODE_OAUTH_TOKEN` and `CLAUDE_FORCE_OAUTH=1` only to the command
it launches. Use it around the host command that starts Harbor so Harbor can
forward the authentication to Claude Code inside its agent container.

The normal `claude` command is unchanged and continues to use Claude Code's
regular local subscription login.

## Generate and store the token

First generate an OAuth token using the supported Claude Code command:

```bash
claude setup-token
```

Copy the generated token. Then run the following manually in a terminal so the
token never passes through an agent or appears in shell history:

```bash
read -rsp "Claude Code OAuth token: " token
echo
printf '%s' "$token" | secret-tool store \
  --label="Claude Code OAuth token" \
  service claude-code \
  credential oauth-token \
  user "$USER"
unset token
```

The desktop may ask you to unlock the login keyring.

## Verify

First verify that the keyring entry exists without printing its value:

```bash
if secret-tool lookup \
  service claude-code \
  credential oauth-token \
  user "$USER" >/dev/null
then
  echo "Claude OAuth token is present in the desktop keyring."
else
  echo "Claude OAuth token is missing from the desktop keyring."
fi
```

Then verify the launcher without printing the token:

```bash
with-claude-oauth sh -c '
  test -n "$CLAUDE_CODE_OAUTH_TOKEN" &&
  test "$CLAUDE_FORCE_OAUTH" = 1
'
```

The current shell is expected not to contain `CLAUDE_CODE_OAUTH_TOKEN`; the
launcher exports it only to the launched command and its children.

## Run Vaadin Bench or Harbor

From the Vaadin Bench checkout, prefix the normal command with the launcher:

```bash
with-claude-oauth uv run vaadin-bench.py -c vanilla -m haiku -t flow-new-view -k 1
```

The same form works when invoking Harbor directly:

```bash
with-claude-oauth uv run harbor run -p tasks -a claude-code
```

The variables are present in Vaadin Bench, inherited by its Harbor subprocess,
and forwarded by Harbor to containerized Claude Code. They do not affect later
commands in the terminal.

Do not print `CLAUDE_CODE_OAUTH_TOKEN` or add it to `.bashrc`, Claude settings,
an environment file, a command argument, or this repository.

If the token expires, run `claude setup-token` again and repeat the keyring
storage command to replace it. New `with-claude-oauth` runs retrieve the
replacement automatically.

## Security boundary

The launcher limits routine exposure to the Harbor command tree, but every
process in that tree can technically inherit the token. Harbor is expected to
forward it to Claude Code. The unlocked desktop keyring is not a security
boundary against arbitrary processes already running as the same local user.
Agent command and network approvals therefore remain independently important.

If `CLAUDE_CODE_OAUTH_TOKEN` is already supplied by a trusted automation
environment, the launcher uses that value instead of querying the keyring.
