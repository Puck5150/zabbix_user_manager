from __future__ import annotations

from typing import Any


def build_usergroup_refs(group_ids: list[str]):
    return [{"usrgrpid": gid} for gid in group_ids]


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
        "usrgrps": build_usergroup_refs(user_group_ids),
    }

    # Only include password for local users
    if not is_ldap_user and password:
        payload["passwd"] = password

    return payload


def user_exists(existing_users: list[dict[str, Any]]) -> bool:
    return len(existing_users) > 0