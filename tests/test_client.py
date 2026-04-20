import requests_mock

from trello_cli.client import BASE_URL, TrelloClient
from trello_cli.config import Config


def _client() -> TrelloClient:
    return TrelloClient(Config(key="KEY", token="TOKEN"))


def test_whoami_injects_auth():
    with requests_mock.Mocker() as m:
        m.get(f"{BASE_URL}/members/me", json={"id": "u1", "username": "alice", "fullName": "Alice"})
        me = _client().whoami()
    assert me["username"] == "alice"
    qs = m.last_request.qs
    assert qs["key"] == ["key"]
    assert qs["token"] == ["token"]


def test_create_card_posts_params():
    with requests_mock.Mocker() as m:
        m.post(f"{BASE_URL}/cards", json={"id": "c1", "idShort": 7, "name": "hi"})
        out = _client().create_card("L1", "hi", "desc")
    assert out["id"] == "c1"
    qs = m.last_request.qs
    assert qs["idlist"] == ["l1"]
    assert qs["name"] == ["hi"]
    assert qs["desc"] == ["desc"]


def test_move_card_puts_idlist():
    with requests_mock.Mocker() as m:
        m.put(f"{BASE_URL}/cards/c1", json={"id": "c1"})
        _client().move_card("c1", "L2")
    assert m.last_request.qs["idlist"] == ["l2"]


def test_comment_card():
    with requests_mock.Mocker() as m:
        m.post(f"{BASE_URL}/cards/c1/actions/comments", json={"id": "a1"})
        _client().comment_card("c1", "hello")
    assert m.last_request.qs["text"] == ["hello"]


def test_error_raises():
    import pytest

    from trello_cli.client import TrelloError

    with requests_mock.Mocker() as m:
        m.get(f"{BASE_URL}/members/me", status_code=401, text="unauthorized")
        with pytest.raises(TrelloError):
            _client().whoami()
