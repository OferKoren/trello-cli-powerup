"""Self-documenting command for AI agents.

Prints a markdown guide describing every command in the CLI. Built from click
introspection so it stays in sync automatically as commands are added or
changed.
"""
from __future__ import annotations

import click


SAFETY_RULES = """\
## Safety rules

- Never archive a card without explicit user confirmation.
- Never change the default board (`trello board use ...`) without asking.
- Confirm before bulk operations (moving/archiving multiple cards).
- If a card query is ambiguous the CLI exits with an error — re-run `trello card ls` and use the full id.
"""

USAGE_TIPS = """\
## When to use

- User mentions a ticket → `trello card ls` to find it, then `trello card show <id>` for detail.
- User starts work on a ticket → move to "Doing" (or equivalent), add short start comment.
- User finishes work → move to "Done" (or equivalent), add one-line result comment.
- New bug or task surfaces → `trello card create "<title>" --list "Backlog" --desc "<context>"`.
- Never spam comments — one per real milestone.

## Discovery

Run these when unsure:

- `trello board show` — current board + exact list names.
- `trello list ls` — list names on current board.
- `trello --help` and `trello <group> --help` — raw click help.
- `trello agent-guide` — this document.
"""


def _render_command(cmd: click.Command, path: list[str], lines: list[str]) -> None:
    full = "trello " + " ".join(path)
    if isinstance(cmd, click.Group):
        lines.append(f"### `{full}`")
        if cmd.help:
            lines.append("")
            lines.append(cmd.help.strip())
        lines.append("")
        for sub_name in sorted(cmd.commands):
            _render_command(cmd.commands[sub_name], path + [sub_name], lines)
        return

    lines.append(f"#### `{full}`")
    lines.append("")
    if cmd.help:
        lines.append(cmd.help.strip())
        lines.append("")

    args = []
    opts = []
    for p in cmd.params:
        if isinstance(p, click.Argument):
            args.append(p)
        elif isinstance(p, click.Option) and not p.hidden:
            opts.append(p)

    if args:
        lines.append("**Arguments:**")
        for a in args:
            req = "required" if a.required else "optional"
            lines.append(f"- `{a.name}` ({req})")
        lines.append("")

    if opts:
        lines.append("**Options:**")
        for o in opts:
            flag = " / ".join(o.opts + o.secondary_opts)
            req = " (required)" if o.required else ""
            help_text = f" — {o.help}" if o.help else ""
            lines.append(f"- `{flag}`{req}{help_text}")
        lines.append("")


@click.command("agent-guide", help="Print a markdown reference of every command — for AI agents.")
@click.pass_context
def agent_guide(ctx: click.Context) -> None:
    root = ctx.find_root().command
    lines: list[str] = []
    lines.append("# trello CLI — agent reference")
    lines.append("")
    lines.append(
        "Auto-generated from the CLI source. Whenever new commands are added "
        "they appear here automatically — always re-run `trello agent-guide` "
        "if you are unsure which commands exist."
    )
    lines.append("")
    lines.append(USAGE_TIPS)
    lines.append(SAFETY_RULES)
    lines.append("## Commands")
    lines.append("")
    assert isinstance(root, click.Group)
    for name in sorted(root.commands):
        _render_command(root.commands[name], [name], lines)
    click.echo("\n".join(lines))
