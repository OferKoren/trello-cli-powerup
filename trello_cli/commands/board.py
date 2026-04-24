from __future__ import annotations

import click
from rich.console import Console
from rich.table import Table

from trello_cli.client import TrelloClient
from trello_cli.config import load_config, require_auth, require_board, save_config
from trello_cli.resolve import resolve_one

console = Console()


@click.group(help="Boards: list, pick the active one.")
def board() -> None:
    pass


@board.command("ls", help="List your open boards.")
def ls_cmd() -> None:
    cfg = load_config()
    require_auth(cfg)
    boards = TrelloClient(cfg).boards()
    table = Table(title="Boards")
    table.add_column("id", style="dim")
    table.add_column("name")
    table.add_column("url", style="cyan")
    for b in boards:
        marker = " *" if b["id"] == cfg.default_board_id else ""
        table.add_row(b["id"], b["name"] + marker, b.get("url", ""))
    console.print(table)
    if cfg.default_board_id:
        console.print("[dim]* = current default[/dim]")


@board.command("use", help="Set the default board (by id or name).")
@click.argument("board_query")
def use_cmd(board_query: str) -> None:
    cfg = load_config()
    require_auth(cfg)
    boards = TrelloClient(cfg).boards()
    b = resolve_one(boards, board_query)
    cfg.default_board_id = b["id"]
    save_config(cfg)
    console.print(f"[green]default board set:[/green] {b['name']} ({b['id']})")


@board.command("show", help="Show current default board and its lists.")
def show_cmd() -> None:
    cfg = load_config()
    require_auth(cfg)
    board_id = require_board(cfg)
    client = TrelloClient(cfg)
    b = client.board(board_id)
    lists = client.board_lists(board_id)
    console.print(f"[bold]{b['name']}[/bold]  [dim]{b['id']}[/dim]")
    console.print(f"url: {b.get('url', '')}")
    table = Table(title="Lists")
    table.add_column("id", style="dim")
    table.add_column("name")
    for lst in lists:
        table.add_row(lst["id"], lst["name"])
    console.print(table)


# --- agent powerup ---

AGENT_FIELDS = [
    {"name": "agent_status", "type": "list",
     "options": ["idle", "planning", "planned", "working", "rejected", "approved", "merged"]},
    {"name": "branch",       "type": "text"},
    {"name": "worktree_path","type": "text"},
    {"name": "model_tag",    "type": "list",
     "options": ["haiku", "sonnet", "opus", "dynamic"]},
    {"name": "agent_tag",    "type": "text"},
    {"name": "last_run_at",  "type": "date"},
    {"name": "spec_attached","type": "checkbox"},
    {"name": "plan_attached","type": "checkbox"},
]

AGENT_LISTS = [
    "human-planned", "agentic-planning", "agentic-planned",
    "agentic-implementing", "manual-testing", "rejected", "approved", "merged",
]


@board.command("init-agent-fields",
               help="Idempotently create the 8 agent Custom Fields and 8 workflow lists on the current board. Requires the built-in Custom Fields Power-Up enabled on the board.")
@click.option("--dry-run", is_flag=True, help="Print what would be created without doing it.")
@click.option("--lists/--no-lists", "create_lists", default=True,
              help="Also scaffold the 8 agentic workflow columns (default: on).")
def init_agent_fields_cmd(dry_run: bool, create_lists: bool) -> None:
    cfg = load_config()
    require_auth(cfg)
    board_id = require_board(cfg)
    client = TrelloClient(cfg)

    # --- Custom Fields ---
    existing_fields = client.list_custom_fields(board_id)
    existing_names = {f["name"] for f in existing_fields}

    console.print("[bold]Custom Fields:[/bold]")
    for spec in AGENT_FIELDS:
        name = spec["name"]
        if name in existing_names:
            console.print(f"  [dim]skip[/dim]  {name} (already exists)")
            continue
        if dry_run:
            console.print(f"  [yellow]would create[/yellow]  {name} ({spec['type']})")
        else:
            client.create_custom_field(
                board_id, name, spec["type"],
                options=spec.get("options"),
            )
            console.print(f"  [green]created[/green]  {name} ({spec['type']})")

    # --- Lists ---
    if create_lists:
        existing_lists = client.board_lists(board_id)
        existing_list_names = {lst["name"] for lst in existing_lists}
        console.print("[bold]Workflow lists:[/bold]")
        for pos, list_name in enumerate(AGENT_LISTS, start=1):
            if list_name in existing_list_names:
                console.print(f"  [dim]skip[/dim]  {list_name} (already exists)")
                continue
            if dry_run:
                console.print(f"  [yellow]would create[/yellow]  {list_name}")
            else:
                client.create_list(board_id, list_name, pos * 100)
                console.print(f"  [green]created[/green]  {list_name}")
