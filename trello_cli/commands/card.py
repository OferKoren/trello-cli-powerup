from __future__ import annotations

from collections import defaultdict

import click
from rich.console import Console
from rich.table import Table

from trello_cli.client import TrelloClient
from trello_cli.config import load_config, require_auth, require_board
from trello_cli.resolve import resolve_card, resolve_one

console = Console()


def _load_board_context():
    cfg = load_config()
    require_auth(cfg)
    board_id = require_board(cfg)
    return cfg, board_id, TrelloClient(cfg)


@click.group(help="Cards: ls, show, create, move, comment, update, archive.")
def card() -> None:
    pass


@card.command("ls", help="List cards on the current board, grouped by list.")
@click.option("--list", "list_name", default=None, help="Filter to a single list (name or id).")
def ls_cmd(list_name: str | None) -> None:
    _, board_id, client = _load_board_context()
    lists = client.board_lists(board_id)
    cards = client.board_cards(board_id)
    lists_by_id = {lst["id"]: lst for lst in lists}

    if list_name:
        lst = resolve_one(lists, list_name)
        lists = [lst]
        cards = [c for c in cards if c["idList"] == lst["id"]]

    grouped: dict[str, list[dict]] = defaultdict(list)
    for c in cards:
        grouped[c["idList"]].append(c)

    for lst in lists:
        bucket = grouped.get(lst["id"], [])
        table = Table(title=f"{lst['name']} ({len(bucket)})")
        table.add_column("#", style="dim", width=5)
        table.add_column("id", style="dim")
        table.add_column("name")
        for c in bucket:
            table.add_row(str(c.get("idShort", "")), c["id"], c["name"])
        console.print(table)


@card.command("show", help="Show full card details.")
@click.argument("card_query")
def show_cmd(card_query: str) -> None:
    _, board_id, client = _load_board_context()
    cards = client.board_cards(board_id)
    c = resolve_card(cards, card_query)
    full = client.card(c["id"])
    console.print(f"[bold]{full['name']}[/bold]  [dim]#{full.get('idShort')} {full['id']}[/dim]")
    console.print(f"url: {full.get('url', '')}")
    if full.get("due"):
        console.print(f"due: {full['due']}")
    labels = [l["name"] or l["color"] for l in full.get("labels", [])]
    if labels:
        console.print(f"labels: {', '.join(labels)}")
    if full.get("desc"):
        console.print("\n[bold]description[/bold]")
        console.print(full["desc"])


@card.command("create", help="Create a card in a list on the current board.")
@click.argument("title")
@click.option("--list", "list_name", required=True, help="Target list (name or id).")
@click.option("--desc", default="", help="Card description (markdown supported).")
def create_cmd(title: str, list_name: str, desc: str) -> None:
    _, board_id, client = _load_board_context()
    lists = client.board_lists(board_id)
    lst = resolve_one(lists, list_name)
    created = client.create_card(lst["id"], title, desc)
    console.print(
        f"[green]created[/green] #{created.get('idShort')} "
        f"{created['name']} -> {lst['name']}"
    )
    console.print(f"id: {created['id']}")
    if created.get("url"):
        console.print(f"url: {created['url']}")


@card.command("move", help="Move a card to another list.")
@click.argument("card_query")
@click.option("--to", "to_list", required=True, help="Destination list (name or id).")
def move_cmd(card_query: str, to_list: str) -> None:
    _, board_id, client = _load_board_context()
    cards = client.board_cards(board_id)
    c = resolve_card(cards, card_query)
    lists = client.board_lists(board_id)
    dst = resolve_one(lists, to_list)
    client.move_card(c["id"], dst["id"])
    console.print(f"[green]moved[/green] '{c['name']}' -> {dst['name']}")


@card.command("comment", help="Add a comment to a card.")
@click.argument("card_query")
@click.argument("text")
def comment_cmd(card_query: str, text: str) -> None:
    _, board_id, client = _load_board_context()
    cards = client.board_cards(board_id)
    c = resolve_card(cards, card_query)
    client.comment_card(c["id"], text)
    console.print(f"[green]commented[/green] on '{c['name']}'")


@card.command("update", help="Update card fields.")
@click.argument("card_query")
@click.option("--title", default=None)
@click.option("--desc", default=None)
@click.option("--due", default=None, help="ISO 8601 datetime or empty string to clear.")
def update_cmd(card_query: str, title: str | None, desc: str | None, due: str | None) -> None:
    _, board_id, client = _load_board_context()
    cards = client.board_cards(board_id)
    c = resolve_card(cards, card_query)
    fields: dict[str, str] = {}
    if title is not None:
        fields["name"] = title
    if desc is not None:
        fields["desc"] = desc
    if due is not None:
        fields["due"] = due
    if not fields:
        raise SystemExit("Nothing to update. Pass --title, --desc, or --due.")
    client.update_card(c["id"], **fields)
    console.print(f"[green]updated[/green] '{c['name']}' ({', '.join(fields)})")


