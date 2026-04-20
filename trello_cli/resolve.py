"""Fuzzy/short-id resolution for boards, lists, cards."""
from __future__ import annotations

from typing import Any


def _norm(s: str) -> str:
    return s.strip().lower()


def resolve_one(items: list[dict[str, Any]], query: str, field: str = "name") -> dict[str, Any]:
    """Find one item by id or case-insensitive name match (exact, then substring)."""
    q = _norm(query)
    for it in items:
        if it.get("id") == query:
            return it
    exact = [it for it in items if _norm(it.get(field, "")) == q]
    if len(exact) == 1:
        return exact[0]
    if len(exact) > 1:
        raise SystemExit(f"Ambiguous {field} '{query}': {[it[field] for it in exact]}")
    subs = [it for it in items if q in _norm(it.get(field, ""))]
    if len(subs) == 1:
        return subs[0]
    if len(subs) > 1:
        raise SystemExit(f"Ambiguous {field} '{query}': {[it[field] for it in subs]}")
    raise SystemExit(f"No {field} matching '{query}'.")


def resolve_card(cards: list[dict[str, Any]], query: str) -> dict[str, Any]:
    """Accept full id, short id (numeric), or fuzzy name."""
    for c in cards:
        if c.get("id") == query:
            return c
    if query.isdigit():
        short = int(query)
        for c in cards:
            if c.get("idShort") == short:
                return c
    return resolve_one(cards, query, field="name")
