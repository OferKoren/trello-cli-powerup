from __future__ import annotations

import requests_mock as req_mock
from trello_cli.client import TrelloClient
from trello_cli.config import Config

BASE = "https://api.trello.com/1"


def _client():
    return TrelloClient(Config(key="KEY", token="TOKEN"))


def test_list_custom_fields():
    """GET /boards/{id}/customFields."""
    with req_mock.Mocker() as m:
        m.get(f"{BASE}/boards/b1/customFields", json=[
            {"id": "f1", "name": "agent_status", "type": "list"},
        ])
        result = _client().list_custom_fields("b1")
    assert len(result) == 1
    assert result[0]["name"] == "agent_status"


def test_list_custom_fields_empty():
    """Returns empty list when API returns None."""
    with req_mock.Mocker() as m:
        m.get(f"{BASE}/boards/b1/customFields", json=None)
        result = _client().list_custom_fields("b1")
    assert result == []


def test_create_custom_field_text():
    """POST /customFields with JSON body for text type."""
    with req_mock.Mocker() as m:
        m.post(f"{BASE}/customFields", json={"id": "f2", "name": "branch", "type": "text"})
        result = _client().create_custom_field("b1", "branch", "text")
    assert m.last_request.json()["name"] == "branch"
    assert m.last_request.json()["type"] == "text"
    assert m.last_request.json()["idModel"] == "b1"


def test_create_custom_field_list_type_sends_options():
    """POST /customFields with options array in JSON body for list type."""
    with req_mock.Mocker() as m:
        m.post(f"{BASE}/customFields", json={"id": "f3", "name": "agent_status", "type": "list"})
        _client().create_custom_field("b1", "agent_status", "list",
                                      options=["idle", "working", "done"])
    body = m.last_request.json()
    assert body["type"] == "list"
    options = body["options"]
    assert len(options) == 3
    assert options[0]["value"]["text"] == "idle"
    assert options[1]["value"]["text"] == "working"
    assert options[2]["value"]["text"] == "done"


def test_get_custom_field_items():
    """GET /cards/{id}/customFieldItems."""
    with req_mock.Mocker() as m:
        m.get(f"{BASE}/cards/c1/customFieldItems", json=[
            {"idCustomField": "f1", "idValue": "opt1"},
        ])
        result = _client().get_custom_field_items("c1")
    assert len(result) == 1
    assert result[0]["idCustomField"] == "f1"


def test_set_custom_field_value_text():
    """PUT body is {"value": {"text": "..."}} for text type."""
    with req_mock.Mocker() as m:
        m.put(f"{BASE}/cards/c1/customField/f1/item", json={})
        _client().set_custom_field_value("c1", "f1", "feat/foo", "text")
    assert m.last_request.json() == {"value": {"text": "feat/foo"}}


def test_set_custom_field_value_checkbox_true():
    """PUT body is {"value": {"checked": "true"}} for checkbox=True."""
    with req_mock.Mocker() as m:
        m.put(f"{BASE}/cards/c1/customField/f1/item", json={})
        _client().set_custom_field_value("c1", "f1", True, "checkbox")
    assert m.last_request.json() == {"value": {"checked": "true"}}


def test_set_custom_field_value_checkbox_false():
    """PUT body is {"value": {"checked": "false"}} for checkbox=False."""
    with req_mock.Mocker() as m:
        m.put(f"{BASE}/cards/c1/customField/f1/item", json={})
        _client().set_custom_field_value("c1", "f1", False, "checkbox")
    assert m.last_request.json() == {"value": {"checked": "false"}}


def test_set_custom_field_value_list_uses_id_value():
    """PUT body is {"idValue": "opt123"} for list type."""
    with req_mock.Mocker() as m:
        m.put(f"{BASE}/cards/c1/customField/f1/item", json={})
        _client().set_custom_field_value("c1", "f1", "opt123", "list")
    assert m.last_request.json() == {"idValue": "opt123"}


def test_set_custom_field_value_date():
    """PUT body is {"value": {"date": "..."}} for date type."""
    with req_mock.Mocker() as m:
        m.put(f"{BASE}/cards/c1/customField/f1/item", json={})
        _client().set_custom_field_value("c1", "f1", "2025-01-01T00:00:00.000Z", "date")
    assert m.last_request.json() == {"value": {"date": "2025-01-01T00:00:00.000Z"}}