@card.command("archive", help="Archive (close) a card.")
@click.argument("card_query")
def archive_cmd(card_query: str) -> None:
    _, board_id, client = _load_board_context()
    cards = client.board_cards(board_id)
    c = resolve_card(cards, card_query)
    client.archive_card(c["id"])
    console.print(f"[green]archived[/green] '{c['name']}'")


@card.command("attach", help="Attach a file or URL to a card.")
@click.argument("card_query")
@click.option(
    "--file",
    "file_path",
    type=click.Path(exists=True, dir_okay=False),
    default=None,
    help="Path to a local file to upload.",
)
@click.option("--url", "url", default=None, help="External URL to attach.")
@click.option("--name", default=None, help="Display name for the attachment.")
def attach_cmd(
    card_query: str, file_path: str | None, url: str | None, name: str | None
) -> None:
    if bool(file_path) == bool(url):
        raise SystemExit("Pass exactly one of --file or --url.")
    _, board_id, client = _load_board_context()
    cards = client.board_cards(board_id)
    c = resolve_card(cards, card_query)
    if file_path:
        att = client.attach_file(c["id"], file_path, name)
        console.print(
            f"[green]attached file[/green] '{att.get('name')}' to '{c['name']}'"
        )
    else:
        att = client.attach_url(c["id"], url, name)  # type: ignore[arg-type]
        console.print(
            f"[green]attached url[/green] '{att.get('name') or url}' to '{c['name']}'"
        )
    if att.get("url"):
        console.print(f"url: {att['url']}")


# --- labels ---


@card.group("label", help="Manage labels on a card.")
def label_group() -> None:
    pass


@label_group.command("ls", help="List all labels defined on the current board.")
def label_ls_cmd() -> None:
    _, board_id, client = _load_board_context()
    labels = client.board_labels(board_id)
    table = Table(title="Board labels")
    table.add_column("id", style="dim")
    table.add_column("name")
    table.add_column("color")
    for lbl in labels:
        table.add_row(lbl["id"], lbl.get("name") or "", lbl.get("color") or "")
    console.print(table)


def _resolve_label(labels: list[dict], query: str) -> dict:
    for lbl in labels:
        if lbl["id"] == query:
            return lbl
    q = query.strip().lower()
    exact = [l for l in labels if (l.get("name") or "").lower() == q]
    if len(exact) == 1:
        return exact[0]
    if len(exact) > 1:
        raise SystemExit(
            f"Ambiguous label name '{query}': use label id from `trello card label ls`."
        )
    colors = [l for l in labels if (l.get("color") or "") == q and not l.get("name")]
    if len(colors) == 1:
        return colors[0]
    subs = [l for l in labels if q in (l.get("name") or "").lower()]
    if len(subs) == 1:
        return subs[0]
    if len(subs) > 1:
        raise SystemExit(
            f"Ambiguous label '{query}': {[l.get('name') for l in subs]}"
        )
    raise SystemExit(f"No label matching '{query}'. Run `trello card label ls`.")


@label_group.command(
    "add", help="Add a label to a card. Use --create to create the label if missing."
)
@click.argument("card_query")
@click.argument("label_query")
@click.option(
    "--create", is_flag=True, help="Create the label on the board if it does not exist."
)
@click.option(
    "--color",
    default=None,
    help="Color when creating: green, yellow, orange, red, purple, blue, sky, lime, pink, black.",
)
def label_add_cmd(
    card_query: str, label_query: str, create: bool, color: str | None
) -> None:
    _, board_id, client = _load_board_context()
    cards = client.board_cards(board_id)
    c = resolve_card(cards, card_query)
    labels = client.board_labels(board_id)
    try:
        lbl = _resolve_label(labels, label_query)
    except SystemExit:
        if not create:
            raise
        lbl = client.create_label(board_id, label_query, color)
        console.print(
            f"[green]created label[/green] '{lbl.get('name')}' ({lbl.get('color') or 'no color'})"
        )
    client.add_label_to_card(c["id"], lbl["id"])
    console.print(
        f"[green]labeled[/green] '{c['name']}' with '{lbl.get('name') or lbl.get('color')}'"
    )


@label_group.command("remove", help="Remove a label from a card.")
@click.argument("card_query")
@click.argument("label_query")
def label_remove_cmd(card_query: str, label_query: str) -> None:
    _, board_id, client = _load_board_context()
    cards = client.board_cards(board_id)
    c = resolve_card(cards, card_query)
    labels = client.board_labels(board_id)
    lbl = _resolve_label(labels, label_query)
    client.remove_label_from_card(c["id"], lbl["id"])
    console.print(
        f"[green]removed label[/green] '{lbl.get('name') or lbl.get('color')}' from '{c['name']}'"
    )


