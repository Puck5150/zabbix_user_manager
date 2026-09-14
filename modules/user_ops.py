from __future__ import annotations

from typing import Any


def build_user_payload(
    username: str,
    first_name: str,
    last_name: str,
    roleid: str,
    user_group_ids: list[str],
    is_ldap_user: bool = True,
    password: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "username": username,
        "name": first_name,
        "surname": last_name,
        "roleid": roleid,
        "usrgrps": [{"usrgrpid": gid} for gid in user_group_ids],
    }

    # Only include password for local users
    if not is_ldap_user and password:
        payload["passwd"] = password

    return payload