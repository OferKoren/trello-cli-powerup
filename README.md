# trello-cli

Lightweight Trello CLI built to be driven by Claude Code during coding sessions. Claude invokes `trello <cmd>` via its Bash tool; your board updates in real time — move cards, leave comments, open new tickets without leaving the terminal.

## Install

**Recommended: pipx from GitHub** (no clone needed, `trello` on PATH globally, isolated env, usable from any project):

```bash
brew install pipx            # first time only (macOS)
pipx ensurepath              # first time only — adds ~/.local/bin to PATH

pipx install git+https://github.com/OferKoren/trello-cli-powerup.git
```

pipx clones the repo into an isolated environment under the hood. You get a `trello` binary without a local checkout.

**Upgrade later:**

```bash
pipx upgrade trello-cli
```

**Pin a branch / tag / commit:**

```bash
pipx install git+https://github.com/OferKoren/trello-cli-powerup.git@main
pipx install git+https://github.com/OferKoren/trello-cli-powerup.git@v0.2.0
```

**Contributing locally** (editable install from a clone):

```bash
git clone https://github.com/OferKoren/trello-cli-powerup.git
cd trello-cli-powerup
pipx install -e .            # changes to source apply without reinstall
```

**Venv alternative** (only works while venv is active — use only if you don't want pipx):

```bash
git clone https://github.com/OferKoren/trello-cli-powerup.git
cd trello-cli-powerup
python -m venv .venv && source .venv/bin/activate
pip install -e .
```

## Auth

Trello's API uses two credentials: a **Power-Up API key** (identifies your app) and a **user token** (grants your app permission to act as you). You need both.

### 1. Create a Power-Up to get an API key

Trello tied API keys to "Power-Ups" a while back, so even a personal CLI needs one:

1. Go to <https://trello.com/power-ups/admin>.
2. Pick a Workspace (any workspace you own — the Power-Up only needs to exist, it is never published).
3. Click **New** → fill in:
   - **Name**: `trello-cli` (anything works).
   - **Workspace**: your workspace.
   - **Iframe connector URL**: leave blank.
   - **Email / Support contact / Author**: your info.
4. Click **Create**.
5. In the new Power-Up's page, open the **API key** tab on the left.
6. Click **Generate a new API key** → accept. Copy the **API key** shown (~32 hex chars). This is your `KEY`.

Alternative shortcut (older accounts only): <https://trello.com/app-key> may show a legacy key directly. If it does, use that and skip the Power-Up step.

### 2. Generate a user token

On the same API key page, to the right of the key you'll see a **Token** link that says something like *"you can manually generate a Token"*. Click it.

1. A Trello auth page opens: *"Would you like to give the following application access to your account?"*
2. Scope shown is **read, write, account** — the CLI needs all three (read cards, write moves/comments, authenticate).
3. Click **Allow**.
4. Trello redirects to a page showing a long token (~64 hex chars). Copy the **token**. This is your `TOKEN`.

Tokens are long-lived by default but you can revoke any token from <https://trello.com/my/account> → **Power-Ups** → *Revoke* if you ever need to.

### 3. Save them locally

```bash
trello auth setup
```

You'll be prompted for `KEY` then `TOKEN`. They are saved to `~/.trello-cli/config.json` (chmod 600). Credentials never leave your machine.

### 4. Verify

```bash
trello auth whoami
```

Should print your Trello username. If you get `401 unauthorized`, the token is wrong or was revoked — regenerate and run `trello auth setup` again.

### Security notes

- **Never commit `~/.trello-cli/config.json`** — it holds a token that can act as you.
- Each teammate generates their own key + token. Do not share them.
- Revoke tokens you are not using at <https://trello.com/my/account>.

## Pick a board

```bash
trello board ls                  # list all your boards
trello board use "My Project"    # set default (by name or id)
trello board show                # show lists on current board
```

## Card ops

```bash
trello card ls                              # group cards by list
trello card ls --list "In Progress"
trello card show <id>

trello card create "fix login bug" --list "Todo" --desc "Stack trace attached."
trello card move <id> --to "Doing"
trello card comment <id> "claude moved this after commit abc123"
trello card update <id> --title "new title" --due 2026-05-01
trello card archive <id>
```

`<id>` accepts: full card ID, short ID, or a fuzzy title match on the current board.

## Letting Claude drive

Claude Code runs shell commands via its built-in Bash tool. Once `trello` is on the PATH, the only thing missing is **Claude knowing it exists** and **where to look up commands**.

The CLI is self-documenting: `trello agent-guide` prints an up-to-date markdown reference (generated from the click command tree). When you add new commands later, the guide updates automatically — no doc maintenance.

Add this block to `~/.claude/CLAUDE.md` (your global Claude instructions, applies to every session in every project):

```markdown
## Trello CLI

You have a `trello` CLI available. Use it to update the team's Trello board during coding sessions.

Before using it for the first time in a session, run:

    trello agent-guide

That prints a self-updating markdown reference of every command, its arguments, and safety rules. Always trust `trello agent-guide` over memory — new commands may have been added since your training.

For a specific command also try:

    trello <group> <command> --help

Typical flow: user finishes a ticket → `trello card ls` to find it → `trello card move <id> --to "Done"` → `trello card comment <id> "<short summary>"`.
```

Why this setup:
- **Single pointer**: Claude reads one block; all details live in the CLI itself.
- **Self-updating**: add a new subcommand in `trello_cli/commands/` and `trello agent-guide` reflects it — no CLAUDE.md edits.
- **Per-project override**: drop a `CLAUDE.md` in any repo to pin a specific board (`trello board use "<name>"`) or add rules.

## Share with teammates

Each teammate runs the same one-liner from **Install** above:

```bash
pipx install git+https://github.com/OferKoren/trello-cli-powerup.git
trello auth setup                 # each teammate uses their own key+token
trello board use "<shared board>" # point at the shared team board
```

Tokens are personal — never commit `~/.trello-cli/config.json` or share tokens.

Updates: push to `main` → teammates run `pipx upgrade trello-cli`.

## Dev

```bash
pip install -e ".[dev]"
pytest
```
