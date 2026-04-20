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
