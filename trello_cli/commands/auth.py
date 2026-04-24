from __future__ import annotations

import click
from rich.console import Console
from rich.table import Table

from trello_cli.client import TrelloClient, TrelloError
from trello_cli.config import (
    Config,
    get_active_profile_name,
    list_profiles,
    load_config,
    require_auth,
    save_config,
    save_profile,
    switch_profile,
)

console = Console()


@click.group(help="Authenticate with Trello.")
def auth() -> None:
    pass


@auth.command("setup", help="Prompt for API key + token and save them.")
@click.option("--key", default=None, help="Trello API key (prompted if omitted).")
@click.option("--token", default=None, help="Trello API token (prompted if omitted).")
@click.option("--power-up-id", "power_up_id", default=None,
              help="Trello Power-Up (plugin) id — from https://trello.com/power-ups/admin.")
@click.option("--profile", "profile_name", default=None,
              help="Profile name to create or update (default: current active profile).")
def setup_cmd(key: str | None, token: str | None, power_up_id: str | None, profile_name: str | None) -> None:
    active = get_active_profile_name()
    target = profile_name or active

    # Load existing profile if it exists, else empty Config
    _, profiles = list_profiles()
    cfg = profiles.get(target, Config())

    key = key or click.prompt("Trello API key (from https://trello.com/app-key)", default=cfg.key or None)
    token = token or click.prompt("Trello API token", hide_input=True, default=cfg.token or None)
    cfg.key = key.strip()
    cfg.token = token.strip()
    if power_up_id is not None:
        cfg.power_up_id = power_up_id.strip()

    save_profile(target, cfg)

    # If this is a new profile (not active), ask whether to switch
    if target != active:
        if click.confirm(f"Profile '{target}' saved. Switch to it now?", default=True):
            switch_profile(target)
            console.print(f"[green]Switched[/green] to profile '[bold]{target}[/bold]'.")

    try:
        me = TrelloClient(cfg).whoami()
    except TrelloError as e:
        raise SystemExit(f"Saved, but auth test failed: {e}")
    console.print(f"[green]OK[/green] profile '[bold]{target}[/bold]' authenticated as [bold]{me.get('username')}[/bold] ({me.get('fullName')}).")


@auth.command("switch", help="Switch active profile.")
@click.argument("profile_name")
def switch_cmd(profile_name: str) -> None:
    cfg = switch_profile(profile_name)
    try:
        me = TrelloClient(cfg).whoami()
        console.print(f"[green]Switched[/green] to '[bold]{profile_name}[/bold]' — {me.get('username')} ({me.get('fullName')}).")
    except TrelloError:
        console.print(f"[green]Switched[/green] to '[bold]{profile_name}[/bold]' (auth test skipped — no credentials).")


@auth.command("ls", help="List saved profiles.")
def ls_cmd() -> None:
    active, profiles = list_profiles()
    if not profiles:
        console.print("No profiles saved. Run `trello auth setup` to create one.")
        return
    table = Table(show_header=True, header_style="bold")
    table.add_column("Profile")
    table.add_column("Trello user")
    table.add_column("Default board")
    table.add_column("Power-Up ID")
    for name, cfg in profiles.items():
        marker = "[green]●[/green] " if name == active else "  "
        try:
            username = TrelloClient(cfg).whoami().get("username", "—") if cfg.authed else "—"
        except TrelloError:
            username = "[red]auth error[/red]"
        table.add_row(
            f"{marker}[bold]{name}[/bold]" if name == active else f"{marker}{name}",
            username,
            cfg.default_board_id or "—",
            cfg.power_up_id or "—",
        )
    console.print(table)


@auth.command("whoami", help="Show current authenticated user.")
def whoami_cmd() -> None:
    cfg = load_config()
    require_auth(cfg)
    me = TrelloClient(cfg).whoami()
    console.print(f"profile:  {get_active_profile_name()}")
    console.print(f"username: {me.get('username')}")
    console.print(f"name:     {me.get('fullName')}")
    console.print(f"id:       {me.get('id')}")
