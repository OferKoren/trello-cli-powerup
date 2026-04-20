import pytest

from trello_cli.resolve import resolve_card, resolve_one


def test_resolve_one_by_id():
    items = [{"id": "abc", "name": "Foo"}, {"id": "def", "name": "Bar"}]
    assert resolve_one(items, "abc")["name"] == "Foo"


def test_resolve_one_exact_name_case_insensitive():
    items = [{"id": "abc", "name": "Foo"}, {"id": "def", "name": "Bar"}]
    assert resolve_one(items, "foo")["id"] == "abc"


def test_resolve_one_substring():
    items = [{"id": "abc", "name": "In Progress"}, {"id": "def", "name": "Done"}]
    assert resolve_one(items, "prog")["id"] == "abc"


def test_resolve_one_ambiguous():
    items = [{"id": "1", "name": "Doing now"}, {"id": "2", "name": "Doing later"}]
    with pytest.raises(SystemExit):
        resolve_one(items, "doing")  # substring of both, no exact match


def test_resolve_one_missing():
    with pytest.raises(SystemExit):
        resolve_one([{"id": "1", "name": "x"}], "nope")


def test_resolve_card_by_short_id():
    cards = [
        {"id": "aaa", "idShort": 12, "name": "One"},
        {"id": "bbb", "idShort": 34, "name": "Two"},
    ]
    assert resolve_card(cards, "34")["id"] == "bbb"


def test_resolve_card_by_name():
    cards = [
        {"id": "aaa", "idShort": 1, "name": "fix login"},
        {"id": "bbb", "idShort": 2, "name": "add logout"},
    ]
    assert resolve_card(cards, "login")["id"] == "aaa"
