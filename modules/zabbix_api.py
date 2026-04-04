from __future__ import annotations

from typing import Any

import requests
import urllib3


class ZabbixAPIError(Exception):
    pass


class ZabbixAPI:
    def __init__(self, url: str, username: str, password: str, verify_ssl: bool = True):
        self.url = url
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl
        self.auth_token: str | None = None
        self._id = 1
        self.session = requests.Session()

        if not verify_ssl:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def _rpc(self, method: str, params: dict[str, Any], auth: str | None = None):
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": self._id,
        }
        self._id += 1

        if auth:
            payload["auth"] = auth

        response = self.session.post(
            self.url,
            json=payload,
            headers={"Content-Type": "application/json-rpc"},
            verify=self.verify_ssl,
            timeout=30,
        )

        response.raise_for_status()
        data = response.json()

        if "error" in data:
            raise ZabbixAPIError(data["error"])

        return data["result"]

    def login(self):
        self.auth_token = self._rpc(
            "user.login",
            {"username": self.username, "password": self.password},
        )

    def logout(self):
        if self.auth_token:
            try:
                self._rpc("user.logout", [], auth=self.auth_token)
            finally:
                self.auth_token = None

    def ensure_auth(self):
        if not self.auth_token:
            self.login()

    def api_version(self):
        return self._rpc("apiinfo.version", {})

    def get_user_groups(self):
        self.ensure_auth()
        return self._rpc(
            "usergroup.get",
            {"output": ["usrgrpid", "name"], "sortfield": "name"},
            auth=self.auth_token,
        )

    def get_roles(self):
        self.ensure_auth()
        return self._rpc(
            "role.get",
            {"output": ["roleid", "name"], "sortfield": "name"},
            auth=self.auth_token,
        )

    def get_users(self, username: str):
        self.ensure_auth()
        return self._rpc(
            "user.get",
            {"filter": {"username": [username]}},
            auth=self.auth_token,
        )

    def create_user(self, payload: dict[str, Any]):
        self.ensure_auth()
        return self._rpc("user.create", payload, auth=self.auth_token)