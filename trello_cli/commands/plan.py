from __future__ import annotations

import json
from datetime import datetime, timezone

import click
from rich.console import Console
from rich.table import Table

from trello_cli.client import TrelloClient
from trello_cli.config import load_config, require_auth, require_board, require_power_up
from trello_cli.resolve import resolve_card

console = Console()

# Agent options matching superpowers skills
AGENT_OPTIONS = [
    "brainstorming", "writing-plans", "subagent-driven-development",
    "test-driven-development", "systematic-debugging", "receiving-code-review",
    "finishing-a-development-branch",
]

AGENT_STATUS_OPTIONS = ["idle", "planning", "planned", "working", "rejected", "approved", "merged"]
MODEL_OPTIONS = ["haiku", "sonnet", "opus", "dynamic"]

# --- Custom Field helpers ---

def _get_fields_map(client: TrelloClient, board_id: str) -> dict[str, dict]:
    """Return {field_name: field_object} for all custom fields on board."""
    fields = client.list_custom_fields(board_id)
    return {f["name"]: f for f in fields}

def _resolve_list_option_id(field: dict, value: str) -> str:
    """Given a list-type custom field and a text value, return the option id."""
    for opt in field.get("options", []):
        if opt.get("value", {}).get("text", "").lower() == value.lower():
            return opt["id"]
    valid = [opt.get("value", {}).get("text", "") for opt in field.get("options", [])]
    raise SystemExit(f"Invalid value '{value}' for field '{field['name']}'. Valid: {valid}")

def _set_field(client: TrelloClient, card_id: str, fields_map: dict, name: str, value, type_: str) -> None:
    """Set a custom field by name. Resolves option id for list type."""
    if name not in fields_map:
        console.print(f"[yellow]skip[/yellow] '{name}' (field not found — run `trello board init-agent-fields` first)")
        return
    field = fields_map[name]
    if type_ == "list":
        value = _resolve_list_option_id(field, value)
    client.set_custom_field_value(card_id, field["id"], value, type_)
    console.print(f"[green]set[/green] {name} = {value}")


