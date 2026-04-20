from __future__ import annotations

import click

from trello_cli.commands.agent_guide import agent_guide
from trello_cli.commands.auth import auth
from trello_cli.commands.board import board
from trello_cli.commands.card import card
from trello_cli.commands.list_cmd import list_cmd


@click.group(help="Trello CLI — drive your board from the terminal (and from Claude Code).")
@click.version_option(package_name="trello-cli")
def main() -> None:
    pass


main.add_command(auth)
main.add_command(board)
main.add_command(list_cmd, name="list")
main.add_command(card)
main.add_command(agent_guide)


if __name__ == "__main__":
    main()
