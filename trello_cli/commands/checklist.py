from __future__ import annotations

import click
from rich.console import Console
from rich.table import Table

from trello_cli.client import TrelloClient
from trello_cli.config import load_config, require_auth, require_board
from trello_cli.resolve import resolve_card, resolve_one

console = Console()


def _ctx():
    cfg = load_config()
    require_auth(cfg)
    board_id = require_board(cfg)
    return cfg, board_id, TrelloClient(cfg)


def _resolve_card_and_checklists(client: TrelloClient, board_id: str, card_query: str):
    cards = client.board_cards(board_id)
    c = resolve_card(cards, card_query)
    checklists = client.card_checklists(c["id"])
    return c, checklists


def _resolve_check_item(checklist: dict, query: str) -> dict:
    items = checklist.get("checkItems", [])
    for it in items:
        if it["id"] == query:
            return it
    q = query.strip().lower()
    exact = [it for it in items if it["name"].lower() == q]
    if len(exact) == 1:
        return exact[0]
    if len(exact) > 1:
        raise SystemExit(f"Ambiguous item '{query}' in checklist.")
    subs = [it for it in items if q in it["name"].lower()]
    if len(subs) == 1:
        return subs[0]
    if len(subs) > 1:
        raise SystemExit(
            f"Ambiguous item '{query}': {[it['name'] for it in subs]}"
        )
    raise SystemExit(f"No checklist item matching '{query}'.")


def _register(card_group: click.Group) -> None:
    @card_group.group("checklist", help="Manage checklists on a card.")
    def checklist_grp() -> None:
        pass

    @checklist_grp.command("ls", help="Show checklists and items on a card.")
    @click.argument("card_query")
    def ls_cmd(card_query: str) -> None:
        _, board_id, client = _ctx()
        c, checklists = _resolve_card_and_checklists(client, board_id, card_query)
        console.print(f"[bold]{c['name']}[/bold] — {len(checklists)} checklist(s)")
        for cl in checklists:
            items = cl.get("checkItems", [])
            done = sum(1 for it in items if it["state"] == "complete")
            table = Table(title=f"{cl['name']} ({done}/{len(items)})  [dim]{cl['id']}[/dim]")
            table.add_column("✓", width=3)
            table.add_column("name")
            table.add_column("id", style="dim")
            for it in sorted(items, key=lambda x: x.get("pos", 0)):
                mark = "[green]x[/green]" if it["state"] == "complete" else " "
                table.add_row(mark, it["name"], it["id"])
            console.print(table)

    @checklist_grp.command("create", help="Create a new checklist on a card.")
    @click.argument("card_query")
    @click.argument("name")
    def create_cmd(card_query: str, name: str) -> None:
        _, board_id, client = _ctx()
        cards = client.board_cards(board_id)
        c = resolve_card(cards, card_query)
        cl = client.create_checklist(c["id"], name)
        console.print(f"[green]created checklist[/green] '{cl['name']}' on '{c['name']}' ({cl['id']})")

    @checklist_grp.command("rename", help="Rename a checklist on a card.")
    @click.argument("card_query")
    @click.argument("checklist_query")
    @click.argument("new_name")
    def rename_cmd(card_query: str, checklist_query: str, new_name: str) -> None:
        _, board_id, client = _ctx()
        _, checklists = _resolve_card_and_checklists(client, board_id, card_query)
        cl = resolve_one(checklists, checklist_query)
        client.rename_checklist(cl["id"], new_name)
        console.print(f"[green]renamed[/green] '{cl['name']}' -> '{new_name}'")

    @checklist_grp.command("delete", help="Delete a checklist from a card.")
    @click.argument("card_query")
    @click.argument("checklist_query")
    def delete_cmd(card_query: str, checklist_query: str) -> None:
        _, board_id, client = _ctx()
        _, checklists = _resolve_card_and_checklists(client, board_id, card_query)
        cl = resolve_one(checklists, checklist_query)
        client.delete_checklist(cl["id"])
        console.print(f"[green]deleted checklist[/green] '{cl['name']}'")

    # --- item subgroup ---

    @checklist_grp.group("item", help="Manage items within a checklist.")
    def item_grp() -> None:
        pass

    @item_grp.command("add", help="Add an item to a checklist.")
    @click.argument("card_query")
    @click.argument("checklist_query")
    @click.argument("text")
    @click.option("--checked", is_flag=True, help="Create already marked complete.")
    def item_add_cmd(card_query: str, checklist_query: str, text: str, checked: bool) -> None:
        _, board_id, client = _ctx()
        _, checklists = _resolve_card_and_checklists(client, board_id, card_query)
        cl = resolve_one(checklists, checklist_query)
        it = client.add_check_item(cl["id"], text, checked=checked)
        mark = "[x]" if checked else "[ ]"
        console.print(f"[green]added[/green] {mark} '{it['name']}' to '{cl['name']}'")

    @item_grp.command("check", help="Mark a checklist item complete.")
    @click.argument("card_query")
    @click.argument("checklist_query")
    @click.argument("item_query")
    def item_check_cmd(card_query: str, checklist_query: str, item_query: str) -> None:
        _, board_id, client = _ctx()
        c, checklists = _resolve_card_and_checklists(client, board_id, card_query)
        cl = resolve_one(checklists, checklist_query)
        it = _resolve_check_item(cl, item_query)
        client.update_check_item(c["id"], it["id"], state="complete")
        console.print(f"[green]checked[/green] '{it['name']}'")

    @item_grp.command("uncheck", help="Mark a checklist item incomplete.")
    @click.argument("card_query")
    @click.argument("checklist_query")
    @click.argument("item_query")
    def item_uncheck_cmd(card_query: str, checklist_query: str, item_query: str) -> None:
        _, board_id, client = _ctx()
        c, checklists = _resolve_card_and_checklists(client, board_id, card_query)
        cl = resolve_one(checklists, checklist_query)
        it = _resolve_check_item(cl, item_query)
        client.update_check_item(c["id"], it["id"], state="incomplete")
        console.print(f"[green]unchecked[/green] '{it['name']}'")

    @item_grp.command("rename", help="Rename a checklist item.")
    @click.argument("card_query")
    @click.argument("checklist_query")
    @click.argument("item_query")
    @click.argument("new_name")
    def item_rename_cmd(
        card_query: str, checklist_query: str, item_query: str, new_name: str
    ) -> None:
        _, board_id, client = _ctx()
        c, checklists = _resolve_card_and_checklists(client, board_id, card_query)
        cl = resolve_one(checklists, checklist_query)
        it = _resolve_check_item(cl, item_query)
        client.update_check_item(c["id"], it["id"], name=new_name)
        console.print(f"[green]renamed[/green] '{it['name']}' -> '{new_name}'")

    @item_grp.command("delete", help="Delete a checklist item.")
    @click.argument("card_query")
    @click.argument("checklist_query")
    @click.argument("item_query")
    def item_delete_cmd(card_query: str, checklist_query: str, item_query: str) -> None:
        _, board_id, client = _ctx()
        _, checklists = _resolve_card_and_checklists(client, board_id, card_query)
        cl = resolve_one(checklists, checklist_query)
        it = _resolve_check_item(cl, item_query)
        client.delete_check_item(cl["id"], it["id"])
        console.print(f"[green]deleted item[/green] '{it['name']}'")
