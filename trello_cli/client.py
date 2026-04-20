from __future__ import annotations

from typing import Any

import requests

from trello_cli.config import Config

BASE_URL = "https://api.trello.com/1"


class TrelloError(RuntimeError):
    pass


class TrelloClient:
    def __init__(self, cfg: Config, timeout: int = 15):
        self.key = cfg.key
        self.token = cfg.token
        self.timeout = timeout
        self.session = requests.Session()

    def _auth_params(self) -> dict[str, str]:
        return {"key": self.key, "token": self.token}

    def _request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        files: dict[str, Any] | None = None,
    ) -> Any:
        url = f"{BASE_URL}{path}"
        merged = {**self._auth_params(), **(params or {})}
        resp = self.session.request(
            method, url, params=merged, files=files, timeout=self.timeout
        )
        if resp.status_code >= 400:
            raise TrelloError(f"{method} {path} -> {resp.status_code}: {resp.text}")
        if not resp.content:
            return None
        try:
            return resp.json()
        except ValueError:
            return resp.text

    def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        return self._request("GET", path, params)

    def post(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        files: dict[str, Any] | None = None,
    ) -> Any:
        return self._request("POST", path, params, files=files)

    def put(self, path: str, params: dict[str, Any] | None = None) -> Any:
        return self._request("PUT", path, params)

    def delete(self, path: str, params: dict[str, Any] | None = None) -> Any:
        return self._request("DELETE", path, params)

    # --- high-level helpers ---

    def whoami(self) -> dict[str, Any]:
        return self.get("/members/me", {"fields": "id,username,fullName,email"})

    def boards(self) -> list[dict[str, Any]]:
        return self.get("/members/me/boards", {"fields": "id,name,url,closed", "filter": "open"})

    def board(self, board_id: str) -> dict[str, Any]:
        return self.get(f"/boards/{board_id}", {"fields": "id,name,url"})

    def board_lists(self, board_id: str) -> list[dict[str, Any]]:
        return self.get(f"/boards/{board_id}/lists", {"fields": "id,name,closed"})

    def board_cards(self, board_id: str) -> list[dict[str, Any]]:
        return self.get(
            f"/boards/{board_id}/cards",
            {"fields": "id,idShort,name,idList,due,labels,url,closed"},
        )

    def card(self, card_id: str) -> dict[str, Any]:
        return self.get(f"/cards/{card_id}")

    def create_card(self, id_list: str, name: str, desc: str = "") -> dict[str, Any]:
        return self.post("/cards", {"idList": id_list, "name": name, "desc": desc})

    def update_card(self, card_id: str, **fields: Any) -> dict[str, Any]:
        return self.put(f"/cards/{card_id}", fields)

    def move_card(self, card_id: str, id_list: str) -> dict[str, Any]:
        return self.update_card(card_id, idList=id_list)

    def archive_card(self, card_id: str) -> dict[str, Any]:
        return self.update_card(card_id, closed="true")

    def comment_card(self, card_id: str, text: str) -> dict[str, Any]:
        return self.post(f"/cards/{card_id}/actions/comments", {"text": text})

    # --- attachments ---

    def attach_url(
        self, card_id: str, url: str, name: str | None = None
    ) -> dict[str, Any]:
        params: dict[str, Any] = {"url": url}
        if name:
            params["name"] = name
        return self.post(f"/cards/{card_id}/attachments", params)

    def attach_file(
        self, card_id: str, file_path: str, name: str | None = None
    ) -> dict[str, Any]:
        params: dict[str, Any] = {}
        if name:
            params["name"] = name
        with open(file_path, "rb") as fh:
            return self.post(
                f"/cards/{card_id}/attachments",
                params,
                files={"file": (name or _basename(file_path), fh)},
            )

    # --- labels ---

    def board_labels(self, board_id: str) -> list[dict[str, Any]]:
        return self.get(
            f"/boards/{board_id}/labels",
            {"fields": "id,name,color", "limit": 1000},
        )

    def create_label(
        self, board_id: str, name: str, color: str | None = None
    ) -> dict[str, Any]:
        return self.post(
            "/labels", {"idBoard": board_id, "name": name, "color": color or ""}
        )

    def add_label_to_card(self, card_id: str, label_id: str) -> Any:
        return self.post(f"/cards/{card_id}/idLabels", {"value": label_id})

    def remove_label_from_card(self, card_id: str, label_id: str) -> Any:
        return self.delete(f"/cards/{card_id}/idLabels/{label_id}")

    # --- members ---

    def board_members(self, board_id: str) -> list[dict[str, Any]]:
        return self.get(
            f"/boards/{board_id}/members",
            {"fields": "id,username,fullName"},
        )

    def add_member_to_card(self, card_id: str, member_id: str) -> Any:
        return self.post(f"/cards/{card_id}/idMembers", {"value": member_id})

    def remove_member_from_card(self, card_id: str, member_id: str) -> Any:
        return self.delete(f"/cards/{card_id}/idMembers/{member_id}")

    # --- checklists ---

    def card_checklists(self, card_id: str) -> list[dict[str, Any]]:
        return self.get(
            f"/cards/{card_id}/checklists",
            {"fields": "id,name,idCard", "checkItems": "all",
             "checkItem_fields": "name,state,pos"},
        )

    def create_checklist(self, card_id: str, name: str) -> dict[str, Any]:
        return self.post("/checklists", {"idCard": card_id, "name": name})

    def rename_checklist(self, checklist_id: str, name: str) -> dict[str, Any]:
        return self.put(f"/checklists/{checklist_id}", {"name": name})

    def delete_checklist(self, checklist_id: str) -> Any:
        return self.delete(f"/checklists/{checklist_id}")

    def add_check_item(
        self, checklist_id: str, name: str, checked: bool = False
    ) -> dict[str, Any]:
        return self.post(
            f"/checklists/{checklist_id}/checkItems",
            {"name": name, "checked": "true" if checked else "false"},
        )

    def update_check_item(
        self,
        card_id: str,
        item_id: str,
        state: str | None = None,
        name: str | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {}
        if state is not None:
            params["state"] = state
        if name is not None:
            params["name"] = name
        return self.put(f"/cards/{card_id}/checkItem/{item_id}", params)

    def delete_check_item(self, checklist_id: str, item_id: str) -> Any:
        return self.delete(f"/checklists/{checklist_id}/checkItems/{item_id}")


def _basename(path: str) -> str:
    import os

    return os.path.basename(path)
