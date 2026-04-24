from __future__ import annotations

import json

import requests_mock as req_mock
from click.testing import CliRunner
from trello_cli.commands.board import init_agent_fields_cmd

BASE = "https://api.trello.com/1"
BOARD_ID = "board123"


def _setup_config(tmp_path, monkeypatch):
    """Write a minimal config and patch CONFIG_PATH."""
    cfg_path = tmp_path / "config.json"
    cfg_path.write_text(json.dumps({
        "key": "KEY", "token": "TOKEN", "default_board_id": BOARD_ID
    }))
    monkeypatch.setattr("trello_cli.config.CONFIG_PATH", cfg_path)
    monkeypatch.setattr("trello_cli.config.CONFIG_DIR", tmp_path)


def test_init_agent_fields_creates_missing(tmp_path, monkeypatch):
    """Creates fields and lists that are missing."""
    _setup_config(tmp_path, monkeypatch)
    runner = CliRunner()
    with req_mock.Mocker() as m:
        m.get(f"{BASE}/boards/{BOARD_ID}/customFields", json=[])
        m.get(f"{BASE}/boards/{BOARD_ID}/lists", json=[])
        m.post(f"{BASE}/customFields", json={"id": "fx", "name": "x"})
        m.post(f"{BASE}/lists", json={"id": "lx", "name": "x"})
        result = runner.invoke(init_agent_fields_cmd, [])
    assert result.exit_code == 0
    post_cf = [r for r in m.request_history if r.method == "POST" and "/customFields" in r.url]
    post_lists = [r for r in m.request_history if r.method == "POST" and "/lists" in r.url]
    assert len(post_cf) == 8
    assert len(post_lists) == 8


def test_init_agent_fields_skips_existing(tmp_path, monkeypatch):
    """Skips fields/lists that already exist by name."""
    _setup_config(tmp_path, monkeypatch)
    runner = CliRunner()
    existing_fields = [
        {"id": "f1", "name": "agent_status", "type": "list"},
        {"id": "f2", "name": "branch", "type": "text"},
    ]
    existing_lists = [
        {"id": "l1", "name": "human-planned"},
    ]
    with req_mock.Mocker() as m:
        m.get(f"{BASE}/boards/{BOARD_ID}/customFields", json=existing_fields)
        m.get(f"{BASE}/boards/{BOARD_ID}/lists", json=existing_lists)
        m.post(f"{BASE}/customFields", json={"id": "fx", "name": "x"})
        m.post(f"{BASE}/lists", json={"id": "lx", "name": "x"})
        result = runner.invoke(init_agent_fields_cmd, [])
    assert result.exit_code == 0
    post_cf = [r for r in m.request_history if r.method == "POST" and "/customFields" in r.url]
    post_lists = [r for r in m.request_history if r.method == "POST" and "/lists" in r.url]
    # 2 fields exist → 6 created; 1 list exists → 7 created
    assert len(post_cf) == 6
    assert len(post_lists) == 7


def test_init_agent_fields_dry_run(tmp_path, monkeypatch):
    """Dry run makes no POST calls."""
    _setup_config(tmp_path, monkeypatch)
    runner = CliRunner()
    with req_mock.Mocker() as m:
        m.get(f"{BASE}/boards/{BOARD_ID}/customFields", json=[])
        m.get(f"{BASE}/boards/{BOARD_ID}/lists", json=[])
        result = runner.invoke(init_agent_fields_cmd, ["--dry-run"])
    assert result.exit_code == 0
    posts = [r for r in m.request_history if r.method == "POST"]
    assert len(posts) == 0