# --- members ---


def _resolve_member(members: list[dict], query: str) -> dict:
    for m in members:
        if m["id"] == query:
            return m
    q = query.strip().lower().lstrip("@")
    for m in members:
        if (m.get("username") or "").lower() == q:
            return m
    exact = [m for m in members if (m.get("fullName") or "").lower() == q]
    if len(exact) == 1:
        return exact[0]
    if len(exact) > 1:
        raise SystemExit(
            f"Ambiguous member '{query}': use username or id from `trello card member ls`."
        )
    subs = [
        m
        for m in members
        if q in (m.get("username") or "").lower()
        or q in (m.get("fullName") or "").lower()
    ]
    if len(subs) == 1:
        return subs[0]
    if len(subs) > 1:
        raise SystemExit(
            f"Ambiguous member '{query}': {[m.get('username') for m in subs]}"
        )
    raise SystemExit(f"No member matching '{query}'. Run `trello card member ls`.")


@card.group("member", help="Assign or unassign members on a card.")
def member_group() -> None:
    pass


@member_group.command("ls", help="List members of the current board.")
def member_ls_cmd() -> None:
    _, board_id, client = _load_board_context()
    members = client.board_members(board_id)
    table = Table(title="Board members")
    table.add_column("id", style="dim")
    table.add_column("username")
    table.add_column("name")
    for m in members:
        table.add_row(m["id"], m.get("username") or "", m.get("fullName") or "")
    console.print(table)


@member_group.command("add", help="Assign a member to a card (by username, full name, or id).")
@click.argument("card_query")
@click.argument("member_query")
def member_add_cmd(card_query: str, member_query: str) -> None:
    _, board_id, client = _load_board_context()
    cards = client.board_cards(board_id)
    c = resolve_card(cards, card_query)
    members = client.board_members(board_id)
    m = _resolve_member(members, member_query)
    client.add_member_to_card(c["id"], m["id"])
    console.print(
        f"[green]assigned[/green] @{m.get('username')} to '{c['name']}'"
    )


@member_group.command("remove", help="Unassign a member from a card.")
@click.argument("card_query")
@click.argument("member_query")
def member_remove_cmd(card_query: str, member_query: str) -> None:
    _, board_id, client = _load_board_context()
    cards = client.board_cards(board_id)
    c = resolve_card(cards, card_query)
    members = client.board_members(board_id)
    m = _resolve_member(members, member_query)
    client.remove_member_from_card(c["id"], m["id"])
    console.print(
        f"[green]unassigned[/green] @{m.get('username')} from '{c['name']}'"
    )


# --- agent powerup ---

@card.command("attach-spec", help="Attach spec.md to a card and mark spec_attached=true.")
@click.argument("card_query")
@click.argument("path", type=click.Path(exists=True, dir_okay=False))
def attach_spec_cmd(card_query: str, path: str) -> None:
    cfg = load_config()
    require_auth(cfg)
    board_id = require_board(cfg)
    client = TrelloClient(cfg)
    cards = client.board_cards(board_id)
    c = resolve_card(cards, card_query)
    att = client.attach_file(c["id"], path, "spec.md")
    console.print(f"[green]attached spec.md[/green] to '{c['name']}' (attachment id: {att.get('id', '?')})")
    # flip Custom Field
    fields = client.list_custom_fields(board_id)
    fields_map = {f["name"]: f for f in fields}
    if "spec_attached" in fields_map:
        field = fields_map["spec_attached"]
        client.set_custom_field_value(c["id"], field["id"], True, "checkbox")
        console.print("[green]set[/green] spec_attached = true")


@card.command("attach-plan", help="Attach plan.md to a card and mark plan_attached=true.")
@click.argument("card_query")
@click.argument("path", type=click.Path(exists=True, dir_okay=False))
def attach_plan_cmd(card_query: str, path: str) -> None:
    cfg = load_config()
    require_auth(cfg)
    board_id = require_board(cfg)
    client = TrelloClient(cfg)
    cards = client.board_cards(board_id)
    c = resolve_card(cards, card_query)
    att = client.attach_file(c["id"], path, "plan.md")
    console.print(f"[green]attached plan.md[/green] to '{c['name']}' (attachment id: {att.get('id', '?')})")
    # flip Custom Field
    fields = client.list_custom_fields(board_id)
    fields_map = {f["name"]: f for f in fields}
    if "plan_attached" in fields_map:
        field = fields_map["plan_attached"]
        client.set_custom_field_value(c["id"], field["id"], True, "checkbox")
        console.print("[green]set[/green] plan_attached = true")
