from __future__ import annotations

import click
from rich.console import Console

from trello_cli.client import TrelloClient, TrelloError
from trello_cli.config import Config, load_config, require_auth, save_config

console = Console()


@click.group(help="Authenticate with Trello.")
def auth() -> None:
    pass


@auth.command("setup", help="Prompt for API key + token and save them.")
@click.option("--key", default=None, help="Trello API key (prompted if omitted).")
@click.option("--token", default=None, help="Trello API token (prompted if omitted).")
def setup_cmd(key: str | None, token: str | None) -> None:
    cfg = load_config()
    key = key or click.prompt("Trello API key (from https://trello.com/app-key)", default=cfg.key or None)
    token = token or click.prompt("Trello API token", hide_input=True, default=cfg.token or None)
    cfg.key = key.strip()
    cfg.token = token.strip()
    save_config(cfg)
    try:
        me = TrelloClient(cfg).whoami()
    except TrelloError as e:
        raise SystemExit(f"Saved, but auth test failed: {e}")
    console.print(f"[green]OK[/green] authenticated as [bold]{me.get('username')}[/bold] ({me.get('fullName')}).")


@auth.command("whoami", help="Show current authenticated user.")
def whoami_cmd() -> None:
    cfg = load_config()
    require_auth(cfg)
    me = TrelloClient(cfg).whoami()
    console.print(f"username: {me.get('username')}")
    console.print(f"name:     {me.get('fullName')}")
    console.print(f"id:       {me.get('id')}")
