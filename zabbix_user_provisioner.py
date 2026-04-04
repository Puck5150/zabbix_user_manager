import argparse
import csv
import os
import sys

from modules.logger import setup_logger
from modules.utils import load_yaml_file
from modules.zabbix_api import ZabbixAPI
from modules.user_ops import build_user_payload


CONFIG_FILE = "config/zabbix_instances.yaml"


def parse_args():
    parser = argparse.ArgumentParser(description="Zabbix User Provisioner")

    parser.add_argument("--env", help="Environment (dev/stage/prod)")
    parser.add_argument("--all", action="store_true", help="Run on all instances")
    parser.add_argument("--dry-run", action="store_true", help="Do not create users")

    parser.add_argument("--username")
    parser.add_argument("--first-name")
    parser.add_argument("--last-name")
    parser.add_argument("--email")
    parser.add_argument("--ldap", action="store_true")

    parser.add_argument("--csv", help="CSV file for bulk provisioning")

    return parser.parse_args()


def load_instances(env=None):
    config = load_yaml_file(CONFIG_FILE)
    instances = []

    for env_name, env_data in config["environments"].items():
        if env and env != env_name:
            continue

        for inst in env_data["instances"]:
            instances.append(inst)

    return instances


def load_users_from_csv(path):
    users = []
    with open(path, newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            users.append(row)
    return users


def get_credentials():
    user = os.getenv("ZABBIX_API_USERNAME")
    pw = os.getenv("ZABBIX_API_PASSWORD")

    if not user or not pw:
        print("ERROR: Set ZABBIX_API_USERNAME and ZABBIX_API_PASSWORD")
        sys.exit(1)

    return user, pw


def process_instance(instance, users, args, logger, api_user, api_pass):
    logger.info(f"Processing instance: {instance['url']}")

    client = ZabbixAPI(
        url=instance["url"],
        username=api_user,
        password=api_pass,
        verify_ssl=instance.get("verify_ssl", True),
    )

    client.login()

    groups = client.get_user_groups()
    roles = client.get_roles()

    # Simple default selection (you can expand this later)
    default_group = groups[0]["usrgrpid"]
    default_role = roles[0]["roleid"]

    for user in users:
        payload = build_user_payload(
            username=user["username"],
            first_name=user["first_name"],
            last_name=user["last_name"],
            roleid=default_role,
            user_group_ids=[default_group],
            is_ldap_user=user.get("is_ldap", "true").lower() == "true",
        )

        if args.dry_run:
            logger.info(f"[DRY RUN] Would create user: {payload}")
            continue

        try:
            result = client.create_user(payload)
            logger.info(f"Created user {user['username']} | result={result}")
        except Exception as e:
            logger.error(f"Failed to create {user['username']}: {e}")

    client.logout()


def main():
    args = parse_args()
    logger = setup_logger()

    api_user, api_pass = get_credentials()

    instances = load_instances(args.env)

    if not instances:
        logger.error("No instances found")
        return 1

    # Determine users
    if args.csv:
        users = load_users_from_csv(args.csv)
    else:
        if not args.username:
            logger.error("Must provide --username or --csv")
            return 1

        users = [
            {
                "username": args.username,
                "first_name": args.first_name,
                "last_name": args.last_name,
                "email": args.email,
                "is_ldap": args.ldap,
            }
        ]

    for instance in instances:
        process_instance(instance, users, args, logger, api_user, api_pass)

    logger.info("Completed run.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
