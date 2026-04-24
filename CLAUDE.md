# trello-cli — Claude Instructions

This project ships a `trello` CLI that you (Claude) use to update the team's Trello board during sessions. Prefer running these commands over asking the user to update cards manually.

## First: learn the CLI

Before using any command for the first time in a session, run:

```bash
trello agent-guide
```

This prints an up-to-date markdown reference of every command, its arguments, safety rules, and usage tips. **It is generated from the source code, so it reflects the current CLI even if new commands have been added.** Always trust `trello agent-guide` over any list you may remember from a prior session.

If you need finer detail on a specific command:

```bash
trello <group> <command> --help
```

## Board context

- `trello board show` — name of current default board and its exact list names. Run this once per session before moving cards so you use the right list names.
- If no default board is set, ask the user which board to use rather than guessing.

## Feature Map

| Area            | Files |
|-----------------|-------|
| CLI entry       | `trello_cli/cli.py`, `trello_cli/__main__.py` |
| Config / auth   | `trello_cli/config.py`, `trello_cli/commands/auth.py` |
| Trello API      | `trello_cli/client.py` |
| Resolvers       | `trello_cli/resolve.py` |
| Board commands  | `trello_cli/commands/board.py` |
| List commands   | `trello_cli/commands/list_cmd.py` |
| Card commands   | `trello_cli/commands/card.py` |
| Agent guide     | `trello_cli/commands/agent_guide.py` |
| Plan commands   | `trello_cli/commands/plan.py` |
| Tests           | `tests/test_client.py`, `tests/test_resolve.py`, `tests/test_plugin_data.py`, `tests/test_custom_fields.py`, `tests/test_init_agent_fields.py` |
| Packaging       | `pyproject.toml` |
| Power-Up JS     | `powerup/client.js`, `powerup/plan.js`, `powerup/policies.js`, `powerup/settings.js`, `powerup/version.js` |
| Power-Up HTML   | `powerup/index.html`, `powerup/plan.html`, `powerup/policies.html`, `powerup/settings.html` |

## Adding new commands

When adding a new subcommand:
1. Put it in `trello_cli/commands/` and register it in `trello_cli/cli.py`.
2. Give the click command a clear `help=` string — it becomes the agent-facing docs automatically.
3. No need to edit this file or `agent-guide` output — `trello agent-guide` picks it up via click introspection.
