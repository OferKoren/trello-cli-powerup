from __future__ import annotations

import requests_mock as req_mock
from trello_cli.client import TrelloClient
from trello_cli.config import Config

BASE = "https://api.trello.com/1"


def _client():
    return TrelloClient(Config(key="KEY", token="TOKEN"))


def test_get_plugin_data_no_filter():
    """Returns all pluginData entries when no id_plugin given."""
    with req_mock.Mocker() as m:
        m.get(f"{BASE}/cards/c1/pluginData", json=[
            {"idPlugin": "P1", "value": '{"plan": {}}'},
            {"idPlugin": "P2", "value": '{}'},
        ])
        result = _client().get_plugin_data("c1")
    assert len(result) == 2


def test_get_plugin_data_filter_by_plugin():
    """Filters entries by idPlugin when id_plugin is provided."""
    with req_mock.Mocker() as m:
        m.get(f"{BASE}/cards/c1/pluginData", json=[
            {"idPlugin": "P1", "value": '{"plan": {}}'},
            {"idPlugin": "P2", "value": '{}'},
        ])
        result = _client().get_plugin_data("c1", id_plugin="P1")
    assert len(result) == 1
    assert result[0]["idPlugin"] == "P1"


def test_get_plugin_data_empty_response():
    """Returns empty list when API returns null/empty."""
    with req_mock.Mocker() as m:
        m.get(f"{BASE}/cards/c1/pluginData", json=None)
        result = _client().get_plugin_data("c1")
    assert result == []