def _register(card_group: click.Group) -> None:

    # ================================================================
    # card plan
    # ================================================================

    @card_group.group("plan", help="Show the agent Plan component stored by the Power-Up.")
    def plan_grp() -> None:
        pass

    @plan_grp.command("show", help="Print plan body and subtasks from the Power-Up's pluginData.")
    @click.argument("card_query")
    def plan_show_cmd(card_query: str) -> None:
        cfg = load_config()
        require_auth(cfg)
        board_id = require_board(cfg)
        require_power_up(cfg)
        client = TrelloClient(cfg)
        cards = client.board_cards(board_id)
        c = resolve_card(cards, card_query)

        entries = client.get_plugin_data(c["id"], cfg.power_up_id)
        plan_data = None
        for entry in entries:
            raw = entry.get("value")
            if not raw:
                continue
            try:
                obj = json.loads(raw)
            except (ValueError, TypeError):
                continue
            if isinstance(obj, dict):
                # Trello stores t.set('card','shared','plan',{...}) as {"plan": {...}}
                candidate = obj.get("plan")
                if isinstance(candidate, dict) and ("body" in candidate or "subtasks" in candidate):
                    plan_data = candidate
                    break

        if plan_data is None:
            console.print(f"[dim]No plan data found for '{c['name']}'. Add one via the Power-Up card-back UI.[/dim]")
            return

        console.print(f"[bold]{c['name']}[/bold] — Agent Plan")
        body = plan_data.get("body", "")
        if body:
            console.print("\n[bold]Plan body:[/bold]")
            console.print(body)

        subtasks = plan_data.get("subtasks", [])
        if subtasks:
            table = Table(title="Subtasks")
            table.add_column("#", width=3)
            table.add_column("done", width=5)
            table.add_column("text")
            table.add_column("model")
            table.add_column("agent")
            table.add_column("rejection")
            for i, st in enumerate(subtasks, 1):
                done = "[green]✓[/green]" if st.get("done") else " "
                table.add_row(
                    str(i), done,
                    st.get("text", ""),
                    st.get("model", ""),
                    st.get("agent", ""),
                    st.get("rejection_reason") or "",
                )
            console.print(table)

    # ================================================================
    # card state
    # ================================================================

    @card_group.group("state", help="Read or write agent state Custom Fields on a card.")
    def state_grp() -> None:
        pass

    @state_grp.command("get", help="Show agent state Custom Fields for a card.")
    @click.argument("card_query")
    def state_get_cmd(card_query: str) -> None:
        cfg = load_config()
        require_auth(cfg)
        board_id = require_board(cfg)
        client = TrelloClient(cfg)
        cards = client.board_cards(board_id)
        c = resolve_card(cards, card_query)

        fields_map = _get_fields_map(client, board_id)
        items = client.get_custom_field_items(c["id"])
        # Build id→field and id→options maps
        id_to_field = {f["id"]: f for f in fields_map.values()}
        item_map = {it["idCustomField"]: it for it in items}

        table = Table(title=f"Agent state — {c['name']}")
        table.add_column("field")
        table.add_column("value")
        agent_fields = ["agent_status", "branch", "worktree_path", "model_tag",
                        "agent_tag", "last_run_at", "spec_attached", "plan_attached"]
        for name in agent_fields:
            if name not in fields_map:
                continue
            field = fields_map[name]
            item = item_map.get(field["id"])
            if item is None:
                table.add_row(name, "[dim]—[/dim]")
                continue
            ftype = field.get("type", "text")
            if ftype == "list":
                # item has idValue; look up text
                opt_id = item.get("idValue", "")
                text = ""
                for opt in field.get("options", []):
                    if opt["id"] == opt_id:
                        text = opt.get("value", {}).get("text", "")
                        break
                table.add_row(name, text)
            elif ftype == "checkbox":
                val = item.get("value", {})
                table.add_row(name, "✓" if val.get("checked") == "true" else "☐")
            elif ftype == "date":
                val = item.get("value", {})
                table.add_row(name, val.get("date", ""))
            else:
                val = item.get("value", {})
                table.add_row(name, str(val.get("text", "")))
        console.print(table)

    @state_grp.command("set", help="Set one or more agent state Custom Fields on a card.")
    @click.argument("card_query")
    @click.option("--status", type=click.Choice(AGENT_STATUS_OPTIONS), default=None,
                  help="Agent lifecycle status.")
    @click.option("--branch", default=None, help="Git branch name.")
    @click.option("--worktree", default=None, help="Absolute path to git worktree.")
    @click.option("--model", type=click.Choice(MODEL_OPTIONS), default=None,
                  help="Model tag: haiku, sonnet, opus, dynamic.")
    @click.option("--agent", default=None, help="Superpowers agent skill name.")
    @click.option("--spec-attached/--no-spec-attached", default=None,
                  help="Mark spec.md as attached.")
    @click.option("--plan-attached/--no-plan-attached", default=None,
                  help="Mark plan.md as attached.")
    @click.option("--bump-last-run", is_flag=True, default=False,
                  help="Set last_run_at to now (UTC ISO-8601).")
    def state_set_cmd(
        card_query: str, status: str | None, branch: str | None, worktree: str | None,
        model: str | None, agent: str | None, spec_attached: bool | None,
        plan_attached: bool | None, bump_last_run: bool,
    ) -> None:
        any_set = any([
            status is not None, branch is not None, worktree is not None,
            model is not None, agent is not None,
            spec_attached is not None, plan_attached is not None,
            bump_last_run,
        ])
        if not any_set:
            raise SystemExit("Nothing to set. Pass at least one option.")

        cfg = load_config()
        require_auth(cfg)
        board_id = require_board(cfg)
        client = TrelloClient(cfg)
        cards = client.board_cards(board_id)
        c = resolve_card(cards, card_query)
        fields_map = _get_fields_map(client, board_id)

        if status is not None:
            _set_field(client, c["id"], fields_map, "agent_status", status, "list")
        if branch is not None:
            _set_field(client, c["id"], fields_map, "branch", branch, "text")
        if worktree is not None:
            _set_field(client, c["id"], fields_map, "worktree_path", worktree, "text")
        if model is not None:
            _set_field(client, c["id"], fields_map, "model_tag", model, "list")
        if agent is not None:
            _set_field(client, c["id"], fields_map, "agent_tag", agent, "text")
        if spec_attached is not None:
            _set_field(client, c["id"], fields_map, "spec_attached", spec_attached, "checkbox")
        if plan_attached is not None:
            _set_field(client, c["id"], fields_map, "plan_attached", plan_attached, "checkbox")
        if bump_last_run:
            now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
            _set_field(client, c["id"], fields_map, "last_run_at", now, "date")
