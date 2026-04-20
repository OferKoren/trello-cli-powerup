from __future__ import annotations

import click
from rich.console import Console
from rich.table import Table

from trello_cli.client import TrelloClient
from trello_cli.config import load_config, require_auth, require_board

console = Console()


@click.group(help="Lists on the current board.")
def list_cmd() -> None:
    pass


@list_cmd.command("ls", help="Show all lists on the current board.")
def ls_cmd() -> None:
    cfg = load_config()
    require_auth(cfg)
    board_id = require_board(cfg)
    lists = TrelloClient(cfg).board_lists(board_id)
    table = Table(title="Lists")
    table.add_column("id", style="dim")
    table.add_column("name")
    for lst in lists:
        table.add_row(lst["id"], lst["name"])
    console.print(table)
